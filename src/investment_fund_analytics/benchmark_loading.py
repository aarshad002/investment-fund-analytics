"""Load official issuer-reported index levels locally, retaining unresolved alignment."""
from datetime import datetime
from decimal import Decimal
import hashlib
import json
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
import psycopg
from psycopg.types.json import Jsonb

from investment_fund_analytics.database_loading import connection_settings,reference,ObservationConflict,DEFAULT_MANIFEST

BENCHMARKS={
 'LU0380865021':dict(code='SX5T:EUR:NTR:DWS',name='EURO STOXX 50 EUR Net Return',identifier='SX5T / EU0009658152',
                   basis='net_total_return',url='https://stoxx.com/index/sx5t/',
                   notes='Official index identifiers; DWS supplies issuer-reported historical levels.'),
 'LU0290355717':dict(code='IBOXX_EUR_SOVEREIGNS_EUROZONE_TR:DWS',name='iBoxx Euro Sovereigns Eurozone Total Return',
                   identifier=None,basis='total_return',
                   url='https://etf.dws.com/en/LU0290355717-eurozone-government-bond-ucits-etf-1c/',
                   notes='No authoritative public vendor code/ISIN verified; project code is internal, not a fabricated vendor identifier.'),
}


def extract(root,acquisition):
    path=(root/acquisition['raw_file']).resolve()
    if not path.is_relative_to((root/'data/raw').resolve()) or hashlib.sha256(path.read_bytes()).hexdigest()!=acquisition['file_sha256']:
        raise ValueError('Raw index source identity mismatch')
    book=load_workbook(path,read_only=True,data_only=True)
    try:
        sheet=book[acquisition['isin']]
        rows=list(sheet.values)
        header=next(i for i,r in enumerate(rows) if 'Date' in r and 'Index Level' in r)
        date_col=rows[header].index('Date');value_col=rows[header].index('Index Level')
        records=[];missing=[]
        for row_number,row in enumerate(rows[header+1:],start=header+2):
            if all(value is None for value in row):continue
            day=datetime.strptime(row[date_col],'%d.%m.%Y').date()
            value=row[value_col]
            if value in (None,'N/A',''):
                missing.append(day);continue
            value=Decimal(str(value))
            if not value.is_finite() or value<=0:raise ValueError('Invalid index level')
            records.append(dict(observation_date=day,value=value,raw_row_number=row_number))
        records.sort(key=lambda r:r['observation_date'])
        if len({r['observation_date'] for r in records})!=len(records):raise ValueError('Duplicate index dates')
        return records,missing
    finally:book.close()


def load(root):
    manifest=json.loads((root/DEFAULT_MANIFEST).read_text())
    prepared=[(a,*extract(root,a)) for a in manifest]
    with psycopg.connect(**connection_settings(root/'.env.owner'),autocommit=True) as owner:
        owner.execute((root/'sql/benchmark_schema.sql').read_text())
    results=[]
    with psycopg.connect(**connection_settings(root/'.env.app'),autocommit=True) as conn,conn.transaction():
        conn.execute("SELECT pg_advisory_xact_lock(hashtextextended('ifa:benchmark-load',0))")
        for a,records,missing in prepared:
            meta=BENCHMARKS[a['isin']]
            instrument=reference(conn,'instrument','instrument_id','instrument_code',dict(
                instrument_code=meta['code'],instrument_name=meta['name'],instrument_type='index',
                value_basis='total_return_index',currency='EUR',adjustment_status='total_return',
                adjustment_notes='Issuer-reported benchmark index levels; effective date alignment unverified.'))
            benchmark=reference(conn,'benchmark','benchmark_id','benchmark_code',dict(
                benchmark_code=meta['code'],instrument_id=instrument,benchmark_name=meta['name'],
                provider_identifier=meta['identifier'],identifier_notes=meta['notes'],benchmark_kind='official_index',
                return_basis=meta['basis'],metadata_url=meta['url'],date_alignment_status='unverified',
                limitations='DWS public export, not independent index-administrator acquisition. Four missing levels; annual endpoint discrepancy; no date shifting or forward filling; benchmark-relative risk blocked. Redistribution restricted.'))
            fund=conn.execute('SELECT instrument_id FROM core.instrument WHERE instrument_code=%s',(a['isin']+':NAV:EUR:NATIVE',)).fetchone()[0]
            assignment=reference(conn,'benchmark_assignment','benchmark_assignment_id',('fund_instrument_id','effective_start_date'),dict(
                fund_instrument_id=fund,benchmark_id=benchmark,effective_start_date=datetime(2021,9,30).date(),
                effective_end_date=datetime(2026,9,30).date(),
                rationale='Project comparison window for issuer-designated benchmark; alignment unverified; not a claim of prospectus history.'))
            source=conn.execute('SELECT source_id FROM core.source WHERE source_code=%s',(a['source_code'],)).fetchone()[0]
            existing={r[0]:r[1] for r in conn.execute('SELECT observation_date,value FROM core.observation WHERE instrument_id=%s',(instrument,))}
            for r in records:
                if r['observation_date'] in existing and r['value']!=existing[r['observation_date']]:
                    raise ObservationConflict('Conflicting benchmark observations; all changes rolled back')
            additions=[r for r in records if r['observation_date'] not in existing]
            run=conn.execute('''INSERT INTO core.ingestion_run(source_id,instrument_id,retrieved_at,request_url,
             request_parameters,requested_start_date,requested_end_date,observed_start_date,observed_end_date,
             raw_file_path,file_sha256,file_bytes,rows_read,rows_accepted,rows_rejected,rows_inserted,pipeline_version)
             VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'benchmark-loader-v1') RETURNING ingestion_run_id''',
             (source,instrument,a['retrieved_at'],a['request_url'],Jsonb(dict(column='Index Level',date_semantics='unverified')),
              a['requested_start'],a['requested_end'],records[0]['observation_date'],records[-1]['observation_date'],
              a['raw_file'],a['file_sha256'],a['file_bytes'],len(records)+len(missing),len(records),len(missing),len(additions))).fetchone()[0]
            with conn.cursor() as cur:
                cur.executemany('''INSERT INTO core.observation(instrument_id,observation_date,value,ingestion_run_id,raw_row_number,quality_status)
                    VALUES(%s,%s,%s,%s,%s,'flagged')''',[(instrument,r['observation_date'],r['value'],run,r['raw_row_number']) for r in additions])
            for day in missing:
                conn.execute('''INSERT INTO core.quality_issue(ingestion_run_id,instrument_id,observation_date,check_code,severity,details)
                 VALUES(%s,%s,%s,'missing_benchmark_level','warning','Issuer export index level unavailable; no filling')''',(run,instrument,day))
            conn.execute('''INSERT INTO core.quality_issue(ingestion_run_id,instrument_id,check_code,severity,details)
             VALUES(%s,%s,'benchmark_date_alignment','warning','Annual endpoint discrepancy; effective index date unverified; all benchmark observations flagged')''',(run,instrument))
            conn.execute("UPDATE core.ingestion_run SET status='succeeded',completed_at=clock_timestamp() WHERE ingestion_run_id=%s",(run,))
            results.append(dict(isin=a['isin'],benchmark_id=benchmark,instrument_id=instrument,assignment_id=assignment,
                source_id=source,run_id=run,rows=len(records),inserted=len(additions),missing=[str(d) for d in missing],
                start=str(records[0]['observation_date']),end=str(records[-1]['observation_date']),alignment_status='unverified'))
    output=root/'data/processed/benchmarks';output.mkdir(parents=True,exist_ok=True)
    (output/'load_validation.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))
    return results


if __name__=='__main__':load(Path.cwd())

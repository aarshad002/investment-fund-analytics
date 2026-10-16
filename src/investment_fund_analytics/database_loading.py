"""Local, append-only PostgreSQL loading with conflict checks and acquisition lineage."""
from __future__ import annotations
from investment_fund_analytics.calendar_validation import read_register

import argparse
import csv
from datetime import date
import hashlib
import json
from pathlib import Path

from dotenv import dotenv_values
import psycopg
from psycopg import sql
from psycopg.types.json import Jsonb

from investment_fund_analytics.sample_ingestion import INSTRUMENTS, parse_workbook

VERSION = 'phase3-loader-v1'
DEFAULT_MANIFEST = 'data/raw/full_history/20261007T105130116510Z/manifest.json'


class ObservationConflict(ValueError):
    """Existing values or statuses differ: reject the whole batch, never overwrite."""


def connection_settings(path):
    config = dotenv_values(path)
    required = ('DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD')
    if any(not config.get(key) or '<' in config[key] for key in required):
        raise ValueError(f'Provide real local connection settings in {path.name}; do not print credentials')
    if config['DB_HOST'] not in {'localhost', '127.0.0.1', '::1'}:
        raise ValueError('This loader is restricted to local PostgreSQL')
    return dict(host=config['DB_HOST'], port=int(config['DB_PORT']), dbname=config['DB_NAME'],
                user=config['DB_USER'], password=config['DB_PASSWORD'],
                sslmode=config.get('DB_SSLMODE', 'prefer'), connect_timeout=5)


def prepare_batches(root, manifest_path):
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if len(manifest) != 2 or {a['isin'] for a in manifest} != set(INSTRUMENTS):
        raise ValueError('Manifest must identify exactly the approved pair')
    batches = []
    for acquisition in manifest:
        isin = acquisition['isin']
        if acquisition['source_code'] != INSTRUMENTS[isin].source_code:
            raise ValueError('Source identity mismatch')
        raw = (root / acquisition['raw_file']).resolve()
        if not raw.is_relative_to((root / 'data/raw').resolve()):
            raise ValueError('Raw path escapes data/raw')
        content = raw.read_bytes()
        if hashlib.sha256(content).hexdigest() != acquisition['file_sha256'] or len(content) != acquisition['file_bytes']:
            raise ValueError('Raw identity/checksum mismatch')
        result = parse_workbook(raw, INSTRUMENTS[isin])
        frame = result.records
        if frame.empty or (frame.quality_status == 'invalid').any():
            raise ValueError(f'{isin}: rejected records require resolution before loading')
        if frame.observation_date.duplicated().any() or not frame.observation_date.is_monotonic_increasing:
            raise ValueError(f'{isin}: dates must be unique and sorted')
        if not frame.observation_date.between(acquisition['requested_start'], acquisition['requested_end']).all():
            raise ValueError('Observation lies outside manifest range')
        batches.append((acquisition, frame, result.issues))
    calendar = read_register(root)
    from investment_fund_analytics.calendar_validation import QUALITY_SUMMARY
    summary = json.loads((root / QUALITY_SUMMARY).read_text(encoding='utf-8'))
    if set(summary) != {acquisition['isin'] for acquisition, _, _ in batches}:
        raise ValueError('Calendar quality evidence fund scope differs from selected acquisition')
    import pandas as pd
    for acquisition, frame, _ in batches:
        details = summary[acquisition['isin']]
        if details.get('acquisition', {}).get('file_sha256') != acquisition['file_sha256']:
            raise ValueError('Calendar quality evidence does not identify selected raw acquisition')
        observed = set(frame.observation_date.dt.strftime('%Y-%m-%d'))
        weekdays = set(pd.bdate_range(frame.observation_date.min(), frame.observation_date.max()).strftime('%Y-%m-%d'))
        if set(details['missing_weekdays']) != weekdays - observed:
            raise ValueError('Calendar quality omissions disagree with parsed NAV dates')
    return batches, calendar


def reference(conn, table, id_column, key, fields):
    """Insert once; refuse to silently change existing reference metadata."""
    names = list(fields)
    keys = (key,) if isinstance(key,str) else tuple(key)
    conn.execute(sql.SQL('INSERT INTO core.{} ({}) VALUES ({}) ON CONFLICT ({}) DO NOTHING RETURNING {}').format(
        sql.Identifier(table), sql.SQL(',').join(map(sql.Identifier, names)),
        sql.SQL(',').join(sql.Placeholder() for _ in names), sql.SQL(',').join(map(sql.Identifier,keys)), sql.Identifier(id_column)),
        list(fields.values())).fetchone()
    existing = conn.execute(sql.SQL('SELECT {}, {} FROM core.{} WHERE {}').format(
        sql.Identifier(id_column), sql.SQL(',').join(map(sql.Identifier, names)),
        sql.Identifier(table), sql.SQL(' AND ').join(sql.SQL('{} = %s').format(sql.Identifier(k)) for k in keys)),
        tuple(fields[k] for k in keys)).fetchone()
    if existing is None or tuple(existing[1:]) != tuple(fields.values()):
        raise ValueError(f'Existing {table} metadata differs; explicit review required')
    return existing[0]


def seed(conn, acquisition):
    isin = acquisition['isin']
    metadata = INSTRUMENTS[isin]
    equity = isin == 'LU0380865021'
    slug = 'euro-stoxx-50' if equity else 'eurozone-government-bond'
    fund_id = reference(conn, 'fund_share_class', 'fund_share_class_id', 'isin', dict(
        isin=isin, fund_name=metadata.fund_name, share_class_name='1C', issuer_name='DWS / Xtrackers',
        legal_umbrella='Xtrackers' if equity else 'Xtrackers II', domicile_country_code='LU',
        asset_class='equity' if equity else 'bond',
        category='Eurozone large-cap equity' if equity else 'Eurozone investment-grade sovereign bonds',
        income_policy='accumulating', share_class_currency='EUR', hedging_policy='unhedged',
        ucits_status=True, benchmark_name='EURO STOXX 50 net total return EUR' if equity else 'iBoxx Euro Sovereigns Eurozone Index',
        metadata_source_url=f'https://etf.dws.com/en/{isin}-{slug}-ucits-etf-1c/',
        metadata_as_of_date=date(2026, 10, 7)))
    instrument_id = reference(conn, 'instrument', 'instrument_id', 'instrument_code', dict(
        instrument_code=metadata.instrument_code, fund_share_class_id=fund_id,
        instrument_name=metadata.fund_name+' native NAV', instrument_type='fund_nav',
        value_basis='nav', currency='EUR', adjustment_status='native',
        adjustment_notes='Reported accumulating-class NAV; separate corporate-action adjustment not verified.'))
    source_id = reference(conn, 'source', 'source_id', 'source_code', dict(
        source_code=metadata.source_code, provider_name='DWS / Xtrackers',
        source_name=f'Official historical NAV XLSX {isin}',
        source_url=f'https://etf.dws.com/api/pdp/de-de/etf/{isin}/historicaldata/download',
        access_method='http_xlsx', authentication_required=False,
        terms_url='https://etf.dws.com/de-de/footer/nutzungsbedingungen/',
        terms_reviewed_on=date(2026, 10, 7), local_use_status='unresolved', redistribution_status='restricted',
        permission_notes='Local approved project acquisition; public visibility does not confer redistribution rights.'))
    return instrument_id, source_id


def load_batches(conn, batches, calendar):
    """Atomic pair load, including repeat attempts; conflicting input rolls back everything."""
    results = []
    with conn.transaction():
        # Serialize participating loaders before reads/inserts, including reference creation.
        conn.execute("SELECT pg_advisory_xact_lock(hashtextextended('ifa:pair-load', 0))")
        for acquisition, frame, issues in batches:
            instrument_id, source_id = seed(conn, acquisition)
            existing = {row[0]: row[1:] for row in conn.execute(
                'SELECT observation_date,value,quality_status FROM core.observation WHERE instrument_id=%s',
                (instrument_id,)).fetchall()}
            incoming = list(frame.itertuples(index=False))
            additions = []
            for row in incoming:
                day = row.observation_date.date()
                if day in existing:
                    if existing[day] != (row.value, row.quality_status):
                        raise ObservationConflict(f'{acquisition["isin"]} {day}: existing NAV/status differs; load rolled back')
                else:
                    additions.append(row)
            run_id = conn.execute('''INSERT INTO core.ingestion_run
                (source_id,instrument_id,retrieved_at,request_url,request_parameters,
                 requested_start_date,requested_end_date,observed_start_date,observed_end_date,
                 raw_file_path,file_sha256,file_bytes,rows_read,rows_accepted,rows_rejected,rows_inserted,pipeline_version)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0,%s,%s) RETURNING ingestion_run_id''',
                (source_id,instrument_id,acquisition['retrieved_at'],acquisition['request_url'],
                 Jsonb(dict(startDate=acquisition['requested_start'],endDate=acquisition['requested_end'],includeTax=False)),
                 acquisition['requested_start'],acquisition['requested_end'],
                 frame.observation_date.min().date(),frame.observation_date.max().date(),
                 acquisition['raw_file'],acquisition['file_sha256'],acquisition['file_bytes'],
                 len(frame),len(frame),len(additions),VERSION)).fetchone()[0]
            with conn.cursor() as cur:
                cur.executemany('''INSERT INTO core.observation
                    (instrument_id,observation_date,value,ingestion_run_id,raw_row_number,quality_status)
                    VALUES (%s,%s,%s,%s,%s,%s)''',
                    [(instrument_id,r.observation_date.date(),r.value,run_id,r.raw_row_number,r.quality_status)
                     for r in additions])
            # Gap issues belong to each attempt; repeats do not alter prior classifications.
            for gap in calendar:
                if gap['isin'] != acquisition['isin']:
                    continue
                conn.execute('''INSERT INTO core.quality_issue
                    (ingestion_run_id,instrument_id,observation_date,check_code,severity,details)
                    VALUES (%s,%s,%s,'calendar_gap',%s,%s)''',
                    (run_id,instrument_id,gap['gap_date'],
                     'info' if gap['classification']=='expected/non-valuation day' else 'warning',
                     json.dumps(gap,sort_keys=True)))
            for issue in issues.itertuples(index=False):
                conn.execute('''INSERT INTO core.quality_issue
                    (ingestion_run_id,instrument_id,raw_row_number,check_code,severity,details)
                    VALUES (%s,%s,%s,%s,%s,%s)''',
                    (run_id,instrument_id,None if str(issue.raw_row_number)=='nan' else issue.raw_row_number,
                     issue.check_code,issue.severity,issue.details))
            conn.execute("UPDATE core.ingestion_run SET status='succeeded', completed_at=clock_timestamp() WHERE ingestion_run_id=%s", (run_id,))
            results.append(dict(isin=acquisition['isin'],instrument_id=instrument_id,source_id=source_id,
                                ingestion_run_id=run_id,rows_read=len(frame),rows_inserted=len(additions)))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path('.env.app'))
    parser.add_argument('--manifest', type=Path, default=Path(DEFAULT_MANIFEST))
    args = parser.parse_args()
    root = Path.cwd()
    batches, calendar = prepare_batches(root, args.manifest)
    with psycopg.connect(**connection_settings(args.config), autocommit=True) as conn:
        results = load_batches(conn, batches, calendar)
    print(json.dumps(results, indent=2))  # IDs/counts only; never connection credentials.


if __name__ == '__main__':
    main()

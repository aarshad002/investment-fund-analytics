"""Verify live pair coverage, integrity and unchanged observations after repeat loading."""
from pathlib import Path
from datetime import datetime
import hashlib
import json

import psycopg

from investment_fund_analytics.database_loading import (
    connection_settings, prepare_batches, load_batches, DEFAULT_MANIFEST,
)


def verify(root):
    batches, calendar = prepare_batches(root, root / DEFAULT_MANIFEST)
    with psycopg.connect(**connection_settings(root / '.env.app'), autocommit=True) as conn:
        version = conn.execute('SELECT version()').fetchone()[0]
        database, user = conn.execute('SELECT current_database(),current_user').fetchone()
        query = '''SELECT o.instrument_id,o.observation_date,o.value,o.ingestion_run_id,o.raw_row_number,
                          o.quality_status,o.created_at FROM core.observation o
                          JOIN core.instrument i USING(instrument_id)
                          JOIN core.fund_share_class f USING(fund_share_class_id)
                          WHERE i.instrument_type='fund_nav' AND f.isin IN ('LU0380865021','LU0290355717')
                          ORDER BY o.instrument_id,o.observation_date'''
        before = conn.execute(query).fetchall()
        repeat = load_batches(conn, batches, calendar)
        after = conn.execute(query).fetchall()
        assert before == after, 'Repeated load changed values or original lineage'
        assert all(r['rows_inserted'] == 0 for r in repeat)
        assert len(after) == sum(len(frame) for _, frame, _ in batches)
        # The SQL diagnostics are also exercised independently via a multi-result cursor.
        with conn.cursor() as cur:
            cur.execute((root / 'sql/validate_load.sql').read_text(encoding='utf-8'))
            diagnostics = []
            while True:
                if cur.description:
                    diagnostics.append([dict(zip([c.name for c in cur.description], row)) for row in cur.fetchall()])
                if not cur.nextset():
                    break
        coverage, duplicates, integrity = diagnostics[1:4]
        assert not duplicates
        assert all(r['orphan_count'] == 0 for r in integrity)
        assert len(coverage) == 2
        for row in coverage:
            expected = next(frame for acquisition, frame, _ in batches if acquisition['isin'] == row['isin'])
            assert row['observation_count'] == len(expected) and row['invalid_values'] == 0
            assert row['earliest'] == expected.observation_date.min().date()
            assert row['latest'] == expected.observation_date.max().date()
            assert (row['currency'],row['value_basis'],row['adjustment_status']) == ('EUR','nav','native')
        privileges = conn.execute("SELECT has_table_privilege(current_user,'core.observation','UPDATE'), has_table_privilege(current_user,'core.observation','DELETE'), has_schema_privilege(current_user,'core','CREATE')").fetchone()
        assert privileges == (False,False,False)
        lineage = conn.execute('''SELECT f.isin,s.source_code,r.source_id,r.instrument_id,r.ingestion_run_id,
            r.retrieved_at,r.file_sha256,r.rows_inserted FROM core.ingestion_run r
            JOIN core.source s USING(source_id) JOIN core.instrument i USING(instrument_id)
            JOIN core.fund_share_class f USING(fund_share_class_id) ORDER BY r.ingestion_run_id''').fetchall()
        for acquisition, _, _ in batches:
            rows = [r for r in lineage if r[0] == acquisition['isin']]
            assert all(r[6] == acquisition['file_sha256'] and r[5] == datetime.fromisoformat(acquisition['retrieved_at']) for r in rows)
        evidence = dict(version=version,database=database,loading_user=user,coverage=coverage,
                        repeat=repeat,duplicate_keys=0,foreign_key_checks=integrity,
                        values_and_lineage_unchanged=True,
                        observation_sha256=hashlib.sha256(repr(before).encode()).hexdigest(),
                        forbidden_privileges=list(privileges),lineage=lineage)
    output = root / 'data/processed/full_history/database_verification.json'
    output.write_text(json.dumps(evidence,indent=2,default=str)+'\n',encoding='utf-8')
    print(json.dumps(evidence,indent=2,default=str))
    return evidence


if __name__ == '__main__':
    verify(Path.cwd())

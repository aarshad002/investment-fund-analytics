"""Live tests use private administrator .env; isolated database, never project data."""
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
import uuid

import psycopg
from psycopg import sql
import pytest

from investment_fund_analytics.database_loading import (
    DEFAULT_MANIFEST, ObservationConflict, load_batches, prepare_batches,
)

ROOT = Path(__file__).resolve().parents[1]


def test_disposable_database_guard_rejects_working_database_names():
    from conftest import require_disposable_database
    for name in ('investment_fund_analytics', 'postgres', 'ifa_test_', 'ifa_test_not_a_uuid'):
        with pytest.raises(ValueError, match='disposable'):
            require_disposable_database(name)
    require_disposable_database('ifa_test_' + 'a' * 32)


def test_verified_input_rejects_changed_checksum(tmp_path):
    import json
    import hashlib
    manifest = json.loads((ROOT / DEFAULT_MANIFEST).read_text()) if (ROOT / DEFAULT_MANIFEST).exists() else None
    if manifest is None:
        pytest.skip('Local raw financial files are deliberately not committed')
    manifest[0]['file_sha256'] = hashlib.sha256(b'changed input').hexdigest()
    altered = tmp_path / 'manifest.json'
    altered.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match='checksum'):
        prepare_batches(ROOT, altered)


@pytest.fixture(scope='module')
def live_database(isolated_database):
    from investment_fund_analytics.calendar_validation import LOCAL_REGISTER, QUALITY_SUMMARY
    if not all((ROOT / p).exists() for p in (DEFAULT_MANIFEST, LOCAL_REGISTER, QUALITY_SUMMARY)):
        pytest.skip('Authorized local raw, calendar and quality inputs required')
    return isolated_database


def observations(conn):
    return conn.execute('''SELECT instrument_id,observation_date,value,ingestion_run_id,
                          raw_row_number,quality_status FROM core.observation
                          ORDER BY instrument_id,observation_date''').fetchall()


def test_live_pair_load_repeat_conflict_and_integrity(live_database):
    conn = live_database
    batches, calendar = prepare_batches(ROOT, ROOT / DEFAULT_MANIFEST)
    first = load_batches(conn, batches, calendar)
    expected = [len(frame) for _, frame, _ in batches]
    assert [r['rows_inserted'] for r in first] == expected
    before = observations(conn)
    assert len(before) == sum(expected)
    repeated = load_batches(conn, batches, calendar)
    assert [r['rows_inserted'] for r in repeated] == [0, 0]
    assert observations(conn) == before
    assert conn.execute('SELECT count(*) FROM core.ingestion_run').fetchone()[0] == 4
    expected_issues = 2 * (len(calendar) + sum(len(issues) for _, _, issues in batches))
    assert conn.execute('SELECT count(*) FROM core.quality_issue').fetchone()[0] == expected_issues
    assert conn.execute('''SELECT count(*) FROM core.observation o
        LEFT JOIN core.ingestion_run r ON o.ingestion_run_id=r.ingestion_run_id AND o.instrument_id=r.instrument_id
        WHERE r.ingestion_run_id IS NULL''').fetchone()[0] == 0
    for acquisition, frame, _ in batches:
        stored = conn.execute('''SELECT o.observation_date,o.value FROM core.observation o
            JOIN core.instrument i USING(instrument_id) JOIN core.fund_share_class f USING(fund_share_class_id)
            WHERE f.isin=%s ORDER BY o.observation_date''', (acquisition['isin'],)).fetchall()
        assert stored == [(row.observation_date.date(), row.value) for row in frame.itertuples()]
    changed = deepcopy(batches)
    changed[0][1].loc[0, 'value'] += Decimal('0.01')
    with pytest.raises(ObservationConflict):
        load_batches(conn, changed, calendar)
    assert observations(conn) == before
    assert conn.execute('SELECT count(*) FROM core.ingestion_run').fetchone()[0] == 4


def test_live_constraints(live_database):
    conn = live_database
    if not observations(conn):
        batches, calendar = prepare_batches(ROOT, ROOT / DEFAULT_MANIFEST)
        load_batches(conn, batches, calendar)
    row = observations(conn)[0]
    with pytest.raises(psycopg.errors.UniqueViolation), conn.transaction():
        conn.execute('''INSERT INTO core.observation(instrument_id,observation_date,value,ingestion_run_id)
                        VALUES(%s,%s,%s,%s)''', row[:4])
    with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
        conn.execute('''INSERT INTO core.observation(instrument_id,observation_date,value,ingestion_run_id)
                        VALUES(%s,'1900-01-01',0,%s)''', (row[0],row[3]))
    with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
        conn.execute('''INSERT INTO core.observation(instrument_id,observation_date,value,ingestion_run_id)
                        VALUES(%s,'1900-01-01',100,-1)''', (row[0],))


def test_live_application_privileges(live_database):
    conn = live_database
    role = 'ifa_test_role_' + uuid.uuid4().hex
    conn.execute(sql.SQL('CREATE ROLE {} NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE').format(sql.Identifier(role)))
    try:
        for grant in ['GRANT USAGE ON SCHEMA core TO {}',
                      'GRANT SELECT,INSERT ON ALL TABLES IN SCHEMA core TO {}',
                      'GRANT UPDATE ON core.ingestion_run,core.quality_issue TO {}',
                      'GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA core TO {}']:
            conn.execute(sql.SQL(grant).format(sql.Identifier(role)))
        with conn.transaction():
            conn.execute(sql.SQL('SET LOCAL ROLE {}').format(sql.Identifier(role)))
            batches, calendar = prepare_batches(ROOT, ROOT / DEFAULT_MANIFEST)
            results = load_batches(conn, batches, calendar)
            assert all(r['rows_inserted'] == 0 for r in results)
        for denied in ['UPDATE core.observation SET value=value WHERE false',
                       'DELETE FROM core.observation WHERE false',
                       'CREATE TABLE core.forbidden_table (id int)']:
            with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
                conn.execute(sql.SQL('SET LOCAL ROLE {}').format(sql.Identifier(role)))
                conn.execute(denied)
    finally:
        conn.execute(sql.SQL('DROP OWNED BY {}').format(sql.Identifier(role)))
        conn.execute(sql.SQL('DROP ROLE {}').format(sql.Identifier(role)))

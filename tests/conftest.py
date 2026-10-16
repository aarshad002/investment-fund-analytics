"""Disposable write-test databases and enforced read-only project connections."""
from pathlib import Path
import re
import uuid

import psycopg
from psycopg import sql
import pytest

from investment_fund_analytics.database_loading import connection_settings

ROOT = Path(__file__).resolve().parents[1]


def require_disposable_database(name):
    """Never allow fixture cleanup or write tests to target an arbitrary database."""
    if not re.fullmatch(r'ifa_test_[0-9a-f]{32}', name):
        raise ValueError('Only a uniquely named disposable test database is allowed')


@pytest.fixture(scope='module')
def isolated_database():
    config = ROOT / '.env'
    if not config.exists():
        pytest.skip('Disposable PostgreSQL tests require private administrator .env')
    settings = connection_settings(config)
    if settings['dbname'] != 'postgres':
        raise ValueError('Test administrator must connect to postgres maintenance database')
    name = 'ifa_test_' + uuid.uuid4().hex
    require_disposable_database(name)
    with psycopg.connect(**settings, autocommit=True) as admin:
        admin.execute(sql.SQL('CREATE DATABASE {} TEMPLATE template0').format(sql.Identifier(name)))
        try:
            with psycopg.connect(**dict(settings, dbname=name), autocommit=True) as conn:
                actual = conn.execute('SELECT current_database()').fetchone()[0]
                require_disposable_database(actual)
                if actual != name:
                    raise ValueError('Test connection does not identify the created database')
                conn.execute((ROOT / 'sql/schema.sql').read_text(encoding='utf-8'))
                yield conn
        finally:
            # Only the database created by this fixture is eligible for cleanup.
            require_disposable_database(name)
            admin.execute(sql.SQL('DROP DATABASE {}').format(sql.Identifier(name)))


@pytest.fixture
def readonly_project_database():
    config = ROOT / '.env.app'
    if not config.exists():
        pytest.skip('Read-only project checks require private application configuration')
    with psycopg.connect(**connection_settings(config),
                         options='-c default_transaction_read_only=on') as conn:
        conn.read_only = True
        assert conn.execute('SHOW transaction_read_only').fetchone()[0] == 'on'
        yield conn

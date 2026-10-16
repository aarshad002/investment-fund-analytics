"""Create the dedicated local database/roles using private administrator configuration."""
from pathlib import Path
import secrets

import psycopg
from psycopg import sql

from investment_fund_analytics.database_loading import connection_settings

DATABASE = 'investment_fund_analytics'


def setup(root):
    settings = connection_settings(root / '.env')
    if settings['dbname'] != 'postgres':
        raise ValueError('Administrator setup must connect to the postgres maintenance database')
    role_settings = {}
    with psycopg.connect(**settings, autocommit=True) as admin:
        version = admin.execute('SELECT version()').fetchone()[0]
        if int(admin.execute('SHOW server_version_num').fetchone()[0]) < 160000:
            raise ValueError('Schema requires PostgreSQL 16 or newer')
        for role, filename in [('ifa_owner', '.env.owner'), ('ifa_app', '.env.app')]:
            private = root / filename
            current = admin.execute('SELECT rolsuper,rolcreatedb,rolcreaterole FROM pg_roles WHERE rolname=%s', (role,)).fetchone()
            if current is not None:
                if any(current):
                    raise ValueError(f'{role} has excessive global privileges; review before proceeding')
                configured = connection_settings(private)
                if configured['user'] != role or configured['dbname'] != DATABASE:
                    raise ValueError(f'{filename} must identify {role} and the project database')
                if (configured['host'], configured['port']) != (settings['host'], settings['port']):
                    raise ValueError('Role connection identifies a different local server')
                role_settings[role] = configured
                continue
            if private.exists():
                raise ValueError(f'{filename} already exists; will not overwrite credentials')
            password = secrets.token_urlsafe(32)
            # Persist the generated secret first so a interrupted setup is recoverable.
            with private.open('x', encoding='utf-8') as stream:
                stream.write(f"DB_HOST={settings['host']}\nDB_PORT={settings['port']}\nDB_NAME={DATABASE}\nDB_USER={role}\nDB_PASSWORD={password}\nDB_SSLMODE=prefer\n")
            admin.execute(sql.SQL('CREATE ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD {}').format(
                sql.Identifier(role), sql.Literal(password)))
            role_settings[role] = connection_settings(private)
        exists = admin.execute('SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname=%s', (DATABASE,)).fetchone()
        if exists is None:
            admin.execute(sql.SQL('CREATE DATABASE {} OWNER ifa_owner').format(sql.Identifier(DATABASE)))
        elif exists[0] != 'ifa_owner':
            raise ValueError('Existing project database has a different owner; no ownership change attempted')
    with psycopg.connect(**role_settings['ifa_owner'], autocommit=True) as owner:
        owner.execute((root / 'sql/schema.sql').read_text(encoding='utf-8'))
        owner.execute('''REVOKE CREATE ON SCHEMA public FROM PUBLIC;
            REVOKE ALL ON DATABASE investment_fund_analytics FROM PUBLIC;
            GRANT CONNECT ON DATABASE investment_fund_analytics TO ifa_owner,ifa_app;
            GRANT USAGE ON SCHEMA core TO ifa_app;
            GRANT SELECT,INSERT ON ALL TABLES IN SCHEMA core TO ifa_app;
            GRANT UPDATE ON core.ingestion_run,core.quality_issue TO ifa_app;
            GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA core TO ifa_app;''')
    with psycopg.connect(**role_settings['ifa_app']) as app:
        if app.execute("SELECT has_table_privilege(current_user,'core.observation','UPDATE'), has_table_privilege(current_user,'core.observation','DELETE'), has_schema_privilege(current_user,'core','CREATE')").fetchone() != (False,False,False):
            raise ValueError('Existing application role has excessive inherited privileges; review required')
        app.execute('SELECT count(*) FROM core.observation')
    print(version)
    print(f'Database {DATABASE} and owner/application roles ready; private credentials are Git-ignored.')


if __name__ == '__main__':
    setup(Path.cwd())

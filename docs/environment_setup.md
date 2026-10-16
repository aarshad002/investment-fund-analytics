# Local environment setup - Windows

Updated 16 October 2026 against the existing local configuration filenames. Read [the clean-clone workflow](reproduction_guide.md) for the complete data-to-dashboard sequence.

## Verified environment and configuration roles

The audit used Windows 64-bit, Python 3.13.9 and PostgreSQL 18.6. The 16 October 2026 suite result was 66 passed, zero failed/skipped in the configured local environment. Power BI Desktop and the five-page PBIX are user-built; the exact Desktop version and PBIX checksum still need to be recorded by the user. No PBIX internals were independently inspected.

| Local file | Consumer | Database / role |
| --- | --- | --- |
| .env | database_setup; administrator integration-test fixture | postgres / local administrator (currently postgres) |
| .env.owner | SQL schema/view application and reconciliation modules | investment_fund_analytics / ifa_owner |
| .env.app | database_loading, read queries and Power BI credentials | investment_fund_analytics / ifa_app |
| .env.example | Tracked placeholder template; never authentication | Administrator bootstrap layout, with comments for the other roles |

All three real files are Git-ignored. The bootstrap reads **.env**, not .env.admin, and creates .env.owner/.env.app only when creating missing roles. Existing roles require matching existing private files; setup refuses to overwrite them or reset passwords. Power BI Desktop does not read dotenv files automatically: privately enter the application login in its credential dialog. Never include a password in SQL, M, screenshots, logs, documentation or Git.

<a id="postgresql-installation-checkpoint--7-october-2026"></a>

## Install prerequisites

Install an official supported 64-bit Python and [PostgreSQL Windows package](https://www.postgresql.org/download/windows/) if absent. The schema requires PostgreSQL 16+; the recorded working database is 18.6. Install server and command-line tools; pgAdmin is optional. Keep the selected port local (5432 in the recorded environment). Record versions actually installed; do not reinstall or recreate an existing working server/database.

From the project root in PowerShell, using an installed interpreter:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pip check
$env:PYTHONPATH = 'src'
```

The lock records the development environment, not certification on every Python/platform. requirements.txt records supported dependency ranges/purposes. No ML dependency is required. Calling the venv interpreter avoids changing execution policy. PostgreSQL and Desktop are separate installations; no Docker, GPU or cloud service is required.

## Administrator file for a new clone

Only if .env does not already exist:

```powershell
Copy-Item -LiteralPath .env.example -Destination .env
```

Privately replace placeholders: DB_HOST localhost, DB_PORT your local port, DB_NAME postgres, DB_USER the local administrator with role/database creation rights, DB_PASSWORD that administrator's private password, DB_SSLMODE prefer for this local setup. Do not send the values through chat. This is **not** the application configuration. The Python helper accepts only localhost/127.0.0.1/::1 and rejects unfilled placeholders.

Keep the example private-password field a placeholder. The optional data-directory/timeout entries describe local defaults; current modules mostly use repository-relative paths and explicit HTTP timeouts, not general dotenv-driven path configuration. Do not imply changing those optional entries reconfigures every module.

## Database bootstrap and grants

After configuring the administrator and choosing permitted inputs, run the documented bootstrap in the reproduction guide. It creates investment_fund_analytics owned by ifa_owner, applies sql/schema.sql, and creates non-superuser ifa_owner/ifa_app roles when missing. Generated secrets are written only to ignored .env.owner/.env.app. An existing database with unexpected ownership or excessive role privileges is rejected for review.

The owner applies DDL. ifa_app has core SELECT/INSERT, selected ingestion/quality UPDATE rights, and sequence access for loading; it has no observation UPDATE/DELETE or schema CREATE right. It is **not a SELECT-only role**. The twelve presentation views grant it SELECT on analytics plus schema USAGE. A separate SELECT-only BI login is optional hardening, not implemented by this batch. Public-schema creation is revoked; database CONNECT is restricted to project roles.

sql/schema.sql creates the six initial core tables and staging/core/analytics schemas. sql/benchmark_schema.sql adds benchmark metadata/assignments and btree_gist. Analytics views are applied separately in dependency order; see [reproduction](reproduction_guide.md). IF NOT EXISTS is not a schema migration mechanism and does not repair drift.

## Test and verification boundaries

Batch 2 isolates all write-capable integration tests in disposable ifa_test_<UUID> databases through tests/conftest.py. Administrator configuration must target the postgres maintenance database; generated test names and actual connection databases are checked before schema setup/cleanup. The benchmark overlap test uses synthetic metadata in that isolated database, not .env.owner or project assignments. Project-data comparison tests use read-only connections with PostgreSQL transaction_read_only enabled. The suite still creates/deletes temporary databases, a temporary NOLOGIN test role and temporary files, so it is not a strictly read-only server operation; it must not change working-project rows or sequences. See [testing evidence](testing_validation.md).

Some integration tests skip when private credentials/raw files are absent. Development-only samples and the original acquisition manifest are deliberately not in Git. A clean-clone test result may differ; record actual passed/failed/skipped counts instead of copying the development audit total.

The modules performance_validation, risk_validation and powerbi_validation apply SQL and write local outputs. database_verification performs a repeat load. They are reproduction/verification tools, **not read-only audit tools**. For a read-only check, use SELECT queries in a read-only PostgreSQL transaction. No such modules were executed during this documentation batch.

## Rights and local operation

DWS local-use/publication permission is unresolved; redistribution is restricted. Permission-gated data acquisition and local analysis do not automatically authorize publishing source data, derived tables, charts, screenshots, PDFs or PBIX. See [source register](source_register.md). Keep all private configurations and data local and excluded from Git.

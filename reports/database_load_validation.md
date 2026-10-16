# PostgreSQL setup and load validation

## Verified live results — current status

Verified against **PostgreSQL 18.6 on x86_64 Windows, 64-bit**. Authentication succeeded using the corrected root `.env` and the local `postgres` maintenance database. The original `.env` was preserved without printing its password. The project database **investment_fund_analytics** was created with `ifa_owner` as owner, `sql/schema.sql` was applied, and the pair was loaded using **ifa_app**. Generated role credentials are in Git-ignored `.env.owner` and `.env.app`; `.env.example` was never used for authentication.

Detailed observation-derived table withheld pending permission; exact evidence is retained locally.

Duplicate instrument/date keys: **0**. Non-positive/nonfinite values: **0**. All six foreign-key diagnostic relationships returned **0 orphans**, covering observation→instrument, observation→run/instrument, instrument→fund, run→source, run→instrument and quality issue→run/instrument.

### Repeated loading and lineage

Repeated loads produced runs 3–4 and 5–6, each inserting **zero** observations. Complete before/after row comparison proved that NAVs, dates, quality statuses, original ingestion-run IDs, raw row numbers and creation timestamps were unchanged. Reference IDs stayed stable. Attempts are retained deliberately; idempotence applies to observations/reference entities, not to the audit trail.

Final per-instrument observation fingerprints from the SQL diagnostics:

- Bond: `57263c595e2d0b2963270f1b3088be7f`.
- Equity: `2f0cda827fa07c626438e7faca71439f`.

The bond retrieval timestamp remains `2026-10-07T10:51:45.341035+00:00`; equity remains `2026-10-07T10:51:53.233877+00:00`. PostgreSQL may display the equivalent local offset; timestamp equality was checked as an instant, not as formatted text. Raw SHA-256 values match the acquisition manifest for all runs:

- Bond: `857c751eb339aa2fafe2aaa289d7f1ec5b159b9395253ddcab313de2f0906f13`.
- Equity: `85df2592c833be953b57085bea414629753e81eddbeef70ea3c08a82e780ec82`.

The final verification evidence is stored locally in Git-ignored `data/processed/full_history/database_verification.json`. The first verification attempt had a timestamp-format comparison failure after its repeat load had already committed. Comparing timezone-aware instants corrected that check; the later verification passed. No observations were changed by this reporting correction.

### Live tests and application privileges

**40 tests passed; none skipped.** The three live tests ran against a newly created disposable PostgreSQL database and removed it afterward. They verified initial/repeat loading, full value/lineage equality, conflict rejection with transaction rollback, exact counts/endpoints, unique/positive/FK constraints, and least-privilege loading. Conflicting synthetic NAVs were tested only in the isolated database; production observations were not modified.

The actual `ifa_app` has no observation UPDATE or DELETE permission and no CREATE permission on `core`. It has SELECT/INSERT on core tables, sequence access and UPDATE only on ingestion-run/quality-issue tables. Live tests demonstrated that the corresponding ingestion role can repeat-load successfully while observation updates/deletes and table creation are denied.

### Reproduction and remaining blockers

```powershell
$env:PYTHONPATH = 'src'
# Bootstrap uses existing private administrator .env; preserves it.
.\.venv\Scripts\python.exe -m investment_fund_analytics.database_setup
# Loading uses generated least-privilege .env.app by default.
.\.venv\Scripts\python.exe -m investment_fund_analytics.database_loading
# Performs another repeat load and verifies live counts, integrity and lineage.
.\.venv\Scripts\python.exe -m investment_fund_analytics.database_verification
.\.venv\Scripts\python.exe -m pytest -q
```

**No database-loading blockers remain.** Calendar uncertainty (the unresolved historical omission and historical calendar-transition caveats) remains relevant before unrestricted daily analysis; its annotations are stored in `core.quality_issue`. No financial metrics, Power BI or ML were computed. The earlier checkpoints below are retained as historical records and are superseded by these live results.

## Historical checkpoints

## Phase 3 continuation — current status

The user reports PostgreSQL is now installed. Rechecking services (including an outside-sandbox service query), standard installation directories, PATH and running processes did not expose the installation to this session. No `.env` or `.env.admin` is present. **Connection, server version, database creation, schema application and live loading remain unverified.** No password guessing, installation, database recreation or authentication changes were attempted.

The transactional loader is now implemented in `src/investment_fund_analytics/database_loading.py`; `database_setup.py` creates the dedicated database and owner/application roles once a local administrator connection is available. Generated owner/application passwords are written only to Git-ignored `.env.owner` and `.env`; existing files or differently owned databases are not overwritten. The application receives core SELECT/INSERT, sequence access and UPDATE only on ingestion runs/quality issues. Setup checks observation UPDATE/DELETE and schema CREATE are unavailable to it.

The loader resolves source codes S01/S06 to generated IDs, retains original retrieval timestamps/checksums, serializes participating loads with an advisory transaction lock, and commits both funds atomically. Each successful attempt gets a new run ID. Matching existing observations retain their original run/row lineage; conflicting NAVs or quality statuses raise an error and roll back the entire pair. Reference metadata differences also require explicit review. Failed transactions leave no partial data/run rows. The current loader raises an exception but does not automatically persist a failed-run audit record or operational-log file; recording the failure externally is an operator responsibility. Successful lineage and transaction safety remain intact.

Current test results: **37 passed, 3 skipped**. Live integration tests use a uniquely named disposable test database, never the project database. They cover initial and repeated pair loads, complete observation/lineage equality, conflict rollback, count/date/FK checks, unique/positive/FK constraints, and application write restrictions. They are skipped until `.env.admin` and local raw inputs are available. These results do not prove live idempotence.

Detailed observation-derived table withheld pending permission; exact evidence is retained locally.

Required connection handoff: confirm installation path and port (or WSL/Docker location), and place administrator settings in local `.env.admin` using `DB_HOST`, `DB_PORT`, `DB_NAME=postgres`, `DB_USER`, `DB_PASSWORD`, and optionally `DB_SSLMODE`. Do not send passwords through chat. Both setup and loader restrict connections to localhost addresses. The administrator needs role/database creation rights; integration tests also create/drop their own isolated test database and test role.

After the connection is available, run from the repository root:

```powershell
$env:PYTHONPATH = 'src'
.\.venv\Scripts\python.exe -m investment_fund_analytics.database_setup
.\.venv\Scripts\python.exe -m investment_fund_analytics.database_loading
# Capture sql/validate_load.sql results before and after this second load:
.\.venv\Scripts\python.exe -m investment_fund_analytics.database_loading
.\.venv\Scripts\python.exe -m pytest -q
```

These commands are prepared, **not executed successfully yet**. The earlier absence report below is historical evidence and is superseded by this current connection checkpoint. The calendar's unresolved the unresolved historical omission remains a separate daily-analysis caveat, not a blocker to storing the observations.

## Earlier installation checkpoint

Checked 7 October 2026 on the local Windows development laptop.

**Status: blocked by PostgreSQL not being detected; no installation or database loading was performed.** The user explicitly requested setup instructions instead of an automatic installation when PostgreSQL is unavailable.

## Local checks

- No PostgreSQL Windows service was returned by `Get-Service *postgres*`.
- Neither `psql` nor `pg_ctl` was found on PATH.
- No installation was found in `C:\Program Files\PostgreSQL` or matching top-level Program Files / Program Files (x86) directories.
- No installations were returned under `HKLM:\SOFTWARE\PostgreSQL\Installations`.
- `Test-NetConnection localhost -Port 5432` returned `TcpTestSucceeded=False`.

These checks cover conventional native installations and the default local port. They do not rule out an unregistered portable installation on another path/port. No database credentials were read or printed.

Detailed observation-derived table withheld pending permission; exact evidence is retained locally.

Zero loaded here does not imply that an unknown database is empty. No project database, role, or ingestion-run ID was created.

## Installation and schema setup

Follow the exact [Windows installation and role commands](../docs/environment_setup.md#postgresql-installation-checkpoint--7-october-2026). The official [PostgreSQL Windows installer guidance](https://www.postgresql.org/download/windows/) links to the EDB installer. Install PostgreSQL Server and Command Line Tools; keep a local project service and password. Then create `investment_fund_analytics`, separate owner/application roles, apply `sql/schema.sql` as owner, and grant the append-only application rights in the guide. Installation requires the user's local administrator interaction; it was not attempted.

## Load contract and required verification

Actual loading implementation and live verification remain pending a working server. The approved schema already enforces unique fund ISINs, instrument codes and source codes, observation primary keys `(instrument_id, observation_date)`, positive finite numeric NAVs, and composite run/instrument foreign keys.

The first loader must read the checked full-export manifest and revalidate raw checksums/data rather than trust editable CSVs alone. Seed the two fund share classes, native EUR NAV instruments and sources S01/S06; resolve their generated IDs instead of assuming numeric IDs. Insert an acquisition attempt in `core.ingestion_run` with source/instrument IDs, retrieval timestamp, exact URL, requested/observed dates, local raw path, checksum, bytes, pipeline version and row counts. Link every observation to that run and raw row. Persist the calendar classifications in `core.quality_issue` with the date, evidence, status and caveats. A gap issue need not have a corresponding observation row.

Required transaction behavior: serialize loads per instrument, compare existing observations before inserting, preserve identical records and their original lineage, and abort/quarantine conflicting dates without updating NAVs. A repeated attempt may create a new run, but must insert zero additional observations; its run counts must reflect that. Source/run creation and the observation batch should be atomic, with failure evidence recorded separately after rollback. Merely using `ON CONFLICT DO NOTHING` without comparing values is insufficient because it hides conflicting input.

Run [validate_load.sql](../sql/validate_load.sql) after initial and repeated loading. Compare a deterministic observation fingerprint as well as counts. Verify conflict rollback in an isolated test database and confirm the application cannot update/delete observations or create schemas.

**Idempotence: not verified against PostgreSQL.** The local consolidator's matching-overlap/conflict behavior is covered by existing unit tests, but those tests are not database-loading tests. Live loader/constraint tests cannot honestly be reported as passing without a server. Calendar annotation tests are separate and do not establish database integrity.

Local verification: 36 Python tests pass, including four calendar tests checking unknown-date handling, the unresolved half-day, exceptional holidays, and one classification per instrument/date matching the full-history gap inventory when local data are present. The new SQL diagnostics have not been executed on PostgreSQL.

## Next step and blockers

Install/start PostgreSQL using the guide, then implement and run the transactional loader and its integration tests against the dedicated project database. No loader invocation is advertised as working yet. Calendar uncertainty does not prevent storing the validated observations, but full-window daily analysis remains conditional as described in [calendar completeness](calendar_completeness.md). No financial metrics, dashboard, or ML work was performed.

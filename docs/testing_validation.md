# Batch 2 testing isolation and evidence

Validated 16 October 2026. This record supplements the earlier 66-test repository audit; it does not replace its historical results or assert PBIX inspection.

## Root cause and correction

The original benchmark overlap test used .env.owner to connect to the working project database, selected an existing assignment, and attempted an overlapping insert inside a rollback transaction. PostgreSQL identity sequence increments can survive rollback, so rejecting the insert did not guarantee an unchanged working sequence.

tests/conftest.py now provides a shared module-scoped isolated_database fixture. It requires the administrator maintenance database to be postgres, creates a fresh ifa_test_<32 hexadecimal UUID> database from template0, verifies the actual database name, applies the unchanged core schema and drops only that exact created database at teardown. Loader integration tests reuse this fixture. Test database creation/deletion is intentional; the suite is not a strictly read-only PostgreSQL-server operation.

The benchmark constraint test applies the unchanged benchmark constraint DDL in the disposable database, excluding application-role grants that are irrelevant to the constraint. It seeds test-only index/benchmark/assignment metadata, attempts the same overlapping effective interval, expects ExclusionViolation and verifies that its original assignment remains unchanged. Any identity allocation occurs only in the disposable database. It needs no working assignment, .env.owner connection or downloaded benchmark data.

The two existing working-data comparison tests retain their SQL assertions but use readonly_project_database: PostgreSQL default_transaction_read_only is enabled at connection startup, psycopg read_only is enabled, and transaction_read_only is asserted on. They issue SELECT/SHOW only. Remaining write-capable tests use the disposable database; the privilege test creates and removes a uniquely named NOLOGIN test role. Private configurations and downloaded inputs remain local and ignored.

## Executed checks

| Check | Result |
| --- | --- |
| Benchmark and loader integration modules | 10 passed, 0 failed, 0 skipped |
| Full existing suite plus one isolation-guard regression | 67 passed, 0 failed, 0 skipped |
| Working core table fingerprints before/after both runs | All eight tables identical, including original lineage and metadata |
| Working core sequence last_value/is_called before/after | All seven sequences identical |
| Remaining ifa_test_* databases after cleanup | None |
| Remaining ifa_test_role_* roles after cleanup | None |

The new pure guard regression rejects the project database name, postgres and malformed test names; it accepts only the expected disposable UUID format. No validated financial formula, production SQL view, DAX measure or PBIX was changed. The configured development machine has local inputs/credentials, so no integrations skipped; a fresh clone may skip source-dependent checks. These dated counts are evidence of these executions, not a permanent guarantee.

Reproduction after reviewing the temporary-database/role scope:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_benchmark_loading.py tests/test_database_loading.py -ra
.\.venv\Scripts\python.exe -m pytest -ra
```

## Financial and dashboard evidence boundaries

Prior independent SQL checks cover both funds' performance, controlled risk, observed drawdown, 63/252-observation rolling volatility, monthly/calendar-year returns, recovery details, quality classifications and original source/run/checksum/retrieval lineage. Existing successful-loader lineage, repeat-load safety and conflict rollback assertions remain in place.

Five Power BI pages and manual screenshot/fund-selection review are user-completed evidence. SQL comparisons and repository DAX review do not constitute direct PBIX inspection, DAX engine evaluation or automated Power BI interaction tests. Desktop version, PBIX hash/revision, actual Desktop refresh time and precise screenshot-review artifact references remain pending, not invented. See [dashboard evidence](../reports/powerbi_validation.md).

The loader preserves successful lineage and atomic transaction safety; a failed conflict can roll back before a run exists and does not necessarily leave a failed-ingestion audit record or automatic failure-log file. Separate failed-attempt persistence remains unimplemented. This batch corrects documentation, not loader behavior.

Source publication permission remains unresolved and redistribution restricted. This testing record does not grant permission to publish raw data, derived financial values, screenshots or imported PBIX data. No such artifact was published by this batch.

## Local calendar input separation

Portable classification and structural tests do not require private financial inputs. Real-register checks require both the ignored local register and quality summary; absence produces an explicit SKIP. Loading checks also require the authorized raw manifest and use disposable databases. Expected real-input row counts and records are independently derived from local inputs rather than fixed published dataset counts. Successful local test results do not imply that a clean public clone executed private-data checks. The register is reconstructed and reviewed before loading; see [reproduction guide](reproduction_guide.md).

## Calendar separation verification - 16 October 2026

The configured local suite passed 81 tests with no failures or skips. A separate public-files-only copy, containing no private credentials, register, raw samples or database inputs, passed 65 tests and explicitly skipped 16 private-input/integration checks. These are dated results, not a clean-clone claim that private financial verification ran.

Read-only fingerprints confirmed unchanged working tables, sequences, analytical outputs and twelve Power BI view structures. Independent Python/SQL reconciliation passed using the preserved local register. Financial formula modules and classification decisions are unchanged; SQL differs only in approved explanatory wording. No working database DDL/loading/reconciliation entry points were executed. The populated register matches its previously recorded original hash, and the public CSV contains only its approved header. Detailed evidence remains local. The earlier clean-history rehearsal is stale and requires rebuilding; no GitHub operation occurred.

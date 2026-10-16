# Clean-clone reproduction workflow

Updated 16 October 2026. This is an execution guide, not a claim that a fresh-clone reproduction was run during the documentation batch. It preserves existing calculations. Commands below intentionally create local files/database objects; they are not read-only audit commands. All paths assume repository root and PowerShell.

## 1. Clone and prepare the environment

Clone aarshad002/investment-fund-analytics and enter its root. Follow [environment setup](environment_setup.md) for Python/requirements-lock.txt, PostgreSQL and private administrator configuration. Set `$env:PYTHONPATH = 'src'` in each execution shell. Do not overwrite existing .env/.env.owner/.env.app. Ensure local PostgreSQL is running and the administrator maintenance database is postgres.

## 2. Confirm authorization before acquiring data

The verified technical source is the official DWS historical XLSX backend, described in [source register](source_register.md). Local-use/publication permission is unresolved and redistribution restricted. Establish the applicable permission basis before a fresh acquisition; public visibility is not permission. This guide does not grant provider rights. If permission cannot be established, stop acquisition and reassess sources separately; do not silently replace the approved series.

The implemented acquisition targets the fixed project window 2021-09-30 to 2026-09-30. It makes two bounded requests and preserves immutable XLSX files, checksums, timestamps and a manifest under a new data/raw/full_history/<UTC timestamp>/ folder:

```powershell
.\.venv\Scripts\python.exe -m investment_fund_analytics.full_history --acquire
```

Existing full-history validation also compares the six original phase0 samples when present. They are optional; a clone need not obtain or fabricate those development samples. Parser tests provide their own deterministic workbooks.

## 3. Select the acquisition manifest explicitly

Do not copy the developer's original timestamped path from old reports. Inspect candidate manifests and select the exact acquisition just authorized, checking both ISINs, requested bounds, retrieved_at, raw paths and checksums:

```powershell
Get-ChildItem -LiteralPath data/raw/full_history -Recurse -Filter manifest.json |
    Select-Object FullName, LastWriteTimeUtc
$ifaManifest = 'data/raw/full_history/<actual-acquisition-directory>/manifest.json'
.\.venv\Scripts\python.exe -m investment_fund_analytics.full_history --manifest $ifaManifest
```

Replace the placeholder manually; do not assume the newest timestamp is necessarily the intended dataset. Validation rejects conflicting versions rather than silently overwriting them. Reuse the cached files offline after acquisition. Source revisions may differ from the recorded development counts/values; investigate rather than forcing matching outputs.

## 4. Reconstruct and review the local calendar, then bootstrap and load

After authorized acquisition and full-history validation, quality_summary.json under data/processed/full_history/ records the observed omissions. Reconstruct the local register before database loading:

```powershell
.\.venv\Scripts\python.exe -m investment_fund_analytics.calendar_validation
```

The populated register lives only at data/interim/calendar/calendar_gap_register.csv (Git-ignored). docs/calendar_gap_register.csv is a header-only schema template and is never a runtime fallback. Review reconstructed decisions against the cited issuer/holiday evidence before loading. Unknown dates remain unresolved; never invent closures or treat absence as a zero return. The reviewed rules retain their historical scope and are not a generic market calendar.

Reconstruction refuses to overwrite an existing register when inputs differ. Preserve it and resolve revised inputs separately; do not delete or overwrite prior approved evidence to force acceptance. The runtime requires exact fund/date agreement with the local quality summary and rejects malformed, duplicate, missing or changed classifications. A header-only local register is accepted only when nonempty quality evidence explicitly establishes no omissions.

```powershell
.\.venv\Scripts\python.exe -m investment_fund_analytics.database_setup
.\.venv\Scripts\python.exe -m investment_fund_analytics.database_loading --config .env.app --manifest $ifaManifest
```

Bootstrap uses private administrator configuration and creates/reuses owner/application configuration. Select the acquisition manifest explicitly; the historical default is not available in a clean clone. Identical repeat loading preserves observations and contributing lineage while recording successful attempts. Conflicts roll back; failed-run audit persistence is not automatic.

## 5. Apply approved analytical SQL

In pgAdmin, connect privately as ifa_owner to investment_fund_analytics. In Query Tool open and execute the files below in order. An alternative is psql from the repository root with host localhost, actual port, database investment_fund_analytics, user ifa_owner, `-W` to prompt for its password and `-v ON_ERROR_STOP=1 -f <file>`. Do not put the password on the command line.

1. sql/performance_views.sql - endpoint, period and observed-path drawdown views.
2. sql/controlled_intervals.sql - approved fixed-window eligibility metadata.
3. sql/risk_views.sql - six approved NAV-only risk metrics.
4. sql/powerbi_views.sql - twelve presentation views.

For a fresh clone, benchmark_schema.sql/benchmark_loading are **not prerequisites for the NAV dashboard**. The existing benchmark loader is tied to the developer's original manifest and has no CLI manifest override. Do not assume it consumes $ifaManifest. Benchmark/cash validation remains a separate incomplete task, with no relative metrics enabled.

Optionally run existing Python reconciliation modules after the approved NAV load:

```powershell
.\.venv\Scripts\python.exe -m investment_fund_analytics.performance_validation
.\.venv\Scripts\python.exe -m investment_fund_analytics.risk_validation
.\.venv\Scripts\python.exe -m investment_fund_analytics.powerbi_validation
```

These apply their respective SQL, write ignored local outputs and assert reconciliation; they are not read-only. They do not enable unapproved metrics. New generated numerical Markdown reports are local under data/processed/, and do not automatically update or publish reviewed reports/ evidence. Dashboard evidence is maintained separately in reports/powerbi_validation.md. Do not run generators merely to update documentation during a read-only audit.

## 6. Connect and refresh Power BI Desktop

Use the [data model](powerbi_data_model.md), [field mapping](powerbi_field_mapping.md), [DAX definitions](../powerbi/measures.dax) and [build/refresh guide](powerbi_build_guide.md). Existing users open the local Investment_Fund_Analytics.pbix; it is not included in a public clone. A clone must rebuild it from the guide or obtain a separately authorized artifact.

Get Data > PostgreSQL > server localhost:5432 (actual port if different), database investment_fund_analytics, Import mode. Enter ifa_app credentials privately from .env.app using Database authentication. Import only the twelve analytics.pbi_* views. Configure the documented single-direction 1:* relationships; no fact-to-fact joins. Snapshot/quality/lineage facts connect only to DimFund. The auxiliary RefreshInfo table is local Power Query metadata, not another database financial source.

Refresh, inspect each fund and both-fund contexts, and record Desktop version, refresh UTC, PBIX revision/checksum and manual results. Performance/recovery uses 2021-09-30 to 2026-09-30; controlled risk uses 2023-12-01 to 2026-09-30. Chart dates do not rebase curves or recalculate fixed snapshots. Risk uses consecutive observed intervals, preserves elapsed days, excludes unexplained gaps, and annualizes approximately by 252 intervals/year; VaR/ES have variable calendar-day horizons. Preserve period/rolling NULLs and zero-target downside labels. Disabled cash/benchmark metrics remain absent.

## 7. Record checks and keep artifacts private

The 16 October 2026 audit recorded 66 passing tests in the development environment. It is dated evidence, not a guarantee for this clone. Batch 2 moves the benchmark overlap write to a disposable test database and enforces read-only project comparison connections. The suite still creates/deletes temporary test databases/roles and files, so it is not a strictly read-only server operation. See [current isolation and test evidence](testing_validation.md). The documentation-only batch did not change tests; Batch 2 subsequently corrected isolation.

Record independent SQL comparison separately from user-performed Desktop review. No direct PBIX inspection by Codex has been established. Before sharing any imported PBIX, derived values, screenshots or PDF, review source permissions and artifact contents. Acquisition authorization does not authorize redistribution; DWS local-use/publication permission remains unresolved and redistribution restricted. Existing numerical reports also remain subject to review. No dataset, secret or PBIX belongs in the initial public reproduction package.

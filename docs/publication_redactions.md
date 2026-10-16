# Batch 4A redaction comparison and preservation record

Prepared 16 October 2026. This document lists withheld categories without repeating source-derived financial values. It records working-tree edits only: no staging, commit, push, deletion or history remediation has occurred, and no licensing clearance is claimed.

## Exact-byte local preservation

Before editing affected reports, the batch copied their exact bytes into a uniquely named directory under data/interim/publication_archive/. Seven working-tree originals were preserved: the five result-bearing files below, README.md and docs/publication_review.md. Six initial-commit versions were additionally preserved: those five result-bearing files and the older reports/powerbi_validation.md.

The local manifest.json records each original relative path, origin (pre-Batch-4A working tree or initial commit), archive relative path, byte size and SHA-256. All thirteen copies matched their source-byte hashes before redaction and remained recoverable after it. The archive and manifest are Git-ignored; they are not part of the public candidate. Restore by copying the selected archived bytes only after separately approving an appropriate local destination; do not overwrite candidate documents inadvertently. No original bytes were destroyed.

## Explicit before/after comparison - categories only

| Current file | Pre-redaction contents withheld | Current candidate retains |
| --- | --- | --- |
| reports/performance_analysis_validation.md | Actual return/CAGR/drawdown comparison table; observed peak/trough/recovery dates and episode durations | Formula conventions, boundary/NULL treatment, SQL/Python checking procedure, local evidence locations and qualitative recovered/ongoing conclusions |
| reports/risk_analysis_validation.md | Actual volatility/downside/VaR/ES/rolling values; empirical ES tail count and rolling-output totals | Approved risk-window policy, eligibility/NULL requirements, formulas, zero-target distinction, approximate annualization, reconciliation procedure and local outputs |
| docs/benchmark_sources.md | Issuer-displayed and export-derived benchmark return comparisons and their numerical discrepancy | Benchmark identity/basis, acquisition route, source lineage, alignment gate and qualitative discrepancy beyond rounding |
| docs/cash_benchmark_validation.md | DWS benchmark comparison values plus actual ECB diagnostic sample rates | Distinct source provenance, bounded access method, date/publication conventions, access failure and incomplete cash/benchmark validation; ECB rights question remains separate |
| docs/powerbi_build_guide.md | Actual financial KPI reference values and empirical ES tail count | Model/page instructions, SQL validation queries, methodology windows, tolerance/rounding procedure and manual interaction checks |

README now explains that financial values are withheld while private verification remains established. No withheld values were moved into another tracked report, example, screenshot or demonstration dataset. reports/powerbi_validation.md was already non-numerical following Batch 1; its older initial-commit table is preserved locally and remains historically exposed.

## Deliberately retained numbers and metadata

Mathematical/implementation parameters remain unchanged: risk confidence level, annualization convention, rolling-window lengths, SQL numeric precision, test tolerances, date bounds and configuration ports. Existing deterministic unit-test fixtures are original test logic, not actual fund findings. No new synthetic financial data was created. Source code, SQL definitions, DAX, tests, raw/processed observations, database contents and PBIX were not altered by this batch.

Historical Batch 4A checkpoint: the candidate then retained identifiers/provenance alongside empirical coverage/count summaries and observed calendar classifications. The later separation update below supersedes retention of detailed empirical records. This is an explicit contents distinction, **not a conclusion that source-derived metadata is legally cleared**. The original populated register feeds approved eligibility checks; it is now preserved byte-for-byte locally, with runtime paths redirected and a public header-only template. See [publication inventory](publication_review.md).

Validation totals, software versions and numerical reconciliation tolerances/errors describe software verification, not investment results. They remain labelled as dated private evidence. A fresh public clone without permitted financial inputs cannot reproduce all live numerical checks, and synthetic unit tests alone do not establish that financial reproduction occurred.

## History exposure - not remediated

The previously pushed initial commit contains potentially restricted financial values in:

- reports/performance_analysis_validation.md
- reports/risk_analysis_validation.md
- reports/powerbi_validation.md (its older numerical KPI table)
- docs/benchmark_sources.md
- docs/cash_benchmark_validation.md (including separately sourced ECB diagnostic rates)
- docs/powerbi_build_guide.md

Its source/coverage/calendar metadata is also present in README and other documentation, including docs/calendar_gap_register.csv, docs/source_register.md and quality/lineage reports; that metadata category still requires clarification. Current redaction does not erase those historical blobs, public copies or caches. No history rewrite, force-push, visibility change or deletion was attempted.

## Remaining release gates

Permission for DWS acquisition/local analysis, derived-result publication and any applicable benchmark-owner rights remains unresolved; redistribution is restricted. ECB reuse/attribution and source-derived metadata require separate clarification. Imported-data PBIX, actual-data screenshots/PDFs, source/processed series and database exports remain local. Redaction reduces current financial-result exposure but does not confer permission or clear the public repository's historical contents. Provider permission, metadata decisions and any historical remediation require separate approval/review.

## Calendar separation and empirical metadata withholding

The public docs/calendar_gap_register.csv is now a six-column header-only template. Its exact populated original is preserved at data/interim/calendar/calendar_gap_register.csv, Git-ignored and checksum-verified. Runtime readers require this local register and the local quality summary; they never fall back to the public template. Classification rules and financial formulas are unchanged.

Detailed empirical coverage/count tables and observation-level omissions are withheld from public summaries pending permission. Earlier statements in this dated review that these records remain public describe the pre-separation checkpoint and are superseded here. Ordinary fund identities, source links, original provenance/checksums, chosen windows, code, methodology and deterministic fixtures remain public. Local numerical reports and archived originals remain private. Removing current records does not erase historical Git exposure or grant permission.

The current separation withholds per-fund observed gap rows, detailed coverage/count tables, missing-benchmark dates and fixed empirical counts embedded in verification narrative. Original evidence remains in ignored archives; source timestamps/checksums and chosen parameters remain public. SQL changes are confined to explanatory wording. Existing database contents and PBIX are not changed. The pre-separation rehearsal commit must not be reused.

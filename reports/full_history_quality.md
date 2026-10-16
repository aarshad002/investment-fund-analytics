# Full historical NAV quality report

Documentation clarification, 16 October 2026: the acquisition-stage evidence below is historical. PostgreSQL loading and validated performance/controlled-risk analytics subsequently completed, and the user completed and manually reviewed all five Power BI pages. This is not a claim of direct PBIX inspection. See [current project status](../README.md) and [dashboard evidence](powerbi_validation.md).

Acquired 7 October 2026 from official DWS/Xtrackers dated XLSX exports. Requested 2021-09-30 through 2026-09-30: approximately five years, including the preceding valuation for an October 2021 start.

## Coverage and consolidation

Detailed observation-derived table withheld pending permission; exact evidence is retained locally.

## Validation and assumptions

The existing sample parser validates workbook identity, EUR currency, dates, finite positive NAVs, numeric precision, duplicate dates, and source ordering. It screens adjacent valid NAV changes above 20% in absolute magnitude as review flags; this is a quality threshold, not a financial metric. Suspicious observations are retained and flagged. Invalid rows and every conflicting version are preserved separately and excluded from the validated dataset. Identical overlaps explicitly select the full export first and retain supporting-file references; no conflicting value is silently overwritten.

The same Date/NAV workbook parser handles both full files. NAV is native reported EUR NAV, not market close or a separately verified corporate-action-adjusted series. No interpolation, calendar filling, or FX conversion is performed. Missing auxiliary index/AUM/tax values do not invalidate a populated NAV.

### LU0290355717

- Exact acquisition: [official dated export](https://etf.dws.com/api/pdp/de-de/etf/LU0290355717/historicaldata/download?startDate=2021-09-30&endDate=2026-09-30&includeTax=false).
- Retrieved UTC: `2026-10-07T10:51:45.341035+00:00`; HTTP 200; 61,631 bytes. No authentication or payment supplied.
- Local raw file: `data/raw/full_history/20261007T105130116510Z/LU0290355717_2021-09-30_2026-09-30.xlsx`; SHA-256: `857c751eb339aa2fafe2aaa289d7f1ec5b159b9395253ddcab313de2f0906f13`.
Detailed row-quality, overlap and interval findings are retained locally pending permission.
Detailed row-quality, overlap and interval findings are retained locally pending permission.
Detailed row-quality, overlap and interval findings are retained locally pending permission.
Detailed observed counts and coverage findings are retained in Git-ignored local evidence pending publication permission.
- Local outputs: `data/processed/full_history/LU0290355717_validated.csv`, plus all rows, conflicts, flags, issues and weekday-gap CSVs.

### LU0380865021

- Exact acquisition: [official dated export](https://etf.dws.com/api/pdp/de-de/etf/LU0380865021/historicaldata/download?startDate=2021-09-30&endDate=2026-09-30&includeTax=false).
- Retrieved UTC: `2026-10-07T10:51:53.233877+00:00`; HTTP 200; 60,409 bytes. No authentication or payment supplied.
- Local raw file: `data/raw/full_history/20261007T105130116510Z/LU0380865021_2021-09-30_2026-09-30.xlsx`; SHA-256: `85df2592c833be953b57085bea414629753e81eddbeef70ea3c08a82e780ec82`.
Detailed row-quality, overlap and interval findings are retained locally pending permission.
Detailed row-quality, overlap and interval findings are retained locally pending permission.
Detailed row-quality, overlap and interval findings are retained locally pending permission.
Detailed observed counts and coverage findings are retained in Git-ignored local evidence pending publication permission.
- Local outputs: `data/processed/full_history/LU0380865021_validated.csv`, plus all rows, conflicts, flags, issues and weekday-gap CSVs.

## Calendar review

Absent weekdays are screened against Monday–Friday only. They are not established missing valuations: an authoritative historical fund valuation calendar has not yet been reconciled. Shared omissions may reflect source/valuation calendars, but this does not prove their cause. Weekend and holiday closures must not be replaced with zero returns. Preserve the gap register for review before daily analytical calculations.

Detailed dataset-derived table withheld; exact original evidence remains local.

## Database-loading readiness

Both actual exports pass row-level validation and conflict checks and can be loaded as validated NAV observations with their acquisition lineage and the accompanying calendar-gap register. The unresolved historical valuation calendar limits completeness claims and daily analytics readiness; database loading itself does not require filling these dates. Review any future flags/conflicts before accepting their rows. At this acquisition-stage checkpoint, PostgreSQL had not yet been loaded and no performance/risk metrics, Power BI dashboard or ML had been produced. Later project progress is identified in the clarification above; ML remains unimplemented.

Raw files, manifests, and processed datasets are Git-ignored. This document retains acquisition methodology and quality/provenance metadata; it is not a statement that publication rights are cleared. Detailed source-derived financial findings are retained locally pending redistribution permission. Derived values, charts, screenshots and PBIX data are not automatically safe to publish; the retained metadata also remains subject to the [publication review](../docs/publication_review.md). Access is a public website backend, not a supported developer API; DWS/third-party reuse restrictions remain as documented in the source register. Public availability does not establish redistribution permission.

## Offline reproduction

```powershell
$env:PYTHONPATH = 'src'
 .\.venv\Scripts\python.exe -m investment_fund_analytics.full_history --manifest data/raw/full_history/20261007T105130116510Z/manifest.json
 .\.venv\Scripts\python.exe -m pytest -q
```

Validation verifies manifest checksums before parsing and writes a detailed Git-ignored local report without downloading. An explicit `--acquire` instead makes two new bounded requests and stores them in a new timestamped folder; existing raw downloads are not overwritten.

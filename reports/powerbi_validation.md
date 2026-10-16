# Power BI validation evidence and scope

Documentation reconciled 16 October 2026. This record separates independent PostgreSQL checks from user-performed Desktop review; it is not a claim of independent PBIX inspection or a publication-rights clearance.

## Delivered dashboard - user-reported evidence

The user reports completing, saving locally and manually reviewing all five pages, including screenshots and the main fund-selection interactions:

1. Executive Overview
2. Performance Comparison
3. Risk & Drawdowns
4. Fund Detail
5. Data Quality & Methodology

The local artifact is powerbi/Investment_Fund_Analytics.pbix and remains Git-ignored. Codex has not inspected its contents, evaluated its DAX in the Power BI engine or independently exercised visual interactions. Exact Desktop version, PBIX checksum/revision and manual-review timestamps/preview locations remain to be supplied by the user. Screenshots have not been exported or published by this documentation batch.

## Independently checked database evidence

Prior read-only PostgreSQL validations checked approved snapshot values, performance series, monthly/year boundaries and NULL handling, observed drawdowns/recovery, rolling series/counts and original source lineage. The initial presentation preparation checked keys, dimension references and snapshot reuse across twelve pbi_* views. The final 16 October 2026 repository audit ran the existing suite: **66 passed, 0 failed, 0 skipped**, in the configured local environment. No tests or financial queries were rerun during Batch 1. Batch 2 subsequently reran the isolated integration tests and suite; see [testing evidence](../docs/testing_validation.md) for the separate dated results and project-state checks.

| Page | Independent SQL/repository evidence | Desktop evidence boundary |
| --- | --- | --- |
| Executive Overview | Both funds' reported KPI values reconcile to approved performance/risk snapshots and latest rolling series; separate windows/counts checked | User reports completed cards and fund-selection review; no independent PBIX interaction check |
| Performance Comparison | Original base, representative daily values, final snapshot agreement, all non-null yearly/monthly endpoint checks and incomplete-period suppression checked | User reports completed visuals and manual review; actual axes, field bindings, sorting and slicer configuration not independently inspected |
| Risk & Drawdowns | Observed minima and recovery dates reconcile; rolling counts, first non-null dates, intermediate/final values and snapshot equality checked | User reports completed page and fund selection; actual DAX/visual behavior not independently evaluated |
| Fund Detail | Identity and approved individual financial/source data checked through shared SQL views; repository DAX reviewed | User reports page completed; direct drill-through, field binding and visual layout not independently inspected |
| Data Quality & Methodology | Fund coverage/counts, gap classifications, source/run mapping, acquisition timestamps/checksums and original provenance checked | User reports screenshot/manual review; actual formatting, refresh labels and interactions not independently inspected |

Exact numerical SQL references remain local under data/processed/powerbi/. This report records scope and evidence without republishing numerical KPI tables. Subsequent powerbi_desktop_evidence runs write an ignored SQL-reference report instead of overwriting this manual record. Its output establishes SQL reference values only, never Desktop evaluation.

## Methodology and display contract

Performance/observed-path drawdown and recovery cover **2021-09-30 to 2026-09-30**. Controlled NAV risk covers **2023-12-01 to 2026-09-30**. Both actual endpoints and elapsed interval lengths are retained; no NAV filling or absent-date zero returns occur. Weekend/reviewed closures are retained, unexplained intervals excluded, and rolling windows cannot bridge excluded inputs. Annualization assumes approximately 252 valuation intervals/year. VaR/ES describe variable-calendar-length valuation intervals. Downside deviation targets zero return.

The full-calendar issue is not resolved by restricted-window approval. Native NAV is not independently certified adjusted total-return data, and observed-path drawdowns can miss unobserved losses or earlier recovery. Cash/benchmark-relative metrics and ML remain absent; benchmark names are descriptive metadata only.

Snapshots stay fixed-window even when chart dates are sliced. The repository DAX guards require one fund/snapshot or one fund/date row as appropriate. Model documentation specifies single-direction 1:* links and no fact-to-fact joins. This is a documented contract, not independent evidence that the PBIX matches it. No Power BI engine DAX differences were measured.

## Reproduction and release restrictions

See [clean-clone workflow](../docs/reproduction_guide.md), [data model](../docs/powerbi_data_model.md), [field mapping](../docs/powerbi_field_mapping.md) and [Desktop guide](../docs/powerbi_build_guide.md). Credentials remain private in .env.app for application/Desktop use; administrator and schema-owner configurations remain separate.

DWS source-use/publication permission is unresolved and redistribution is restricted. Technical validation and user dashboard completion do not clear imported PBIX data, derived financial values, charts, screenshots or PDF exports for publication. Existing published numerical reports need the same rights review. See [source register](../docs/source_register.md). No rights clearance, new artifact publication or direct PBIX validation is asserted here.

## Artifact evidence still pending

| Evidence item | Status |
| --- | --- |
| Power BI Desktop exact version | Pending user-provided record |
| Saved PBIX checksum/revision | Pending; no hash invented or file contents inspected |
| Actual Desktop refresh UTC | Pending user-provided record; SQL query time is not a substitute |
| Manual screenshot-review date and screenshot locations | User confirms review occurred; exact artifact references/date pending |
| Main fund-selection tests | User confirms manual success; direct automated PBIX interaction results unavailable |

Both-fund SQL validation covers performance, risk, drawdown, rolling volatility, monthly/calendar-year returns, recovery, quality and original source lineage. These checks are independently established database evidence, not screenshots inferred by this routine and not direct PBIX validation. No new financial query or numerical-report publication is part of this evidence update.

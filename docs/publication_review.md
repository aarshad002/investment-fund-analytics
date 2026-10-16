# Publication-safety review and release inventory

Historical Batch 4A inventory, 16 October 2026; calendar/metadata separation update below supersedes its retained-record status. This is a contents-based publication assessment, not legal clearance or a claim that public history is free of source-derived information. Exact detailed originals are preserved in a verified Git-ignored archive. Targeted current-tree redactions are now performed; no financial dataset, screenshot or PBIX was published, and no staging, commit, push, deletion or history change occurred. See [preservation and redaction comparison](publication_redactions.md).

## Classification rules

- **Suitable based on known rights and contents:** original project code, schemas, tests, configuration placeholders and original non-numerical explanatory material, subject to normal authorship/dependency checks. This does not license third-party data or establish that every third-party asset may be reused.
- **Withhold pending permission or further review:** source files/series, source-derived numerical financial findings, benchmark comparisons and artifacts embedding those contents. Public access and successful validation do not establish redistribution permission.
- **Requires clarification:** mixed documents, provider/issuer metadata, calendar omission registers, acquisition/coverage metadata and independently sourced ECB material where the exact intended reuse/attribution scope has not been settled.

## Tracked contents inventory

The tracked-file audit covered all 67 index-tracked files, including current working-copy edits. New Batch 1/2 documentation and test fixtures were also checked as release candidates. No tracked binary financial dataset, PBIX, screenshot, PDF or database export was found. No embedded credential or personal absolute user-directory path was detected by the review; secret scanning is not an absolute guarantee.

| Contents / paths | Classification | Evidence and minimum handling |
| --- | --- | --- |
| src/, sql/, tests/, powerbi/measures.dax | Suitable based on known contents | Original implementation, formulas, schema/view definitions and deterministic tests; not downloaded series. Runtime numerical outputs must stay local. Existing synthetic unit-test sequences are test cases, not new portfolio demo data. |
| requirements.txt, requirements-lock.txt, pytest.ini, .gitignore, .env.example and .gitkeep placeholders | Suitable based on known contents | Configuration/dependency references and empty directory markers; real environment files excluded. No blanket license to dependency code/data is conferred. |
| Updated README; data dictionary, metric/risk methodology, Power BI model/field mapping; reproduction/testing documentation | Suitable based on known explanatory contents | Architecture, formulas, test evidence and non-numerical dashboard descriptions. Format examples in powerbi_field_mapping.md are formatting instructions, not actual fund results. Fund identities and coverage metadata are not a downloaded price series. |
| reports/performance_analysis_validation.md (pre-redaction table) | Withhold pending permission | Actual financial comparison and recovery-event values are now withheld. Exact original is locally archived; current file is a methodology/private-verification summary. Historical exposure remains. |
| reports/risk_analysis_validation.md (pre-redaction table) | Withhold pending permission | Actual risk/rolling values, empirical tail counts and rolling-output totals are now withheld. Exact original is locally archived; methodology and private-validation procedure remain. |
| docs/benchmark_sources.md (pre-redaction comparison) | Withhold numerical comparison section pending permission | Numerical benchmark comparison values are now withheld after archival. Identity and unresolved alignment narrative remain. Historical comparisons still require rights review. |
| docs/cash_benchmark_validation.md (pre-redaction samples/comparison) | Withhold DWS-derived numerical comparison pending permission | Numerical benchmark comparison and ECB diagnostic rates are now withheld after archival. ECB reuse/attribution remains separate; DWS rights are not imputed to ECB observations. |
| docs/powerbi_build_guide.md (pre-redaction reference paragraph) | Withhold numerical reference paragraph pending permission | Actual KPI reference values and empirical tail counts are now withheld after archival. Non-numerical SQL comparison instructions remain; detailed references are local. |
| reports/powerbi_validation.md | Suitable current non-numerical evidence; history requires review | Batch 1 removed its earlier numerical KPI table. User completion/manual review is separated from independent SQL checks. The earlier numerical report still exists in HEAD/public history. |
| docs/source_register.md, docs/fund_candidates.md | Requires clarification | URLs, public issuer identities, metadata, source coverage, checksums and access/licensing observations. They are not open-data permission grants; provider metadata/document reproduction scope still needs review. |
| docs/calendar_gap_register.csv and reports/calendar_completeness.md | Public template/methodology; populated records withheld locally | Header-only public schema; detailed observed omissions and classifications preserved in ignored local evidence. |
| reports/full_history_quality.md, reports/phase0_sample_quality.md, reports/database_load_validation.md | Requires clarification | Coverage/quality/lineage metadata, local repository-relative input paths and checksums; not price series. Separate original test evidence from source-derived coverage metadata. Historical status claims also remain in these dated records. |
| docs/project_plan.md | Suitable as original planning, with context | Design intentions, source references and deferred ML options; not evidence that planned ML or production infrastructure exists. README states actual delivery. |

The file entries identify original result-bearing sections; Batch 4A replaced those numerical sections while preserving exact originals locally. This inventory identifies content, not a conclusion that every numeric fact is restricted or every non-numeric field is freely licensed.

## Local artifacts and credential protections

Real .env/.env.owner/.env.app, raw/interim/processed data, the virtual environment and powerbi/Investment_Fund_Analytics.pbix are ignored. Data-directory exceptions are empty .gitkeep files only. PBIX contents were not inspected; importing a series can embed it even if a visual hides it. Before any separately authorized PBIX release, inspect imported/hidden tables, queries, local paths and connection metadata without exposing secrets.

The ignore rules now additionally cover database dumps/backups, compressed SQL dumps, embedded database files and private certificate containers outside data/. Plain .sql remains versionable because project SQL is source code: a plain-text database export with a .sql suffix must stay under an ignored local data directory and be manually checked before staging. Screenshots/PDFs in reports/ are ignored by its allowlist; screenshots elsewhere may not be ignored. Keep previews local and review the staging list explicitly. Ignore rules do not remove files already tracked and do not clean old commits.

## Confirmed restrictions and unanswered questions

The recorded DWS source status is local_use_status unresolved and redistribution_status restricted. The [DWS German-locale terms, section 5.1](https://etf.dws.com/de-de/footer/nutzungsbedingungen/) restrict copying/downloading/distribution absent written consent, subject to legal exceptions. More specific terms may take precedence. The [equity product page](https://etf.dws.com/en/LU0380865021-euro-stoxx-50-ucits-etf-1c/) specifically prohibits further dissemination of its STOXX/Qontigo information. The [bond page](https://etf.dws.com/en/LU0290355717-eurozone-government-bond-ucits-etf-1c/) identifies licensed iBoxx information; DWS's license is not evidence that this project received redistribution rights. See [source register](source_register.md).

Outstanding external questions:

1. What permission or applicable exception covers local acquisition/analysis and the intended public portfolio use?
2. Does that basis cover aggregate derived fund statistics, NAV-based charts, recovery results, screenshots/PDFs or embedded PBIX data, and under what attribution/retention conditions?
3. What separate benchmark-owner permission applies to issuer-displayed/export-derived index comparisons?
4. What ECB reuse/attribution terms apply to the diagnostic rate samples? Free access alone is not an all-content licensing conclusion.
5. Which source/coverage/calendar metadata can be retained in a public methods-only release?

No legal exception, consent, fair-use entitlement or public-data license has been assumed. No request was sent to a provider. An original-code license is not yet present; choosing one is a separate user decision and must exclude third-party data rights.

## Batch 4A completed and remaining decisions

Exact-byte archival and targeted financial-result redaction are complete; see [the explicit category comparison](publication_redactions.md). The archive is local and ignored, and source/analytics inputs remain unchanged. Current numerical reports are now non-numerical methodology/private-validation summaries; no replacement financial demonstration was created.

Source/coverage/calendar metadata and ECB reuse still need clarification, and historical numerical content remains exposed. Raw/processed data, PBIX and actual-data previews remain withheld. This is a reduced-exposure working-tree candidate, not a legally cleared release. Review these open categories and any response to existing public history separately before staging or publication approval. No source permission, history remediation or public release was performed.

## Existing Git history

Initial commit 918acfa823f75e8c131b6a48bb83e4480e64c759 was previously pushed and contains numerical reports, benchmark comparisons and the earlier numerical Power BI validation table. Subsequent working-copy documentation corrections are still uncommitted. Removing numbers in a future ordinary commit would improve the latest tree but would not erase that original commit, copies or caches.

No history rewrite, force push, removal, deletion or account/repository visibility change is authorized here. Determine the appropriate rights/remediation response separately before describing the entire public repository history as safe. Neither an allowlist nor .gitignore retroactively removes published content.

## Portfolio recommendation

Use the original code, SQL, methodology, test-isolation evidence, architecture diagram and non-numerical descriptions of the five completed dashboard pages as the portfolio core. Highlight reproducible data acquisition boundaries, lineage, idempotent conflict-safe loading and SQL/Python reconciliation for AI/data-science/analytics/financial-data engineering roles. No predictive ML, benchmark outperformance, investment recommendation or production deployment is implemented or claimed.

An architecture diagram adds useful context without reproducing financial observations; README now includes one. A synthetic demo could later illustrate interactions independently of restricted observations, but no new synthetic financial data or simulated screenshot has been created or approved. Screenshots with actual data are not automatically safer than embedded datasets and remain permission-gated. User-completed Desktop review and independent SQL checks remain separate from direct PBIX inspection.

## Calendar separation and empirical metadata withholding

The public docs/calendar_gap_register.csv is now a six-column header-only template. Its exact populated original is preserved at data/interim/calendar/calendar_gap_register.csv, Git-ignored and checksum-verified. Runtime readers require this local register and the local quality summary; they never fall back to the public template. Classification rules and financial formulas are unchanged.

Detailed empirical coverage/count tables and observation-level omissions are withheld from public summaries pending permission. Earlier statements in this dated review that these records remain public describe the pre-separation checkpoint and are superseded here. Ordinary fund identities, source links, original provenance/checksums, chosen windows, code, methodology and deterministic fixtures remain public. Local numerical reports and archived originals remain private. Removing current records does not erase historical Git exposure or grant permission.

Historical exposure now also includes the formerly populated docs/calendar_gap_register.csv and detailed coverage/count/omission sections in the source, quality and analytics documentation. A future replacement must exclude those original blobs as well as the previously identified financial-result reports. The earlier rehearsal is stale after this batch and must be rebuilt and revalidated; no Git operation is authorized or performed by these edits.

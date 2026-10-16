# Source register — Phases 0–2

## Current implementation status

Documentation clarified 16 October 2026. The local PostgreSQL database is installed and loaded, performance and controlled NAV-risk analytics are implemented and independently checked, and twelve presentation views support the five Power BI pages completed/manually reviewed by the user. This does not establish direct PBIX inspection. See [README](../README.md), [database evidence](../reports/database_load_validation.md), [dashboard evidence](../reports/powerbi_validation.md) and [testing evidence](testing_validation.md). Source publication permission remains unresolved and redistribution restricted; no financial result or new permission is asserted here.

Earlier source-access/acquisition checkpoints below preserve what was known at those stages; their not-detected/not-loaded statements do not describe the current implementation.


## Cash feasibility and controlled-risk update

The restricted calendar methodology is now approved for six NAV-only risk metrics; results are in [risk validation](../reports/risk_analysis_validation.md). Benchmark eligibility remains unchanged. Separate ECB probes verified no-authentication CSV access to EST.B.EU000A2X2A25.WT in bounded endpoint probes for the controlled window, with annual percentage units. These samples remain local, are not database-loaded and do not establish full history/alignment. EST.B.EU000A2QQF08.CI returned HTTP 500 during the bounded probe. Exact methods, observed values, official publication references and outstanding validation are in [cash/benchmark investigation](cash_benchmark_validation.md).

## Current benchmark-stage status — 7 October 2026

The earlier setup/loading statements below are historical. Existing official DWS exports supply Index Level values for EURO STOXX 50 EUR Net Return (SX5T, EU0009658152) and iBoxx Euro Sovereigns Eurozone Total Return (internal identity, external identifier not verified). No new acquisition was required; exact request URLs, original acquisition times and checksums below remain authoritative.

These are issuer-exported benchmark levels, not market prices or a separately adjusted-close series. Benchmark instruments and assignments are loaded idempotently with original source lineage, but every index value is flagged pending date/basis verification. Equity export-based period returns differ from issuer-displayed benchmark returns; no date shift or replacement was applied. Public backend access requires no authentication in the verified acquisition, but provides no stability guarantee or established redistribution permission. Raw and processed data remain local and Git-ignored. See [benchmark sources](benchmark_sources.md) for exact identifiers, basis evidence, discrepancies, database IDs and access limitations; [risk validation](../reports/risk_analysis_validation.md) records current gates.

<a id="phase-2-full-acquisition--current-verified-status"></a>

## Phase 2 acquisition checkpoint (historical)

The issuer's calendar definitions and historical holiday evidence explain the pattern without inventing NAV dates; the unresolved historical omission and historical effective-date exceptions remain open. At that historical calendar/acquisition checkpoint, PostgreSQL had not been detected and no loading had occurred. This records the earlier observation, not the current state; subsequent loading is documented in [database validation](../reports/database_load_validation.md).

On 7 October 2026, two official, date-bounded DWS XLSX downloads returned HTTP 200 without authentication, API key, subscription, or payment. This supersedes the sample-only coverage statements below; those are retained as Phase 0 evidence.

| Source | Instrument | Exact final request | Retrieved UTC | Bytes | SHA-256 |
| --- | --- | --- | --- | ---: | --- |
| S01 | LU0380865021 | [Official equity XLSX](https://etf.dws.com/api/pdp/de-de/etf/LU0380865021/historicaldata/download?startDate=2021-09-30&endDate=2026-09-30&includeTax=false) | 2026-10-07T10:51:53.233877+00:00 | 60,409 | `85df2592c833be953b57085bea414629753e81eddbeef70ea3c08a82e780ec82` |
| S06 | LU0290355717 | [Official bond XLSX](https://etf.dws.com/api/pdp/de-de/etf/LU0290355717/historicaldata/download?startDate=2021-09-30&endDate=2026-09-30&includeTax=false) | 2026-10-07T10:51:45.341035+00:00 | 61,631 | `857c751eb339aa2fafe2aaa289d7f1ec5b159b9395253ddcab313de2f0906f13` |

Method: `requests` HTTP GET with `startDate`, `endDate`, and `includeTax=false`; one five-year export per instrument, timeout and XLSX-response checks, timestamped immutable raw filenames, and SHA-256 manifest. Raw files and manifest are under `data/raw/full_history/20261007T105130116510Z/`, excluded from Git. The existing sample parser handles both files. Consolidated local datasets and audit artifacts are under `data/processed/full_history/`, also Git-ignored.

These are NAV per share, not exchange prices. Both workbook currencies are EUR. No separately adjusted NAV series or split adjustment guarantee has been established; `includeTax` is not an adjustment flag. No exchange ticker or currency conversion is used.

Each instrument's 15 earlier sample observations match its full export exactly. Consolidation explicitly removes 15 identical extra rows per instrument, retaining source references. There are no within-export duplicate dates, conflicting NAVs, invalid dates, missing/non-positive/nonfinite NAVs, unexpected currencies, out-of-window observations, or changes above the 20% review threshold. Source dates descend; validated dates ascend.

A historical fund valuation calendar has not been reconciled: these are review candidates, not confirmed missing valuations or proven holidays. No observations were filled. See [full quality report](../reports/full_history_quality.md) for all dates, auxiliary missing cells, reproduction, and loading readiness.

**Practical recommendation:** retain these official exports as the primary source; no fallback is needed for this acquisition. Both validated NAV datasets are ready for database loading with their lineage and calendar-gap register. Resolve historical valuation-calendar completeness before daily analytics. Access remains a public website backend without a documented supported API or service guarantee. The existing DWS/third-party reuse restrictions below remain in force; no redistribution permission has been established and downloaded workbooks/data are not published. No database loading or financial calculations were performed during that acquisition checkpoint. Both were subsequently implemented; see the current implementation status above.

## Phase 0 access evidence (historical)

Review date: 7 October 2026. Scope: public metadata, source-access inspection, and bounded daily NAV samples only. See [fund candidates](fund_candidates.md) for the instrument definitions and [approved plan](project_plan.md) for the intended methodology. The verified E01/B01 findings below supersede the initial reconnaissance statuses for S01 and S06.

## Verified findings for the two test instruments

**Recommendation: use the official DWS dated XLSX NAV export for both instruments.** Six bounded requests succeeded with HTTP 200 and genuine Excel workbooks: one week in October 2021, one in October 2023, and one in September 2026 for each fund. Each contained five daily observations, giving 15 observations per instrument and 30 in total. No subscription, login, API key, or payment was needed. No full history was requested.

Technical access to observations five years apart is verified. A usable five-year daily series is strongly supported by these samples, but uninterrupted coverage and corporate-action consistency between the sampled windows remain to be checked during a later authorized full acquisition. Do not confuse the span of these samples with a completeness audit.

| Field | Equity — E01 | Bond — B01 |
| --- | --- | --- |
| Fund / ISIN | Xtrackers Euro Stoxx 50 UCITS ETF 1C / LU0380865021 | Xtrackers II Eurozone Government Bond UCITS ETF 1C / LU0290355717 |
| Official page checked first | [DWS product page](https://etf.dws.com/de-de/LU0380865021-euro-stoxx-50-ucits-etf-1c/) | [DWS product page](https://etf.dws.com/de-de/LU0290355717-eurozone-government-bond-ucits-etf-1c/) |
| Exact tested export | [2021 bounded XLSX request](https://etf.dws.com/api/pdp/de-de/etf/LU0380865021/historicaldata/download?startDate=2021-10-01&endDate=2021-10-07&includeTax=false) | [2021 bounded XLSX request](https://etf.dws.com/api/pdp/de-de/etf/LU0290355717/historicaldata/download?startDate=2021-10-01&endDate=2021-10-07&includeTax=false) |
| Value basis | Official NAV per share; not exchange closing price | Official NAV per share; not exchange closing price |
| Adjustment status | Native reported NAV; no separate adjusted-NAV field or documented split-adjustment flag in the export. Accumulating income remains within the class. Do not label this vendor-adjusted close | Same: native reported accumulating-class NAV, with no separately verified split-adjusted series |
| Verified observation windows | 1–7 October 2021; 2–6 October 2023; 24–30 September 2026, five rows in each | Same three windows, five rows in each |
| Verified historical reach | 1 October 2021 to 30 September 2026, sampled only; absolute earliest/latest availability not tested | Same sampled span; absolute earliest/latest availability not tested |
| Currency | EUR explicitly recorded in workbook | EUR explicitly recorded in workbook |
| Format / method | HTTP GET to date-bounded XLSX route used by the public frontend | Same |
| Authentication | No login, API key or account cookie supplied. The 2023/2026 checks worked without the frontend identification header | Same |
| Cost | No payment/subscription required for tested requests | Same |
| Redistribution | No affirmative permission found. DWS terms restrict downloading/reproduction/distribution without consent except as legally permitted; STOXX-related information has an additional distribution restriction | No affirmative permission found; DWS terms apply and exported benchmark data also involves third-party rights |
| Access limitations | Public website backend, not a documented supported developer API. URL/format/service availability can change. Locale terms may apply; no rate limit or maximum request range established | Same |

### How the official access method was verified

The rendered product pages expose Historical Data navigation. A direct page request returns a JavaScript application shell; scraping its HTML alone does not yield daily history. Inspection of the public frontend identified a date picker, XLSX download handling, and the same dated backend route used by the page.

Observed on this review date:

- [Public application bundle](https://etf.dws.com/_passive-nuxt/ZBmxg8YN.js): date-range component and URL construction.
- [Product-page module](https://etf.dws.com/_passive-nuxt/B60xWFRA.js): names the output `HistoricalData-{ISIN}.xlsx`.
- [Public request wrapper](https://etf.dws.com/_passive-nuxt/1CBXQxdY.js): historical download uses `startDate`, `endDate`, and `includeTax`.

These versioned JavaScript names are inspection evidence, not stable dependencies. The observed backend request pattern is:

```text
https://etf.dws.com/api/pdp/de-de/etf/{ISIN}/historicaldata/download
    ?startDate=YYYY-MM-DD&endDate=YYYY-MM-DD&includeTax=false
```

`includeTax=false` is the frontend's tax-data option, not a price-adjustment option. Its full tax semantics have not been established; use the explicitly labelled NAV column and do not interpret this switch as adjusted/unadjusted performance. Initial 2021 requests included the public `client-id: passive-frontend` header, which is a frontend identifier rather than a credential; subsequent requests succeeded without it. No authentication controls were bypassed.

Workbook structure verified: identity block containing fund name, ISIN, currency and export as-of date; followed by Date, Asset Under Management, NAV, Index Level, and Interim Profits columns. Dates are descending and formatted `DD.MM.YYYY`; values are numeric cells. All 30 NAV values were positive, all sampled dates unique, and observed dates remained inside requested bounds. Interim Profits values were N/A in these samples. The export as-of date is 7 October 2026 and is not the historical observation date.

Accumulating NAV is a preferable starting point to ETF market prices because it retains reinvested income in the fund rather than introducing exchange premiums/discounts. Still check share splits, class changes, and valuation conventions before calculating returns. A NAV column is not automatically a corporate-action-adjusted total-return index. No return or risk metric was calculated here.

### Small-sample acquisition evidence

Samples are preserved locally in `data/raw/phase0/` and excluded by existing Git ignore rules. They are the original downloaded workbooks, not cleaned outputs. File timestamps below record completion of retrieval in UTC on 7 October 2026 (add two hours for Europe/Paris). The server content type was `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`; its filename was `HistoricalData-{ISIN}.xlsx`.

For the two later windows, the same exact endpoint was used with `startDate=2023-10-02&endDate=2023-10-06&includeTax=false` and `startDate=2026-09-24&endDate=2026-09-30&includeTax=false` respectively.

| Local raw filename | Retrieval completed (UTC) | Requested / observed dates | Rows | Bytes | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| LU0380865021_2021_sample.xlsx | 10:22:50 | 2021-10-01–2021-10-07 / same endpoints | 5 | 6,983 | `77f6d66419f31b391a84e7740ce33d83843c6ad7b046d5eb1a016e8d175bc959` |
| LU0380865021_2023_sample.xlsx | 10:23:41 | 2023-10-02–2023-10-06 / same endpoints | 5 | 6,978 | `28ddccf36b4815e38240a46915ddd0b90fc98dde96441c0340ff48de0322e96b` |
| LU0380865021_2026_sample.xlsx | 10:23:42 | 2026-09-24–2026-09-30 / same endpoints | 5 | 6,974 | `c3e7740534d7190a483df5768ffde913affc503904e30979d0020a80be11df11` |
| LU0290355717_2021_sample.xlsx | 10:22:52 | 2021-10-01–2021-10-07 / same endpoints | 5 | 7,088 | `50ff6ab4e78b42cf6b27d33e39be25b29dd8e010a1eaefa6d14ce9b85c5d1729` |
| LU0290355717_2023_sample.xlsx | 10:23:44 | 2023-10-02–2023-10-06 / same endpoints | 5 | 7,098 | `7bd108a2958a6a73937d900079bcb936e89206cbefda23a4bcdc9b7355f14733` |
| LU0290355717_2026_sample.xlsx | 10:23:45 | 2026-09-24–2026-09-30 / same endpoints | 5 | 7,090 | `d417c343df6fe0ec76c0fcd13098dffd45f9cdde82aab423cb2f4dcbeb81cd9e` |

### Terms and practical recommendation

[DWS German-locale terms, section 5.1](https://etf.dws.com/de-de/footer/nutzungsbedingungen/) restrict downloading, copying and distributing site material absent written consent except where legally permitted. The availability of a public download control does not establish an open-data license. The equity export also includes a restriction on further dissemination of STOXX/Qontigo-related information. These are observed provider restrictions, not a legal determination about applicable exceptions.

Use **DWS native NAV XLSX as the preferred technical source**, with a manual dated download as an operational backup to the backend route. Resolve the applicable permission basis for intended local analysis and eventual publication before full acquisition or release. Do not publish the workbooks or bundled benchmark columns based on technical accessibility alone. Permission to publish derived tables, charts or dashboard exports also remains to be established.

There is no need to replace these exact instruments or move to market prices on technical-access grounds. The next authorized acquisition can target 1 October 2021–30 September 2026 with the preceding valuation for the first return, followed by calendar completeness and corporate-action validation. This review does not authorize that acquisition or an ingestion pipeline.

### Fallback assessment

Official daily exports succeeded, so the condition requiring a replacement source was not triggered. A limited fallback screen was nevertheless made to avoid recommending an assumed free CSV route:

| Alternative | Candidate mapping / basis | Verified access finding | Decision |
| --- | --- | --- | --- |
| Yahoo Finance | XESC.DE / XGLE.DE are proposed German listing symbols, EUR market prices; adjusted-close availability for these instruments not verified | [Yahoo's own help](https://help.yahoo.com/kb/finance-for-web/download-historical-data-yahoo-finance-sln2311.html) says browser CSV download requires Gold. History pages were inaccessible through the web tool here; that is not evidence the instruments lack history | Not the default no-cost source. No chart API or third-party wrapper was tested; stability, usage terms and 3–5-year coverage remain unverified |
| Stooq | Proposed xesc.de / xgle.de market-price mappings, not verified | Instrument history pages could not be read through the web tool. No instrument-specific adjusted series, currency, authenticated download method or coverage established | Unverified lead only; do not assume free usable CSV data or no authentication |

No fallback has demonstrated a stronger combination of exact share-class identity, NAV semantics, no-cost access and historical reach than the tested official route. If future access or permission fails, reopen source selection rather than silently adopting an unofficial API.

## Status definitions and provenance

- **Reviewed:** public issuer page was inspected through web search/open; metadata and displayed performance were observed.
- **Provisional history:** a historical-data navigation item, performance display, or download lead exists; no daily-history export has been exercised.
- **Untested supporting source:** documented data service is a proposed later input, not acquired data.
- **Verified technical access:** bounded daily files returned successfully, with old and recent observations checked. S01 and S06 have this status; continuous full-window coverage and permission clearance remain separate checks.
- **Confirmed usable history:** reserved for validated complete history and a resolved permission basis; no source currently has this status.

The review date is the access-review date, not a valuation date. The six bounded S01/S06 acquisitions are recorded above. Other sources have no acquired files or checksums. At that Phase 0 access-review checkpoint, no database records existed; this does not describe the subsequently loaded project database. History bounds must not be inferred from inception dates alone.

## Instrument source entries

All entries below are official issuer sources, reviewed on 7 October 2026. Public page access does not establish unrestricted automated access or bulk-download rights. Daily frequency was verified in bounded samples for S01/S06 only. Use ISIN when changing site locale or selecting a share class.

| Source ID / candidate | Provider and canonical product URL | Intended data and observed evidence | Likely method / format | Free history assessment and unresolved access |
| --- | --- | --- | --- | --- |
| S01 / E01 / LU0380865021 | [DWS — Euro Stoxx 50 1C](https://etf.dws.com/en/LU0380865021-euro-stoxx-50-ucits-etf-1c/) | EUR capitalizing class; bounded daily NAV samples in 2021, 2023 and 2026 | Official date-bounded XLSX GET; exact method verified above | Verified technical access at no cost. Full-window completeness and intended-use permission remain open |
| S02 / E02 / LU0274209237 | [DWS — MSCI Europe 1C](https://etf.dws.com/en/LU0274209237-msci-europe-ucits-etf-1c/) | USD class/NAV, capitalizing; 2007 launch; historical performance and navigation | Official NAV/history route; format unverified | Provisional history. Separate USD NAV from EUR listing prices |
| S03 / E03 / IE00B4L5Y983 | [iShares — Core MSCI World](https://www.ishares.com/de/privatanleger/de/produkte/251882/ishares-msci-world-ucits-etf-acc-fund) | Ireland, USD accumulating, 2009 inception; performance and Download lead | Official NAV/pricing download if available; inspect whether CSV/XLSX output is NAV or holdings | Provisional history. General download link is not evidence of daily historical NAV export |
| S04 / E04 / IE00B5BMR087 | [iShares — Core S&P 500](https://www.ishares.com/de/privatanleger/de/produkte/253743/ishares-core-s-p-500-ucits-etf) | USD NAV, SXR8 listing, 19 May 2010 class inception and historical performance | Official NAV/pricing route if supported; format unverified | Provisional history. Confirm adjustment basis and benchmark return variant |
| S05 / E05 / IE00B4L5YC18 | [iShares — MSCI EM](https://www.ishares.com/de/privatanleger/de/produkte/251858/ishares-msci-emerging-markets-ucits-etf-acc-fund) | Ireland, USD accumulating, 2009 launch; net MSCI EM benchmark | Official NAV/pricing route if supported; format unverified | Provisional history. Check calendar, currency and history depth |
| S06 / B01 / LU0290355717 | [DWS — Eurozone Government Bond 1C](https://etf.dws.com/en/LU0290355717-eurozone-government-bond-ucits-etf-1c/) | EUR capitalizing; bounded daily NAV samples in 2021, 2023 and 2026 | Official date-bounded XLSX GET; exact method verified above | Verified technical access at no cost. Full-window completeness and intended-use permission remain open |
| S07 / B02 / LU0478205379 | [DWS — EUR Corporate Bond 1C](https://etf.dws.com/en/LU0478205379-eur-corporate-bond-ucits-etf-1c/) | EUR capitalizing, 2010 launch; benchmark-change notice | Official NAV/history route; format unverified | Provisional history. Date-dependent benchmark assignment required |
| S08 / B03 / IE00BDBRDM35 | [iShares — Core Global Aggregate EUR Hedged](https://www.ishares.com/uk/individual/en/products/291770/ishares-core-global-aggregate-bond-ucits-etf) | Ireland, EUR hedged accumulating, 2017 class launch; USD fund base and named aggregate index | Official NAV/pricing route if supported; format unverified | Provisional history. Confirm hedged benchmark series and relevant listing-line delisting notice |
| S09 / B04 / IE00BF11F565 | [iShares — Core EUR Corporate Acc](https://www.ishares.com/uk/individual/en/products/290619/ishares-core-corp-bond-ucits-etf-eur-acc-fund) | Ireland, EUR accumulating; 2017 class inception versus 2009 fund launch | Official NAV/pricing route if supported; format unverified | Provisional history. Never use another share class's earlier history |
| S10 / C01 / LU0290358497 | [DWS — EUR Overnight Rate Swap 1C](https://etf.dws.com/en/LU0290358497-eur-overnight-rate-swap-ucits-etf-1c/) | EUR capitalizing, 2007 launch; current €STR +8.5bp target; 2023 benchmark change | Official NAV/history route; format unverified | Provisional history. Optional cash-like comparator; synthetic exposure and benchmark discontinuity |

## Supporting identity and listing evidence

| Evidence ID | Source | Purpose / limitation |
| --- | --- | --- |
| M01 | [DWS ETF FAQ](https://etf.dws.com/en-gb/knowledge/faq-etfs/) | Explains Xtrackers Euro Stoxx 50 Luxembourg domicile and why venue/currency exposure differ |
| M02 | [DWS MSCI Europe factsheet](https://etf.dws.com/download/asset/9851b59e-0dd9-4624-9a83-9f580e0a60a3) | Listing example XMEU/Xetra in EUR; recheck document date before final mapping |
| M03 | [DWS sovereign factsheet](https://etf.dws.com/en-lu/AssetDownload/Index/c20c6b6d-d1d1-4b23-85a3-7b472b341115/LU0290355717-LUB-FS-EN-2020-12-31.pdf) | Historical official evidence of Luxembourg domicile; not current fee evidence |
| M04 | [DWS corporate factsheet](https://etf.dws.com/en-lu/AssetDownload/Index/de822568-70bf-4c56-a1c7-b1a8d5a3d3c4/Factsheet.pdf) | Luxembourg domicile and corporate-bond identity; historical document |
| M05 | [DWS overnight factsheet](https://etf.dws.com/download/asset/9a8343c9-e855-4f02-b06d-eeedca84a42f) | Luxembourg domicile, EUR class and synthetic replication |
| M06 | [DWS fee-change announcement](https://etf.dws.com/en-lu/about-us/press-releases/dws-reduces-fees-for-five-xtrackers-etfs/) | ISIN-to-XGLE/XBLC ticker leads; venue and quote currency need separate verification |
| M07 | [DWS London sovereign listing page](https://etf.dws.com/en-gb/LU0290355717-eurozone-government-bond-ucits-etf-1c/) | XGLE LN listing identifier; do not infer quote currency from class currency |
| M09 | [DWS German sovereign page](https://etf.dws.com/de-de/LU0290355717-eurozone-government-bond-ucits-etf-1c/) and [corporate page](https://etf.dws.com/de-de/LU0478205379-eur-corporate-bond-ucits-etf-1c/) | XGLE GY and XBLC GY German listing identifiers; quote currency to verify |
| M08 | [Exchange overnight listing](https://live.euronext.com/it/product/etfs/LU0290358497-ETFP/company-information) | XEON ETFplus listing lead; exchange data is market-price evidence, not NAV |

Current factsheets/KIDs/prospectuses must be retained as references when the universe is fixed. Do not infer domicile solely from the ISIN prefix or from the provider's headquarters. E02's Luxembourg domicile is also corroborated by the [candidate profile](https://www.justetf.com/en/etf-profile.html?isin=LU0274209237); this secondary source supports discovery, while current issuer legal documentation remains the final check.

## Supporting analytical sources and fallbacks

| Source ID | Provider / reference | Intended use and access lead | Status / limits |
| --- | --- | --- | --- |
| S11 | [ECB FX reference rates](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html) and [SDMX API examples](https://data.ecb.europa.eu/help/api/data-examples) | Official EUR FX reference observations; documented API/download route | Untested supporting source. Confirm series key, units, dates, use terms and quote direction; reference rates are not dealing prices |
| S12 | [ECB €STR dataset](https://data.ecb.europa.eu/data/datasets/EST) and [web services](https://data.ecb.europa.eu/help/getting-data-web-services-sdmx-0) | EUR cash-rate proxy via documented statistical service | Untested supporting source. Capture reference/publication dates, annual-rate units and day count; do not use future publications |
| S13 | [Vienna Exchange MSCI Europe history](https://www.wienerborse.at/en/market-data/exchange-traded-funds/historical-data/?ID_NOTATION=200476255&ISIN=LU0274209237) | Example public market-price historical page for E02 | Fallback lead only. Range/export rights and trading liquidity unverified; listing differs from Xetra and cannot be silently substituted |
| S14 | [Alpha Vantage documentation](https://www.alphavantage.co/documentation/) | Candidate alternative market-data API | Not selected. Daily adjusted endpoint is labelled premium; do not assume no-cost adjusted UCITS history or coverage |
| S15 | Official STOXX/MSCI/iBoxx/Bloomberg index history, reached through product references | Fund-specific benchmark data | Unresolved. Knowing an index name or seeing annual issuer performance does not establish free daily index access. Use a documented comparable proxy only if official history is unavailable |

No third-party API, paid subscription, or scraping workaround is selected. The tested DWS endpoint is the official site's public frontend backend, without a developer support guarantee. A market-price fallback must establish venue, currency, adjustment basis and accessible range and must be labelled separately from NAV analysis.

## Terms and acquisition policy

**DWS terms were reviewed; permission clearance remains unresolved.** Restrictions and exact references are recorded above. No open license or redistribution right has been established for issuer or exchange histories. Terms review for other sources remains incomplete. Keep raw data out of Git. Public access, free price, local use and permission to redistribute are separate questions.

The S01/S06 bounded acquisition records are populated above. For each future sample or full acquisition, append:

| Field | Required record |
| --- | --- |
| Source and instrument | Source ID, ISIN, selected class, value type; ticker/venue only if market prices |
| Retrieval | Exact timestamp with timezone, official export URL or manual steps, locale and parameters |
| Coverage | Requested and observed start/end, frequency, calendar, first/last observation, row count |
| File identity | Original filename, local raw path, bytes, SHA-256 checksum, format/encoding |
| Semantics | Currency, units, NAV/price/total-return basis, adjustments, distribution convention |
| Permissions | Terms/license URL and review date; local use, automation and redistribution outcomes separately |
| Quality/status | Duplicates, gaps, unusual values, reconciliation to issuer display, pass/fail and unresolved issues |

## First test record and Phase 0 exit status

| Instrument | Metadata review | Daily sample | 3–5-year daily range | Local-use terms | Decision |
| --- | --- | --- | --- | --- | --- |
| E01 / LU0380865021 | Reviewed; EUR accumulating equity, Luxembourg | Three five-row daily NAV samples | Five-year historical reach verified; continuous coverage not audited | Restrictions reviewed; permission basis unresolved | Preferred technical source: official dated XLSX |
| B01 / LU0290355717 | Reviewed; EUR accumulating sovereign bond, Luxembourg | Three five-row daily NAV samples | Five-year historical reach verified; continuous coverage not audited | Restrictions reviewed; permission basis unresolved | Preferred technical source: official dated XLSX |

The requested bounded access verification is complete. Resolve the permission basis and, when authorized, validate full-window calendars and corporate actions. At that bounded Phase 0 access-verification checkpoint, no returns, risk calculations, database build, dashboard or ML work had been performed. Later implementation is documented above; ML remains unimplemented.

Phase 0 now has verified no-cost daily NAV access for both test instruments. The full gate remains **open** because intended-use permissions, continuous coverage validation and the final universe are not yet resolved. Technical access alone does not establish publication rights.

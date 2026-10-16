# Fund candidates — Phase 0

Review date: 7 October 2026. Related documents: [project plan](project_plan.md) and [source register](source_register.md).

## Scope and evidence status

Propose 10 accumulating UCITS ETFs: five equity, four bond, and one optional overnight-rate comparator. Five are Luxembourg-domiciled and five Irish-domiciled. Six have EUR share-class currency; four have USD share-class currency and can be analysed in EUR later with documented FX conversion. These are research candidates, not investment recommendations or an approved final universe.

Issuer metadata and public performance pages were reviewed. No historical files were downloaded and no daily-history completeness has been verified. Launch dates establish potential history, not proof of accessible daily observations. All candidates are older than five years, but retention in the project depends on confirming at least three years of usable history.

**Access status P:** public historical performance is visible without payment; a complete 3–5-year daily NAV export has not been tested. P does not mean confirmed free bulk data or permission to redistribute. Historical Data navigation on DWS pages and general Download links on iShares pages are leads, not verified daily endpoints.

Tickers below are listing examples, not universal identifiers or API symbols. ISIN identifies the share class; ticker, exchange, listing currency, and vendor symbol must be mapped separately before acquiring market prices. Domicile is the legal fund location, independent of where its shares trade. Unhedged means no dedicated share-class currency hedge; it does not mean EUR denomination removes foreign economic exposure.

## Candidate metadata

| ID | Fund name / share class | ISIN | Ticker example / venue | Issuer / legal umbrella | Domicile | Category | Income | Share-class currency | Currency hedging | Benchmark |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E01 | Xtrackers Euro Stoxx 50 UCITS ETF 1C | LU0380865021 | XESC / Xetra (EUR) | DWS / Xtrackers | Luxembourg | Equity — eurozone large cap | Accumulating | EUR | Unhedged | EURO STOXX 50, net total return, EUR |
| E02 | Xtrackers MSCI Europe UCITS ETF 1C | LU0274209237 | XMEU / Xetra (EUR) | DWS / Xtrackers | Luxembourg | Equity — developed Europe | Accumulating | USD | Unhedged | MSCI Europe, net total return |
| E03 | iShares Core MSCI World UCITS ETF USD (Acc) | IE00B4L5Y983 | EUNL / Xetra (EUR) | BlackRock / iShares III plc | Ireland | Equity — developed global markets | Accumulating | USD | Unhedged | MSCI World Index (Net) |
| E04 | iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | SXR8 / Xetra (EUR) | BlackRock / iShares VII plc | Ireland | Equity — US large cap | Accumulating | USD | Unhedged | S&P 500; exact return variant to confirm in current factsheet |
| E05 | iShares MSCI EM UCITS ETF USD (Acc) | IE00B4L5YC18 | EUNM / Xetra (EUR) | BlackRock / iShares III plc | Ireland | Equity — emerging markets | Accumulating | USD | Unhedged | MSCI Emerging Markets Index (Net) |
| B01 | Xtrackers II Eurozone Government Bond UCITS ETF 1C | LU0290355717 | XGLE / Xetra (GY); listing currency to verify | DWS / Xtrackers II | Luxembourg | Bond — eurozone investment-grade sovereign | Accumulating | EUR | Unhedged; EUR-denominated target bonds | iBoxx Euro Sovereigns Eurozone Index |
| B02 | Xtrackers II EUR Corporate Bond UCITS ETF 1C | LU0478205379 | XBLC / Xetra (GY); listing currency to verify | DWS / Xtrackers II | Luxembourg | Bond — EUR investment-grade corporate | Accumulating | EUR | Unhedged; EUR-denominated target bonds | Bloomberg Euro Corporate Bond Index |
| B03 | iShares Core Global Aggregate Bond UCITS ETF EUR Hedged (Acc) | IE00BDBRDM35 | AGGH / issuer page label; venue mapping to verify | BlackRock / iShares III plc | Ireland | Bond — global investment-grade aggregate | Accumulating | EUR (fund base currency USD) | Hedged to EUR | Bloomberg Global Aggregate Bond Index; appropriate EUR-hedged comparison series must be confirmed |
| B04 | iShares Core € Corp Bond UCITS ETF EUR (Acc) | IE00BF11F565 | IEAA / London (LN); listing currency to verify | BlackRock / iShares III plc | Ireland | Bond — EUR investment-grade corporate | Accumulating | EUR | Unhedged; EUR-denominated target bonds | BBG Euro Corporate Index (EUR), issuer ticker LECPTREU |
| C01 | Xtrackers II EUR Overnight Rate Swap UCITS ETF 1C | LU0290358497 | XEON / ETFplus Milan (EUR) | DWS / Xtrackers II | Luxembourg | Cash-like — synthetic overnight-rate exposure | Accumulating | EUR | No separate currency hedge; EUR overnight-rate target | Solactive €STR +8.5 Daily Total Return Index |

Issuer/umbrella labels distinguish the commercial provider from the issuing entity; management-company names and current legal documents must be retained in final metadata. C01 is not a conventional bond fund or a risk-free cash deposit and should be excluded from ordinary bond peer rankings.

## History, sources, and limitations

Each source ID links to the corresponding entry in [source_register.md](source_register.md). Primary links support metadata; access statements describe observations made during this review, not successful acquisition.

| ID | Share-class history anchor | Likely historical source / free access | Instrument-specific uncertainty or limitation | Primary evidence |
| --- | --- | --- | --- | --- |
| E01 | 29 August 2008; sub-fund itself started in 2007 | S01: DWS Historical Data/NAV route; P | Verify daily export depth, locale requirements, NAV basis and any historical replication changes. Use share-class inception, not sub-fund inception. | [Issuer page](https://etf.dws.com/en/LU0380865021-euro-stoxx-50-ucits-etf-1c/); [DWS domicile explanation](https://etf.dws.com/en-gb/knowledge/faq-etfs/) |
| E02 | 10 January 2007 | S02: DWS Historical Data/NAV route; P | NAV currency is USD despite EUR trading lines. Historical replication/benchmark conventions require review; not a direct peer of eurozone-only E01. | [Issuer page](https://etf.dws.com/en/LU0274209237-msci-europe-ucits-etf-1c/); [issuer listing factsheet](https://etf.dws.com/download/asset/9851b59e-0dd9-4624-9a83-9f580e0a60a3) |
| E03 | 25 September 2009 | S03: iShares NAV/pricing export if available; P | EUR quotation does not make this a EUR share class or hedged fund. Establish daily NAV download separately from holdings exports. | [Issuer page](https://www.ishares.com/de/privatanleger/de/produkte/251882/ishares-msci-world-ucits-etf-acc-fund) |
| E04 | 19 May 2010; fund launched 18 May 2010 | S04: iShares NAV/pricing export if available; P | USD NAV and US-market exposure; confirm net/gross benchmark return variant and corporate-action treatment. | [Issuer page](https://www.ishares.com/de/privatanleger/de/produkte/253743/ishares-core-s-p-500-ucits-etf) |
| E05 | 25 September 2009 | S05: iShares NAV/pricing export if available; P | Emerging-market calendars and valuation timing differ; do not rank against developed-market funds as equivalent peers. | [Issuer page](https://www.ishares.com/de/privatanleger/de/produkte/251858/ishares-msci-emerging-markets-ucits-etf-acc-fund) |
| B01 | 22 May 2007 | S06: DWS Historical Data/NAV route; P | Daily depth and benchmark return variant still unverified. Physical sampling and interest-rate sensitivity differ from corporate credit funds. | [Issuer page](https://etf.dws.com/en/LU0290355717-eurozone-government-bond-ucits-etf-1c/); [issuer factsheet confirming domicile](https://etf.dws.com/en-lu/AssetDownload/Index/c20c6b6d-d1d1-4b23-85a3-7b472b341115/LU0290355717-LUB-FS-EN-2020-12-31.pdf) |
| B02 | 23 February 2010 | S07: DWS Historical Data/NAV route; P | Benchmark changed on 1 February 2017 from iBoxx liquid corporate 100 to Bloomberg Euro Corporate. Track assignment by date; listing quote currency remains to be verified. | [Issuer page](https://etf.dws.com/en/LU0478205379-eur-corporate-bond-ucits-etf-1c/); [issuer domicile factsheet](https://etf.dws.com/en-lu/AssetDownload/Index/de822568-70bf-4c56-a1c7-b1a8d5a3d3c4/Factsheet.pdf) |
| B03 | 21 November 2017 | S08: iShares NAV/pricing export if available; P | EUR-hedged class must not be compared to an unhedged USD benchmark. Issuer page flags a future listing-line delisting: identify the affected line before selecting a price source. | [Issuer page](https://www.ishares.com/uk/individual/en/products/291770/ishares-core-global-aggregate-bond-ucits-etf) |
| B04 | 21 September 2017; umbrella fund began in 2009 | S09: iShares NAV/pricing export if available; P | Do not borrow the older distributing class's history. Useful potential corporate-bond peer for B02 after index and calendar alignment. | [Issuer page](https://www.ishares.com/uk/individual/en/products/290619/ishares-core-corp-bond-ucits-etf-eur-acc-fund) |
| C01 | 25 May 2007 | S10: DWS Historical Data/NAV route; P | Synthetic swap exposure. Benchmark changed on 30 November 2023; current index adds 8.5 basis points to €STR. Not a substitute for the ECB cash rate in Sharpe calculations. | [Issuer page](https://etf.dws.com/en/LU0290358497-eur-overnight-rate-swap-ucits-etf-1c/); [issuer domicile factsheet](https://etf.dws.com/download/asset/9a8343c9-e855-4f02-b06d-eeedca84a42f) |

Historical factsheets are supporting identity/domicile evidence, not proof that current terms or benchmark methodology are unchanged. Recheck current documents before freezing the universe. No candidate has confirmed redistribution permission.

## First feasibility-test instruments

**Equity: E01 — Xtrackers Euro Stoxx 50 UCITS ETF 1C, LU0380865021.** Its EUR accumulating class, eurozone equity exposure, Luxembourg domicile, and 2008 class inception minimize the initial FX/distribution complications. The issuer exposes a Historical Data section and long-run performance, making it a sensible first NAV-access test.

**Bond: B01 — Xtrackers II Eurozone Government Bond UCITS ETF 1C, LU0290355717.** Its EUR accumulating class, EUR sovereign-bond exposure, Luxembourg domicile, and 2007 inception provide a contrasting asset class with similarly simple initial currency handling. The same provider permits comparison of source mechanics without building two ingestion approaches immediately.

These choices are based on metadata and plausible access, not a claim that daily data is already usable. Shared-provider dependency is a limitation; if DWS export access fails, use E03 and B04 as secondary issuer-access tests, documenting the extra USD conversion for E03. They are alternatives for feasibility, not identical investment exposures.

## Bounded next check and decision gate

Proposed common five-year window: 1 October 2021–30 September 2026, subject to source availability; the first valid return needs the preceding valuation. Inspect available start/end dates without downloading the entire series. Three years is the fallback minimum, not an automatic pass.

For E01 and B01, next inspect the official browser export control and terms. If a bounded export is supported and permitted, inspect at most one month (approximately 20–25 observations) per fund, plus visible history range metadata. Do not trigger an unbounded multi-year export merely to obtain a sample. This review has not acquired even those samples.

Record file format, column names, identifier, currency, NAV versus market price, return/adjustment basis, observation dates, and available history bounds. Confirm no payment is required, distinguish any locale/disclaimer acknowledgement from an account requirement, and document use/redistribution terms. Check one displayed NAV against a sample row and inspect duplicates, missing dates, and positive values without calculating performance.

Keep both instruments **provisional** until identity, bounded sample structure, accessible 3–5-year history, and permitted local use are evidenced. Public annual return tables alone cannot pass a daily-risk-data gate. Freeze the final 6–10 instruments only after this check; Phase 0 remains open until the data-feasibility evidence is complete.

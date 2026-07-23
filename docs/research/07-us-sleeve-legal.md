# India-Resident US-Sleeve Legal & Tax — Deep Research (Stream 07)

> Manual MoA aggregation (3 cross-family reference drafts → Opus aggregator). 2026-07-19.
> Ran references + aggregator directly (the `/moa` wrapper hit its float-inf accounting bug).

---

3 reference-model drafts received.

# Ground-Truth Compliance Report: India-Resident US Equity Sleeve via Alpaca / LRS

**Skeptic's source ledger.** Only three sources in this corpus are primary government text: the **RBI LRS FAQ (updated 06 Apr 2023)**, the **Income Tax Department Schedule FA page**, and the **IRS "Claiming tax treaty benefits" page**. The **Rashminsanghvi FEMA article** is authoritative practitioner commentary on RBI/OI text — near-primary, not a government circular. Everything else (Investmates, Capitalmind, Tax2win, Zerodha Varsity, INDmoney, Tradetron, DBS, Wise, AU Bank, Standard Chartered, Schwab, Investopedia) is blog/bank/fintech content, useful for cross-check but not citable to a regulator. No primary text of the **Income-tax Act 2025** or the **Finance (No.2) Act 2024** is in the corpus — rate claims resting on them are blog-consensus only.

---

## 1. FEMA / LRS Legal Invariants (Hard Locks)

**1a. Margin / leveraged trading — VERDICT: PROHIBITED, CONFIRMED (primary).**
RBI LRS FAQ Q2: *"Remittance from India for margins or margin calls to overseas exchanges / overseas counterparty"* is explicitly prohibited. Identical language in the DBS article and Rashminsanghvi para 2.2.12. Also prohibited: "remittance for trading in foreign exchange abroad." No LRS funds may post margin.

**1b. Shorting — VERDICT: PROHIBITED, effectively CONFIRMED by logic.** Not named in RBI's list, but shorting requires a margin/borrow construct that RBI Q2 bans. Treat as a hard block.

**1c. Derivatives / options / futures — VERDICT: PROHIBITED, CONFIRMED (near-primary).** Rashminsanghvi cites OI Directions para 1(ix)(a): *"OPI is not permitted in derivatives and commodities."* Capitalmind (blog) concurs: "funds through LRS cannot be used to invest in levered products." The blog aside that you *could* trade derivatives with a non-Indian funding source is editorial and irrelevant to an LRS-funded sleeve.

**1d. Cash/delivery equity only — VERDICT: CONFIRMED.** The permitted use is Overseas Portfolio Investment (OPI): long-only, cash-funded, **listed** foreign equity/ETFs and regulated fund units. RBI FAQ Q15 imposes no quality/rating filter, but Q2 + OI Directions exclude derivatives/commodities. Rashminsanghvi (para 2.2.8) adds a sharp exclusion: **no investment in securities of Indian companies listed abroad** (e.g., ADRs of Indian issuers) — those are not OPI.

**1e. LRS limit — VERDICT: USD 250,000 per resident individual per FY (Apr–Mar), CONFIRMED (primary).** RBI FAQ Q1. PAN-tracked cumulatively across all banks and all purposes. Q8: bringing proceeds back does **not** reset the year's limit. Equity purpose code **S0001** (INDmoney, blog — procedural, verify with AD bank; do not assume S0023 "bank account abroad").

**1f. 180-day idle-funds rule — VERDICT: CONFIRMED (primary), and the sharpest operational risk.** RBI FAQ Q4: *"received/realised/unspent/unused foreign exchange, unless reinvested, shall be repatriated ... within a period of 180 days."* Rashminsanghvi (paras 3.2–3.7) dates this to 24 Aug 2022, notes retrospective effect, and flags that bank FDs likely do **not** count as "invested." **This directly collides with a swing OS holding cash between trades.**

---

## 2. TCS on LRS Remittance

**Rate/threshold conflict (date-dependent) — resolved:**

| Source | Threshold | Rate | Effective |
|---|---|---|---|
| DBS (Dec 2025) | ₹7L | 20% | **STALE — pre-Apr-2025** |
| AU Bank (Jun 2025) | ₹10L | 20% | 1 Apr 2025 |
| INDmoney | ₹10L | 20% | Budget 2025 |
| Wise (verified 3 Mar 2026) | ₹10L | 20% | Budget 2026 |
| Standard Chartered notice | ₹10L | 20% | 1 Apr 2026 |

**VERDICT (equity = "other LRS purposes"): threshold ₹10 lakh, 20% above threshold, from FY 2025-26 onward — CONFIRMED by bank-published sources.** Any gate using ₹7L is wrong for FY26+.

⚠️ **Date/legislation flag:** The Standard Chartered notice references **Income Tax Act 2025, Section 506** (successor to §206C(1G) of the 1961 Act). Rate/threshold appear unchanged, but no primary IT Act 2025 text is in the corpus. Do **not** hardcode the TCS constant — verify §506 against §206C(1G) with a CA.

**Creditable? — VERDICT: YES, CONFIRMED.** TCS is advance tax, not final; reflected in Form 26AS/27D; adjustable/refundable via ITR. Budget 2024 lets salaried filers offset TCS against salary TDS mid-year (Zerodha).

**Funding math:** For **small disposable balances** (cumulative FY LRS < ₹10L ≈ ~$12k), **TCS = zero.** This is the likely regime here. Above ₹10L, 20% on the excess is a cash-flow drag until refund, not a legal barrier.

---

## 3. Tax Treatment of US-Stock Gains (India Resident)

**3a. Capital gains classification — VERDICT: 24-month threshold for foreign shares, CONFIRMED.** Distinct from Indian listed equity (12 months). The engine needs a separate holding-period clock for the US sleeve.

⚠️ **Rate conflict:** Tax2win states LTCG on foreign shares = 20% with indexation (**stale/old rule**). Investmates, Zerodha Varsity, and INDmoney state **12.5% without indexation, effective 23 Jul 2024** (Finance No.2 Act 2024). Use the date-versioned table:

| Gain | Holding | Rate |
|---|---|---|
| STCG | ≤ 24 mo | Slab (up to 30% + surcharge + cess) |
| LTCG (sold ≥ 23 Jul 2024) | > 24 mo | **12.5%** + surcharge + cess, no indexation |
| LTCG (sold 1 Apr–22 Jul 2024) | > 24 mo | 20% with indexation |

(Rates are blog-consensus; primary Act text not in corpus — verify.)

**3b. INR conversion — VERDICT: SBI TT buying rate, last day of month PRIOR to transaction, CONFIRMED (blog consensus, INDmoney/Zerodha).** All gains computed in USD then converted.

**3c. Dividends — VERDICT: 25% US withholding under India-US DTAA Art. 10, CONFIRMED.** USATaxGurus cites Article 10; IRS.gov (primary) confirms the W-8BEN mechanism for reduced treaty withholding (though it does not quote the 25% India figure). Default NRA rate is 30%; 25% requires a valid W-8BEN with the treaty box checked.
⚠️ **Tradetron error:** it claims W-8BEN cuts dividend withholding to **15%** — WRONG for India (15% is other treaties). Withhold at **25%**.
India side: gross dividend added at slab rate (Schedule OS); foreign tax credit via **Form 67 filed before the ITR deadline** (IT Rule 128) — missing it forfeits the credit.

**3d. US capital gains on India-resident NRA — VERDICT: ZERO, CONFIRMED.** Under US domestic law (not treaty), an NRA with <183 US days and no US trade/business owes no US capital-gains tax (Investmates, Zerodha, USATaxGurus). Record $0 US tax on equity gains. FIRPTA exception applies only to US real estate — irrelevant here.

**3e. ITR — VERDICT: ITR-2 (ITR-3 if business income), CONFIRMED.** ITR-1 is barred once any foreign asset exists. Schedules: **CG** (gains), **OS** (dividends), **FSI** (foreign-source income), **TR** (relief), **FA** (assets), plus **Form 67**.

---

## 4. Schedule FA & Wash-Sale

**4a. Schedule FA — VERDICT: MANDATORY regardless of size, CONFIRMED (primary).** IncomeTaxIndia.gov.in Schedule FA page: applies to resident assessees holding/owning/beneficially interested in foreign assets or with foreign-source income. Tax2win: required even if the asset is held a **single day**. No de-minimis for ordinary filing.
**Reporting period is the CALENDAR YEAR (1 Jan–31 Dec), not the Indian FY** — a record-keeping gotcha; reconcile Alpaca statements on calendar-year cutoffs.
**Report:** country/code, broker name, account number, acquisition date, **peak balance**, closing balance, gross income, sale proceeds — all in INR at SBI TTBR.
**Penalty:** ₹10 lakh per assessment year under the Black Money Act 2015, plus up to 7 years imprisonment and loss of DTAA credit (Capitalmind/Investmates/Tax2win/INDmoney — secondary, but consistent). Severe asymmetric risk even at tiny balances.
⚠️ **Budget 2026 FAST-DS 2026** amnesty (one-time 6-month window, prosecution immunity for non-immovable foreign assets <₹20L, retrospective from 1 Oct 2024) — reported by Tax2win only, not primary. Treat as a past-cleanup window, not an exemption. Always disclose from day one.

**4b. US wash-sale rule — VERDICT: DOES NOT APPLY to Indian ITR (PLAUSIBLE by inference; no explicit statutory text).** Investopedia/Schwab describe it as a US IRC §1091 rule governing US capital-loss deductions on US returns. An India-resident NRA files no US return computing equity gains, and Indian law (loss set-off under §§70–74) has **no wash-sale analog**. **Design implication: the tax-lot engine can IGNORE US wash-sale for India books** — use FIFO or specific-identification per Indian rules. Only relevant if the user ever becomes a US filer (183+ US days). Practitioner confirmation advised; conclusion rests on absence of an Indian provision.

---

## 5. Ranked Compliance-Gate Rules + Open Legal Risks

**Deterministic gates (encode as pre-trade / pre-remit checks):**

| # | Rule | Confidence |
|---|---|---|
| G1 | REJECT margin orders / any order posting collateral to an overseas exchange | RBI Q2 — PRIMARY |
| G2 | REJECT short/sell-to-open orders (no negative positions) | Derived from G1; Rashminsanghvi — NEAR-PRIMARY |
| G3 | REJECT options/futures/CFDs/swaps/forex/commodity orders | RBI Q2 + OI Directions 1(ix)(a) — PRIMARY |
| G4 | REJECT leveraged/inverse ETFs and Indian-issuer ADRs | OI Directions; Rashminsanghvi 2.2.8 — NEAR-PRIMARY |
| G5 | PERMIT only long, fully-paid, US-listed equity/ETF buys | OI/OPI — PRIMARY |
| G6 | BLOCK remittance when cumulative FY LRS (PAN-aggregate) would exceed USD 250,000 | RBI Q1 — PRIMARY |
| G7 | MONITOR idle USD (remittance/sale/dividend); FLAG @150d, ALERT @175d, force reinvest/repatriate <180d | RBI Q4 — PRIMARY |
| G8 | WARN when cumulative FY LRS > ₹10L (20% TCS on excess; date-versioned config) | AU Bank / SC — bank-published |
| G9 | Tax-lot: 24-month ST/LT split; date-versioned LTCG rate (12.5% post 23 Jul 2024) | Finance Act 2024 — blog consensus |
| G10 | Dividends: assume 25% US withholding; require valid W-8BEN; pre-fill Form 67 | DTAA Art.10; IRS.gov — PRIMARY (US mechanism) |
| G11 | Calendar-year snapshot (peak/closing balance, income) → Schedule FA, regardless of size | IncomeTaxIndia — PRIMARY |
| G12 | Force ITR-2 flag; generate FSI/TR/OS/CG/Form 67 pack; SBI TTBR conversions | Schedule FA page — PRIMARY |
| G13 | Do NOT apply US wash-sale in India tax engine | Inference from US/India law gap |

**Top 3 open legal risks (verify with a FEMA-qualified CA before live):**

**Risk 1 — 180-day idle-cash rule vs. swing-trading cash buffer (HIGHEST).** RBI Q4 (primary) + Rashminsanghvi make sale proceeds "realised FX" subject to 180-day repatriation unless reinvested. A swing OS structurally holds cash between trades. *Unresolved:* whether a buffer earmarked for imminent re-entry counts as "reinvested" or "idle" — Rashminsanghvi notes RBI has not clarified, and bank FDs likely don't qualify. Non-compliance = FEMA contravention requiring compounding. **Get a written opinion covering active-trading cash and whether Alpaca money-market sweep qualifies as reinvestment.**

**Risk 2 — Alpaca account configuration + derivatives scope (HIGH).** Alpaca often provisions margin/options/crypto-eligible accounts by default; the *existence* of a margin agreement could be argued inconsistent with LRS terms even if unused. Also unresolved: whether a covered call on already-held stock is a prohibited "derivative" or permissible. *Evidence:* RBI Q2 + OI Directions bar derivatives/margin, but the covered-call nuance is silent. **Obtain written Alpaca confirmation of a cash-only, no-margin, no-options, no-crypto account; get CA sign-off on any options feature before enabling.**

**Risk 3 — TCS legislative vehicle change (MEDIUM-HIGH).** Standard Chartered cites Income-tax Act 2025 §506 replacing §206C(1G); rate/threshold appear unchanged but no primary 2025-Act text is in corpus. Likewise, LTCG 12.5%/24-month rests on blog reading of Finance Act 2024, with Tax2win still showing the old 20%-with-indexation. **Verify §506 (TCS) and the current foreign-share LTCG rate against primary Act text before hardcoding constants.**

**Bottom line:** A **long-only, cash-funded, US-listed equity/ETF** sleeve for an India-resident individual is legally permissible under LRS. Margin, shorting, derivatives/options, leveraged ETFs, and Indian-issuer ADRs are prohibited. Schedule FA disclosure, Form 67, and the 180-day repatriation clock are non-negotiable and penalty-bearing even at small balances — the 180-day rule is the one most likely to be breached by an autonomous swing engine.

<!-- MOA-SYNTHESIS SELF-AUDIT: sections 1-5 present; 3 reference drafts received -->
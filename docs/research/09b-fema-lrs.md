# 09b — FEMA/LRS Adversarial Validation (F05, F06, F12-US, F13-LRS)

> **Status:** Evidence-first adversarial research pass. No implementation, no spec edit, no
> RESEARCH-STATE.md edit. Output is this report only.
> **Date:** 2026-07-20.
> **Scope:** India-resident individual funding a US equity sleeve via Alpaca under the LRS.
> **Assigned findings:** F05 (180-day idle-FX watchdog), F06 (PAN-wide LRS cap),
> F12 US-sleeve portion (compliance rule set), F13 LRS gross-vs-net accounting.
> **Companion to:** `07-us-sleeve-legal.md` (built on and re-verified against current primary text).
> **Authoritative decisions under review:** D19 (compliance invariants), D21 (two-currency accounting).

---

## 0. Source ledger (primary vs secondary)

**PRIMARY (government / regulator text, current):**
- **RBI LRS FAQ**, `https://www.rbi.org.in/scripts/FAQView.aspx?Id=115` — *Updated as on April 06, 2023.* Q1 (cap), Q2 (prohibited items incl. margin), Q4 (180-day repatriation), Q6/Q12 (Form A2 + designated AD branch), Q8 (PAN-aggregate cap, no reset on repatriation), Q15 (no quality filter, subject to OI Rules 2022).
- **FEMA (Overseas Investment) Regulations, 2022**, No. FEMA 400/2022-RB, 22 Aug 2022, `https://rbi.org.in/Scripts/BS_FemaNotifications.aspx?Id=12380` — OPI reporting for resident individuals (Reg 10(3)); designated-AD-bank routing (Reg 9); the OI framework the LRS FAQ Q15/Q4 defers to.
- **CBDT "Tax Collection at Source (TCS)" explainer PDF**, incometaxindia.gov.in, published Mar 2026 (`.../42998/Tax-Collection-at-Source-TCS_2026-01-19...pdf`) — §206C(1G): LRS "other purposes" **20%** above **₹10 lakh**; threshold across **all purposes on a first-come-first-serve basis**; collected at debit/receipt whichever earlier; max TCS rate capped at 20% since 1 Jul 2023; creditable via Form 26AS/27D.
- **Income-tax Rule 115A**, `https://www.incometaxindia.gov.in/w/rule-115a` (upload 13 Dec 2025) — TT-rate conversion, but **NRI/Indian-company-shares specific** (see F13 caveat).
- **RBI BoP purpose-code annexure** (in FAQ Id=1834 and `https://www.rbi.org.in/upload/notification/pdfs/52220.pdf`) — **S0001 = "Indian investment abroad – in equity capital (shares)."**
- **Form 15CA/15CB FAQ**, incometax.gov.in — §195 TDS mechanism (relevance-limited for LRS equity, see F13).
- **Alpaca FDIC Bank Sweep docs**, `https://docs.alpaca.markets/us/docs/fdic-sweep-program` + support FAQ — swept cash is **"uninvested cash"** held as an **FDIC-insured bank deposit**, "treated differently and subject to separate regulatory regimes."

**SECONDARY / near-primary (practitioner + bank commentary, cross-check only):**
- **ELP OI-Rules digest** (elplaw.in) — near-primary restatement of OI Rules 2022 definitions (OPI, non-debt instruments, resident-individual manner). Used for the OPI "listed / >50%-equity ETF / Indian-issuer" boundary.
- **RSM India newsflash** — dates the 180-day rule to Master Direction 7/2015-16 amendment **24 Aug 2022**, aligned with FEMA (Realisation, Repatriation & Surrender) Regs 2015 Reg 7; explicitly flags the **ambiguity** for non-invested balances and recommends AD-bank confirmation.
- **Rashminsanghvi FEMA article** (rashminsanghvi.com) — practitioner commentary; OI Directions para 1(ix)(a) derivatives/commodities exclusion; Indian-issuer-listed-abroad exclusion.
- **CompareRemit / Razorpay / DBS / SC Bank / HDFC** — blog/bank confirmations of the 180-day framing, S0001 code, and TCS ₹10L/20% effective 1 Apr 2025+.

---

## F05 — 180-day idle-FX watchdog cannot prevent a FEMA breach

### Primary text (RBI LRS FAQ Q4, updated 06-Apr-2023)
> "The investor who has remitted funds under LRS can retain and reinvest the income earned from his investments made under the Scheme. However, the **received/realised/unspent/unused foreign exchange, unless reinvested, shall be repatriated and surrendered to an authorised person within a period of 180 days from the date of such receipt/ realisation/ purchase/ acquisition or date of return to India**, as the case may be. Further, any additional repatriation requirement with respect to investments made under Overseas Investments Rules and Regulations 2022 shall also be adhered to."

### Answers to the specific questions
- **Clock start.** PRIMARY-CONFIRMED. The 180-day clock runs from **the date of receipt / realisation / purchase / acquisition** (or return to India) of the *foreign exchange* — i.e., it is **per-credit, not per-remittance-wire.** Concretely:
  - **Unspent remittance remainder** → clock from the **date the FX was purchased/remitted** (receipt of FX abroad).
  - **Sale proceeds** → clock from the **sale-realisation (settlement) date** of the disposed security.
  - **Dividend** → clock from the **dividend receipt date.**
  This defeats a design that keys the deadline off the remittance wire only. Each realized-FX credit is its own clock — exactly the `IdleFxLot` model F05 proposes.
- **Does reinvestment cure it?** PRIMARY-CONFIRMED yes: "**unless reinvested**" is the express carve-out. Reinvestment into a permitted OPI security within 180 days cures that lot. (RSM confirms: "invest the funds in securities outside India ... within 180 days.")
- **Does an Alpaca money-market / FDIC cash sweep count as "invested"?** **NOT-SUPPORTED as a cure → OPEN-LEGAL-OPINION, but the evidence now points strongly to NO.** Alpaca's own primary documentation labels swept balances "**uninvested cash**" moved into an "**FDIC-insured bank deposit**" that is "treated differently and subject to separate regulatory regimes" from securities in the brokerage account (SIPC vs FDIC). A bank deposit earning interest is materially the same instrument class the practitioner commentary (Rashminsanghvi, stream 07 §1f) says likely does **not** qualify as "invested" (bank FDs flagged as non-qualifying). Reinvestment in FAQ Q4 is tied to "investments made under the Scheme" governed by **OI Rules 2022** — a foreign bank deposit is neither ODI nor OPI (OPI = investment in *foreign securities*; a deposit is not a security). **Conclusion: a cash sweep is best treated as still-idle FX, NOT a cure. This resolves the highest open risk in 07 in the conservative direction, but because RBI has not issued a clarification, a written AD-bank / FEMA-CA opinion remains a mandatory pre-live blocker before relying on any sweep as a cure.**
- **Does blocking new investment at day 175 CURE a breach?** **CONFIRMED (finding is correct).** Blocking new *investment* removes one of the two cures (reinvestment) while doing nothing about the other (repatriation). The only two lawful terminal states for an idle lot are **(a) reinvested into a permitted OPI security** or **(b) repatriated & surrendered to an authorised person**, both **before** day 180. A warn-and-block design leaves the money idle at day 180 → the FEMA contravention crystallises. The watchdog as specced (alert 150, block 175) does not reach a compliant terminal state; it must *repatriate* (or reinvest) a lot, not merely stop new buys.
- **Is autonomous Alpaca→India repatriation feasible/legal?** **OPEN / likely MANUAL.** Repatriation must land back through the **designated AD bank** and be surrendered to an authorised person; a broker-initiated ACH/wire back to the Indian AD account is operationally a manual/bank-mediated step, not a broker API primitive that the OS can fire deterministically and prove. Absent explicit tested automated-repatriation capability, F05's fallback — **verified manual repatriation with broker/bank-confirmed disposition per lot, else the US sleeve cannot go live** — is the correct posture.

### Verdict: **CONFIRMED** (finding is materially correct). Sweep-as-cure sub-question: **NEEDS-HUMAN/LEGAL-DECISION** (evidence leans NO).

### Concrete breach trace
Day 0: sell AAPL, USD 8,000 settles as cash → realized-FX lot, clock starts (realisation date). Day 0–174: cash sits (or is swept to FDIC program = still "uninvested"). Day 150 alert, Day 175 block-new-buys fires → cash still idle. Day 180: no reinvestment, no repatriation → **FEMA (Realisation, Repatriation & Surrender) Reg 7 contravention**, compoundable under FEMA §13; the watchdog "succeeded" while the legal state breached.

### Smallest correct design edit
Adopt the F05 `IdleFxLot` model verbatim, plus: (1) clock keyed to **each realized-FX credit's value date** (remittance/sale/dividend/refund), not the wire; (2) the terminal action at the deadline is **reinvest-or-repatriate**, never "block only"; (3) **treat FDIC/MMF sweep as idle** (does not stop the clock) until a written opinion says otherwise; (4) require **broker/bank-confirmed disposition** per lot; (5) if automated repatriation is not authorized+tested, gate the whole US sleeve behind verified manual repatriation.

### D19/D21 impact
**D19 must be amended.** Its current text says "180-day idle-FX watchdog (alert day 150, block new investment day ~175)" — that is precisely the non-curing design F05 exposes. D19 should be reworded to a per-lot reinvest-or-repatriate obligation with confirmed disposition. **D21 needs a schema addition**: the LRS remittance ledger must also carry realized-FX-lot origin/value-date/deadline/disposition (currently D21 tracks INR-out/USD-in per wire only).

---

## F06 — a local ledger cannot enforce the PAN-wide LRS cap

### Primary text
- **Q1:** "all resident individuals ... are allowed to freely remit up to **USD 2,50,000 per financial year (April – March)** for any permissible current or capital account transaction **or a combination of both**."
- **Q8:** "the total amount of foreign exchange **purchased from or remitted through, all sources in India** during a financial year should be within the cumulative limit of USD 2,50,000. **Once a remittance is made for an amount up to USD 2,50,000 during the financial year, a resident individual would not be eligible to make any further remittances under this scheme, even if the proceeds of the investments have been brought back into the country.**"
- **Q7:** PAN mandatory for all LRS transactions (the aggregation key).

### Answers to the specific questions
- **PAN-level, all-banks, all-purposes aggregation?** **PRIMARY-CONFIRMED.** Q8 = "all sources in India" + "combination of both" purposes; Q7 = PAN is the key. The cap is a single per-PAN-per-FY meter, **not per-bank, not per-purpose.**
- **Repatriation does NOT reset the used amount within the FY?** **PRIMARY-CONFIRMED.** Q8 explicit: "even if the proceeds of the investments have been brought back into the country." Bringing money back does not restore headroom in the same FY.
- **Does buying US stock with already-settled cash consume additional LRS?** **CONFIRMED (finding correct): NO.** LRS meters the **outbound remittance / FX purchase** (Q8: "purchased from or remitted through"). Once USD is at Alpaca, buying/selling securities inside the account is not a further LRS drawal. So the LRS gate is a **pre-remittance** gate, not a pre-trade gate — exactly F06's split. The corollary F06 flags is the real hazard: **a local ledger sees only the wires it originated; it is blind to remittances the same PAN made through other banks or for other purposes** (education, travel, another broker). It therefore cannot compute true FY headroom.
- **Correct purpose code + AD-bank requirement?** **PRIMARY-CONFIRMED.** **S0001 = "Indian investment abroad – in equity capital (shares)"** (RBI BoP purpose-code annexure; Razorpay secondary confirms with an NYSE-share example). NOT S0023/bank-account-abroad. Q12/Q6: the individual must **designate a branch of an AD** for all capital-account LRS remittances and file **Form A2**; the ultimate compliance responsibility is the remitter's.

### Verdict: **CONFIRMED** (finding is correct in full).

### Concrete breach trace
User remitted USD 200k via Bank X (education + travel + another broker) — invisible to the OS. OS has recorded only USD 20k of its own wires to Alpaca and computes USD 230k headroom. It approves a USD 50k remittance. True FY total = USD 270k → **USD 20k over the §Q1 cap → FEMA contravention.** The local meter's "230k free" was structurally uninformed.

### Smallest correct design edit
Adopt F06 verbatim: split `PreRemittanceGate` from `PreTradeGate`. The pre-remittance gate must require a **current PAN-wide opening position** — either an AD-bank statement of FY LRS utilisation or an **explicit signed remitter attestation** of all-bank/all-purpose FY remittances — and **fail closed** on unknown/stale external state. Repatriation never decrements the meter. Purchases from settled cash do not touch the meter. Keep the ₹10L soft-warn (TCS) and 80%-cap soft-warn.

### D19/D21 impact
**D19 partially correct but under-specified** — it already says "PAN-level, all banks ... no reset on repatriation," which is right, but it does not acknowledge that a local ledger **cannot know** external remittances; it must add the external-state / signed-attestation requirement and the fail-closed rule. **D21**: the LRS remittance ledger is only the OS's own view; it must be explicitly labelled as a *lower bound* on PAN utilisation, never the authoritative meter.

---

## F12 (US portion) — must these be explicit gate rules?

All items below are pre-order US-sleeve gates. Verdicts:

| Rule | Verdict | Basis |
|---|---|---|
| **Indian-issuer ADR exclusion (not OPI-eligible)** | **CONFIRMED — must be an explicit gate** | OI Rules 2022 def. of OPI: "investment ... in foreign securities, **but not** ... any security **issued by a person resident in India** who is not in an IFSC" (ELP digest of primary Rules; Rashminsanghvi 2.2.8). An ADR/security of an Indian issuer listed abroad is **not** OPI → not LRS-permitted. PRIMARY-grounded (Rules text), near-primary source. |
| **Leveraged / inverse / synthetic / commodity ETF exclusion** | **CONFIRMED — explicit gate** | OI Rules non-debt-instrument list permits "units of mutual funds and **Exchange-Traded Fund which invest more than 50% in equity**." Commodity/derivative/leveraged/inverse ETFs are **not >50% cash equity** → outside OPI. Reinforced by OI Directions para 1(ix)(a) "OPI is not permitted in derivatives and commodities" (Rashminsanghvi, near-primary). |
| **Margin / short / derivative / FX / crypto exclusion** | **CONFIRMED — explicit gate (hard lock)** | RBI LRS FAQ **Q2**: "Remittance from India for margins or margin calls to overseas exchanges / overseas counterparty" and "Remittance for trading in foreign exchange abroad" prohibited (PRIMARY). Derivatives/commodities barred by OI Directions (near-primary). Shorting requires margin/borrow → falls under Q2 by construction. Crypto: not a permitted foreign security under OI Rules. |
| **Cash-account-only** | **CONFIRMED — explicit gate** | Direct corollary of Q2 margin prohibition: a margin account posts collateral. Cash account is the only LRS-consistent structure. (Blocker: written Alpaca confirmation of a contractual cash / no-implicit-leverage account — carried from D19 verify-before-live.) |
| **Settled-cash-only** | **CONFIRMED-WITH-MODIFICATION** | Follows from cash-account-only (no unsettled-funds trading = no de-facto margin/free-riding). This is PRIMARY-by-inference from Q2 rather than a named FEMA rule; also a US Reg-T/good-faith-violation concern. Keep as an explicit gate; label its FEMA basis as inference. |

### Verdict: **CONFIRMED** — every listed item must be an explicit deterministic pre-order gate. This matches D19's whitelist ("long common stock + plain listed ETFs only") but D19 should be made precise: **"plain ETF" → ">50%-equity, non-leveraged, non-inverse, non-commodity, non-synthetic ETF"**, and **"reject Indian-issuer securities/ADRs"** should be named explicitly (D19 currently omits the Indian-issuer exclusion). No D-decision *reversal*, but D19 wording refinement.

---

## F13 (LRS accounting) — gross vs net; AD-bank certificate; TCS; Rule 115

### Answers to the specific questions
- **Is the LRS meter fed by GROSS or NET remittance?** **PRIMARY-CONFIRMED: GROSS.** §206C(1G) collects TCS **on the remittance amount at the time of debiting the account / receipt, whichever earlier** — TCS is charged *on top of* the amount remitted, it does not reduce what counts against LRS. The LRS cap is the **foreign exchange purchased/remitted** (Q8), i.e., the **gross principal converted to FX**, *before* TCS and *before* the bank's FX spread. So the D19/D21 LRS meter must accrue the **gross USD (or INR-equivalent) actually remitted/purchased**, with **TCS and bank spread recorded as separate lines** (they are not part of the FX sent abroad). This matches F13's proposed edit ("AD-bank certificates for gross LRS amounts; record spreads, fees, and TCS separately").
- **What does the AD-bank certificate certify?** **CONFIRMED-WITH-MODIFICATION.** The load-bearing LRS document is **Form A2** (RBI FAQ Q6/Q12): the remitter declares purpose (via A2) and the **AD certifies the remittance conforms to RBI instructions**; A2 is the authoritative record of the **gross FX remitted under LRS**. **Form 15CA/15CB is a §195-TDS instrument for payments *chargeable to tax* in India** — an outbound LRS equity purchase is a capital transfer generally *not* chargeable (Form 15CA **Part D** "not chargeable to tax"), so **15CB (CA certificate) is typically NOT the LRS-amount certificate.** The finding's mention of "Form A2 / Form 15CA-CB" should be corrected: **A2 is the gross-LRS certificate; 15CA/15CB is a separate TDS-on-payment-to-non-resident form and is generally Part-D/not-required for a plain equity remittance.**
- **TCS current rate/threshold.** **PRIMARY-CONFIRMED.** CBDT TCS PDF (Mar 2026): LRS "other purposes" = **20% on the amount exceeding ₹10 lakh** per FY; **₹10L threshold aggregates across all purposes, first-come-first-serve**; **max TCS rate capped at 20%** since 1 Jul 2023; credited via Form 26AS, certificate Form 27D, creditable/refundable in the ITR. The stale **₹7 lakh / pre-Apr-2025** figure is wrong for FY 2025-26+. Equity = "other purposes" (not the 5% education/medical bucket). The legislative vehicle is §206C(1G) of the 1961 Act (the 2025-Act successor §506 flagged in 07 — rate/threshold unchanged per the current CBDT explainer, which still cites §206C(1G); no divergence observed, but do not hardcode — keep date-versioned config).
- **Rule-115 conversion (SBI TT buying rate, last day of month prior).** **CONFIRMED-WITH-IMPORTANT-CAVEAT.** For a **resident** holding **foreign** shares, the general conversion rule is **Rule 115** (income converted at the TT buying rate of the SBI on the specified date; for capital gains the relevant date convention is the last day of the month **immediately preceding** the month of the transaction). **Rule 115A** (which this pass fetched) is **narrower** — it applies to an **NRI**'s gains on **shares/debentures of an Indian company** and uses the currency "initially utilised in the purchase" — so **Rule 115A is NOT the applicable rule for an India-resident's US-equity gains.** The design should cite **Rule 115** (last-day-of-prior-month SBI TTBR), matching D21's existing "Rule-115 tax rate (SBI TTBR, last day of prior month)." The holiday-fallback / stale-rate handling F13 asks for is a real gap: neither Rule 115 nor RBI text specifies a holiday fallback, so the design must define one deterministically (e.g., last published SBI TTBR on/before the reference date) and label it INFERENCE.

### Verdict: **CONFIRMED-WITH-MODIFICATION.** The gross-remittance principle is primary-correct; the certificate must be re-labelled **Form A2 (gross LRS)**, not 15CA/CB; the conversion rule is **Rule 115**, not 115A.

### D19/D21 impact
**D19**: fine on TCS (₹10L/20%) — keep date-versioned. **D21 must be amended twice:** (1) explicitly state the LRS meter accrues **gross FX** with TCS + spread as separate ledger lines (currently D21 says "records INR-out / USD-in per wire" without the gross/net distinction); (2) cite **Rule 115** for the tax rate (D21 already says "Rule-115" — good — but the fetched Rule 115A must not be substituted); add a defined holiday/stale-rate fallback.

---

## Per-finding verdict table

| Finding | Verdict | Primary basis | D-impact |
|---|---|---|---|
| **F05** 180-day watchdog | **CONFIRMED**; sweep-as-cure = **NEEDS-HUMAN/LEGAL-DECISION** (evidence → NO) | RBI FAQ Q4 (clock = per realized-FX credit; reinvest cures; block ≠ cure) + Alpaca sweep = "uninvested cash" | **D19 amend** (reinvest-or-repatriate per lot, confirmed disposition); **D21 schema add** (idle-FX-lot fields) |
| **F06** PAN-wide cap | **CONFIRMED** (full) | RBI FAQ Q1/Q7/Q8 (PAN, all-banks/all-purposes, no reset) + S0001 code + Q12 AD-bank/A2 | **D19 add** external-state/attestation + fail-closed; **D21** label local meter a lower bound |
| **F12** US-sleeve gates | **CONFIRMED** (all 5 must be explicit gates) | OI Rules 2022 OPI def (Indian-issuer + >50%-equity-ETF); RBI FAQ Q2 (margin/FX); OI Directions (derivatives/commodities) | **D19 refine wording** (name Indian-issuer exclusion; precise ETF definition) — no reversal |
| **F13** LRS accounting | **CONFIRMED-WITH-MODIFICATION** | §206C(1G) gross-basis TCS 20%/₹10L (CBDT PDF); Form A2 (not 15CA/CB); Rule 115 (not 115A) | **D21 amend** (gross-FX meter + separate TCS/spread lines; cite Rule 115; holiday fallback) |

---

## Compliance matrix — pre-remittance & idle-FX rules

Label key: **PRIMARY** = government/regulator text; **SECONDARY** = practitioner/bank; **INFERENCE** = logical corollary of primary; **OPEN** = unresolved, needs legal opinion.

### Pre-remittance rules (the `PreRemittanceGate`)

| Rule | Label | Source |
|---|---|---|
| USD 250,000 / FY (Apr–Mar) hard cap | **PRIMARY** | RBI FAQ Q1 |
| Aggregated at PAN level, across all banks & all purposes | **PRIMARY** | RBI FAQ Q7, Q8 |
| Repatriation does not reset FY headroom | **PRIMARY** | RBI FAQ Q8 |
| Local ledger cannot know external-bank remittances → external state / signed attestation required, fail-closed | **INFERENCE** (of Q8 PAN-aggregation) | F06 reasoning |
| Buying stock with settled cash does NOT consume LRS (meter = wire only) | **PRIMARY** | RBI FAQ Q8 ("purchased from or remitted through") |
| Purpose code S0001 (Indian investment abroad – equity capital/shares) | **PRIMARY** | RBI BoP purpose-code annexure |
| Designated AD-bank branch + Form A2 declaration | **PRIMARY** | RBI FAQ Q6, Q12 |
| LRS meter fed by GROSS FX (TCS + spread separate) | **PRIMARY** | §206C(1G) + FAQ Q8 |
| TCS 20% on remittance > ₹10L/FY (all purposes, FCFS), creditable | **PRIMARY** | CBDT TCS PDF |
| ₹10L soft-warn + 80%-cap soft-warn | **INFERENCE** (operational, from the two primary thresholds) | design |
| Margin/FX/derivative/commodity remittance prohibited | **PRIMARY** | RBI FAQ Q2 + OI Directions |
| Indian-issuer ADR / security not OPI-eligible | **PRIMARY** (OI Rules def) / near-primary source | OI Rules 2022; ELP; Rashminsanghvi |

### Idle-FX (180-day) rules (the `IdleFxLot` watchdog)

| Rule | Label | Source |
|---|---|---|
| Realized/unspent/unused FX must be reinvested-or-repatriated within 180 days | **PRIMARY** | RBI FAQ Q4 |
| Clock starts per credit at receipt/realisation/purchase/acquisition/return-to-India (not per wire) | **PRIMARY** | RBI FAQ Q4 |
| Reinvestment into a permitted OPI security cures the lot | **PRIMARY** | RBI FAQ Q4 ("unless reinvested") |
| Blocking new investment ≠ cure; only reinvest OR repatriate cures | **INFERENCE** (of Q4's binary cure set) | F05 reasoning |
| FDIC/MMF cash sweep is NOT "invested" (does not stop the clock) | **OPEN** (evidence leans NO: Alpaca calls it "uninvested cash"; OPI = security, deposit ≠ security) | Alpaca docs (PRIMARY on product) + OI Rules + Rashminsanghvi (SECONDARY) |
| Autonomous Alpaca→India repatriation feasibility | **OPEN** (likely manual; needs tested capability) | OI Reg 9 designated-AD routing + operational reality |
| Rule was aligned with FEMA (Realisation/Repat/Surrender) Regs 2015 Reg 7 on 24 Aug 2022 | **SECONDARY** | RSM newsflash |

---

## Mandatory human / legal decisions (do not silently resolve)

1. **Sweep-as-reinvestment (F05).** Get a written FEMA-CA / AD-bank opinion: does an Alpaca FDIC/MMF cash sweep count as "reinvested" under FAQ Q4? Evidence says NO; the OS must default to treating it as idle until told otherwise. **Pre-live blocker.**
2. **Automated vs manual repatriation (F05).** Confirm whether Alpaca→designated-AD-bank repatriation can be executed and confirmed programmatically, or must be manual. Without a tested automated path, gate the US sleeve behind verified manual repatriation. **Pre-live blocker.**
3. **External LRS-utilisation source (F06).** Decide the authoritative PAN-wide-utilisation input: AD-bank statement vs signed remitter attestation; define the fail-closed staleness bound.
4. **Rule 115 vs 115A + holiday fallback (F13).** CA sign-off that Rule 115 (resident, foreign shares) governs, and a defined deterministic holiday/stale-rate fallback for SBI TTBR.
5. **§206C(1G) vs IT-Act-2025 §506 (F13).** Confirm the 2025-Act successor leaves 20%/₹10L unchanged before hardcoding; keep date-versioned config regardless (carried from D19 verify-before-live blocker #1).

---

## Bottom line

- **F05 CONFIRMED** — the watchdog as specced never reaches a compliant terminal state; it must reinvest-or-repatriate each realized-FX lot with confirmed disposition. The single most consequential newly-closed sub-question: **a cash sweep is very likely NOT a cure** (Alpaca itself labels it "uninvested cash"), but this needs a written opinion. **D19 amend + D21 schema add.**
- **F06 CONFIRMED in full** — PAN-aggregate, all-banks/all-purposes, no reset on repatriation, meter = outbound wire, S0001 + designated AD + Form A2, all PRIMARY. A local ledger is a lower bound; the pre-remittance gate needs external state or attestation and must fail closed. **D19 add external-state rule.**
- **F12 (US) CONFIRMED** — all five exclusions are mandatory explicit gates, grounded in OI Rules 2022 (OPI definition) + RBI FAQ Q2 + OI Directions. **D19 wording refinement** (name the Indian-issuer exclusion; precise ETF definition).
- **F13 CONFIRMED-WITH-MODIFICATION** — LRS meter is fed **gross** (TCS + spread separate); the gross-LRS certificate is **Form A2** (not 15CA/CB); the conversion rule is **Rule 115** (not the fetched 115A). TCS 20%/₹10L is primary-confirmed. **D21 amend.**

None of these findings is NOT-SUPPORTED. Two sub-questions remain OPEN-LEGAL-OPINION (sweep-as-cure; automated repatriation), both under F05, both pre-live blockers.

---

**Self-audit:** Assigned findings F05, F06, F12-US, F13-LRS all addressed with per-finding verdict, primary source + effective date, breach trace, smallest design edit, and D19/D21 amendment call. Primary sources (RBI LRS FAQ 06-Apr-2023; FEMA OI Regs 2022; CBDT TCS Mar-2026; Rule 115A text; RBI purpose-code annexure; Form 15CA FAQ; Alpaca FDIC-sweep docs) fetched and quoted; secondary sources labelled. Per-finding table + two compliance matrices (pre-remittance, idle-FX) with PRIMARY/SECONDARY/INFERENCE/OPEN labels included. Human-decision section lists 5 items; 2 OPEN sub-questions flagged. Spec and RESEARCH-STATE.md were NOT edited. Known limitations: OI Rules/OI Directions read via near-primary digest (ELP) + practitioner commentary, not the raw Gazette PDF of the Rules (the Regulations Gazette was fetched primary); Schedule FA field enumeration deferred to 07 §4a (out of assigned scope); §506 IT-Act-2025 text not independently pulled (carried as an existing verify-before-live blocker).

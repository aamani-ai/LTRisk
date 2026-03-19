Create a technical slide deck that explains and defends the Long-Term Climate Risk Framework end-to-end, using the source as truth. Emphasize math, assumptions, data flow, and pilot implementation.

Source document to upload: `local_docs/long_term_risk_evolution/LONG_TERM_RISK_FRAMEWORK.md`

Audience: Internal technical team implementing the pilot (climate data + risk + valuation)
Tone: Technical but clear; auditable; define terms; show reasoning and limitations.

Slide Structure:

Slide 1: Title + Scope
- Long-Term Climate Risk Framework (Pilot) → NAV Impairment for renewables
- Assets: Solar (25y EUL), Wind (35y EUL); Scenario: moderate pathway (RCP/SSP)
- Outputs: SCVR, HCR/BI, EFR/IUL, NPV_base vs NPV_climate, NAV impairment

Slide 2: Why This Exists (Problem + Gap)
- Investors need: “How does climate change impair asset value over 25–35 years?”
- Traditional models miss chronic stress shortening asset life (“duration of cashflows”)
- Framework separates channels: hazards (BI), performance, equipment life

Slide 3: Core Definitions (Glossary Table)
- Table: SCVR | HCR | EFR | EUL | IUL | BI | NAV impairment
- Units: SCVR (%) ; HCR (%) ; EFR (% life per % SCVR) ; EUL/IUL (years)
- Baseline vs Climate scenario: what changes, what is held constant

Slide 4: Master Equation (Valuation)
- NPV: Σ[Net(t) / (1+WACC)^t]
- Baseline: sum to EUL; Climate: sum to IUL
- NAV impairment: (1 - NPV_climate / NPV_base) × 100%

Slide 5: System Architecture (3 Pathways)
- Pathway A: Climate → SCVR → HCR → BI → Net revenue down
- Pathway B: Climate vars → physics performance model → MWh → Revenue
- Pathway C: Climate stress → SCVR → EFR → IUL → fewer revenue years

Slide 6: Data Inputs + Period Averaging
- Baseline period vs future window (avoid single-year noise)
- Variables: temp, precip, wind, humidity, irradiance (dataset-dependent)
- Ensemble handling: compute per model; report mean + spread

Slide 7: SCVR (Severe Climate Variability Rating)
- Definition: % change in area under exceedance curve
- Captures frequency + severity (not just counts)
- Computed per variable/index (heatwave, Rx5day, wind proxy, etc.)

Slide 8: Pathway A — Hazards → Business Interruption
- HCR: % hazard risk increase as function of relevant SCVRs
- BI_climate(h) = BI_base(h) × (1 + HCR_h)
- Needs: hazard list, BI_base sources, coefficient justification

Slide 9: Pathway B — Climate → Performance
- Solar: irradiance + temp + wind → pvlib-style chain → AC power
- Wind: hub-height wind + power curve + cut-out + icing → AEP
- Output: P10/P50/P90 envelopes; years 1–3 may use S2S

Slide 10: Pathway C — Stress → Life (IUL)
- Scientific models: Peck (heat+humidity), Coffin–Manson (thermal cycling), Miner (fatigue)
- Linearized summary: EFR table per asset type × climate variable
- IUL: IUL = EUL × [1 - Σ_i (EFR_i × SCVR_i)]

Slide 11: Worked Example (Hayhurst Solar) — Numbers Flow
- Show: SCVR_heat+humidity, SCVR_freeze (benefit), example EFRs
- Compute: life reduction = Σ(EFR×SCVR) → IUL years
- Then: BI changes + performance changes → NPV_climate → NAV impairment

Slide 12: Sensitivity + Uncertainty (What Matters Most)
- Table: vary EFR, SCVR, HCR coeffs, WACC, EUL
- Explain why life reduction dominates value (lost terminal years)
- Present outputs as ranges (P10/P90 or scenario bands)

Slide 13: Key Assumptions + Known Limitations
- Linearization (EFR×SCVR, HCR×SCVR) vs real non-linear physics
- Exclusions: physical damage, catastrophic hazards, price evolution, O&M changes
- Dataset/variable availability risks; proxy metrics (gusts, wildfire, etc.)

Slide 14: Implementation Plan (Pilot Execution)
- Step 1: pull climate ensembles + compute SCVR tables (per year/window)
- Step 2: run performance sims (base vs climate) + envelopes
- Step 3: build HCR table from literature/internal + BI projections
- Step 4: build EFR table + compute IUL + finalize NPV/NAV impairment

Slide 15: Deliverables (Engineering + Stakeholders)
- Dashboard panels: SCVR evolution; performance envelopes; BI by hazard; EUL vs IUL bars
- Artifacts: SCVR/HCR/EFR tables with citations; reproducible notebooks/scripts
- Decision outputs: NAV impairment % + uncertainty; top drivers; next improvements

Slide 16: Roadmap (Gen1 → Gen2)
- Gen1: linear tables + transparent assumptions + ranges
- Gen2: non-linear hazard/life response; equipment-specific params; validation vs field
- Gen3: portfolio scale; probabilistic integration; price/O&M dynamics

Design: Clean, minimal text; diagrams from source (3-pathway flow, exceedance curve, IUL bar). Use 1–2 compact tables per slide max. Consistent color coding: SCVR (green), BI/HCR (orange), IUL/EFR (red), NPV (blue).

Key Messages:
- NAV impairment comes from performance + hazards + shortened life.
- SCVR is the central, auditable climate stress metric.
- Biggest uncertainty is HCR/EFR calibration; show ranges + sensitivity.
- Framework is implementable now; defensibility improves with staged calibration.

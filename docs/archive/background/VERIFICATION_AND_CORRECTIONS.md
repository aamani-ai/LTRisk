# Verification and Corrections Log

*Systematic review of claims in PILOT_FRAMEWORK_ANALYSIS.md against Team's Original Proposal*

**Purpose:** Address accuracy concerns and clearly distinguish between (a) what the team actually proposed, (b) what I added as illustrative examples, and (c) potential errors or discrepancies.

**Created:** February 1, 2026  
**Status:** Critical Review

---

## CRITICAL DISCREPANCY FOUND

### 1. CMIP5 vs CMIP6 Confusion

**What the TEAM's original proposal said:**
> "Expected Performance will be the Revenues estimated by the InfraSure asset-specific performance models for the Base Scenario under the **CORDEX down-scaled CMIP5** framework."

**What I wrote after the user's correction:**
> "Use NEX-GDDP-**CMIP6** for climate data"
> "CMIP6 DOES provide solar radiation via rsds variable"

**The Problem:**
- CMIP5 and CMIP6 are DIFFERENT datasets
- CORDEX (downscaled CMIP5) vs NEX-GDDP (downscaled CMIP6) are DIFFERENT products
- The user's correction about rsds availability was about CMIP6, but the team's proposal uses CMIP5

**Resolution Needed:**
1. Clarify with team: Are they using CMIP5 (as stated) or CMIP6?
2. If CMIP5: Does CORDEX-CMIP5 include rsds (solar radiation)?
3. If CMIP6: Update proposal to reference correct data source

**Action Required:** 
- Add clarification note in analysis document
- Do NOT assume CMIP5 CORDEX has same variables as CMIP6 NEX-GDDP

---

## Items Where I ADDED Illustrative Examples (Not From Team)

The following content in my analysis is **MY ILLUSTRATIVE EXAMPLE**, not from the team's proposal:

### 1. EFR Values

**What I wrote:**
```
EFR values (from research):
  • Temperature impact: EFR = 0.5% life loss per % SCVR
  • Freeze/thaw impact: EFR = 0.3% life loss per % SCVR
  • Humidity impact: EFR = 0.2% life loss per % SCVR
```

**What the team actually said:**
> "Develop the EFR Table based on review of published research and internal discussions."

**Correction:** These specific EFR values (0.5%, 0.3%, 0.2%) are MADE UP by me as illustrative. The team has NOT specified these values yet - they will derive them from research.

**Action:** Mark these as "ILLUSTRATIVE - actual values TBD by team"

---

### 2. HCR Values

**What I wrote in the HCR table:**
```
Pluvial Flood: +8% → +30% by 2050
Hail: +2% → +10% by 2050
Wind: +5% → +15% by 2050
```

**What the team actually said:**
> "Develop the HCR Table based on review of published research and internal discussions."

**Correction:** These HCR percentages are ILLUSTRATIVE EXAMPLES I created. The team has NOT provided these values.

**Action:** Mark HCR table as "ILLUSTRATIVE - actual values TBD by team"

---

### 3. Numerical NAV Impairment Example (27.6%)

**What I wrote:**
```
NAV_base ≈ $22.8M
NPV_climate ≈ $16.5M
NAV Impairment = 27.6%
```

**Reality:** This is MY worked example to show how the calculation would work. The team's proposal does NOT include a specific NAV impairment calculation.

**Correction:** Mark clearly as "ILLUSTRATIVE WORKED EXAMPLE - not team's calculation"

---

### 4. SCVR Values

**What I wrote:**
```
Climate Stresses in 2030-2050 (average):
  • Temperature extremes: SCVR = +20%
  • Freeze/thaw cycles: SCVR = +15%
  • Humidity: SCVR = +10%
```

**Reality:** These are MY ILLUSTRATIVE numbers. The team will compute actual SCVR values from CMIP data in Step 1.

**Action:** Mark as "ILLUSTRATIVE - actual values computed from climate data"

---

## Items That ARE Accurate (From Team's Proposal)

### ✅ Correctly Quoted From Team:

1. **WACC = 10% discount rate** - Team stated: "[10%] is used as the annual discount rate for NPV calculations, representing the Weighted Average Cost of Capital (WACC)."

2. **EUL = 25 years (Solar), 35 years (Wind)** - Team stated: "Expected Useful Life will be 25 years for Solar and 35 years for Wind"

3. **Sample Sites** - Team stated:
   - Hayhurst Texas Solar (Culberson, TX) - 24.8 MW - 31.815992, -104.0853
   - Maverick Creek Wind (Concho, TX) - 491.6 MW - 31.262546, -99.84396

4. **What's NOT included** - Team stated:
   - Physical damage costs (only BI)
   - Catastrophic events (hurricane, wildfire)
   - Price impacts from climate/hazards
   - OpEx/maintenance changes

5. **Scientific Formulas** - Team provided these in Appendix 2:
   - Temperature Coefficient: P_actual = P_rated × [1 + γ × (T_cell − T_ref)]
   - Peck's Model: η = exp(γ0 + γ1 × ln(hr) + γ2 / T_mod)
   - Coffin-Manson: N_f = C × (Δε_p)^(-k)
   - Palmgren-Miner: D = Σ(n_i / N_i)

6. **Climate Metrics Definitions** - Team provided standard definitions for:
   - Heat Wave: 3+ consecutive days T_max/T_min > P90
   - Cold Wave: 3+ consecutive days T_max/T_min < P10
   - Freeze/Frost: Days with T_min < 0°C
   - Icing Condition: T < 0°C AND RH > 75%

---

## Technical Claims Requiring External Verification

### 1. Temperature Coefficient Range

**My claim:** γ = -0.003 to -0.005 per °C

**Status:** This is standard for crystalline silicon PV. SHOULD VERIFY against IEC 61215 standard or manufacturer datasheets.

**Verification Source Needed:** IEC 61215, PVsyst documentation, or specific module datasheet

---

### 2. Solar PV Degradation Rate (0.5%/year)

**Claim in my analysis:** "Degradation: -0.5%/year for solar"

**Team's proposal reference:** Jordan & Kurtz NREL study (2013)

**Status:** This is a well-known reference. The median degradation rate from Jordan & Kurtz analysis of 2000+ studies was approximately 0.5%/year.

**Verification Status:** ✅ LIKELY CORRECT - standard industry reference
**Should verify:** Read Jordan & Kurtz (2013) to confirm exact median value

---

### 3. 10% WACC Appropriateness

**My concern:** "10% WACC is high for renewable energy (typically 6-8%)"

**Status:** NEEDS VERIFICATION

**Reality Check:**
- Debt financing for utility-scale solar: 4-6% (as of 2024-2025)
- Equity returns: 8-15% depending on risk
- Blended WACC depends on debt/equity ratio

**For CONTRACTED renewables (PPA):** 6-8% WACC is more typical
**For MERCHANT renewables:** Higher WACC (8-12%) may be appropriate

**Recommendation:** 
- The team should specify WHY 10% was chosen
- 10% is CONSERVATIVE (makes climate risk look smaller)
- For sensitivity analysis, show 6%, 8%, 10% scenarios

---

### 4. Wind Turbine Cut-Out Speed

**My claim:** "If Wind_mean > 25 m/s, then Power = 0"

**Status:** This is APPROXIMATELY correct but oversimplified.

**Reality:**
- Cut-out speeds vary by turbine: typically 22-28 m/s
- Modern turbines have "storm control" modes that reduce speed threshold for grid stability
- 25 m/s is a reasonable default, but should be turbine-specific

**Recommendation:** Specify actual turbine models at sample sites and use their specific cut-out speeds.

---

### 5. Icing Loss Factor Range

**My claim:** "L_ice = 0.2 to 0.8"

**Status:** This is from PMC8545448 (cited by team). SHOULD VERIFY the source directly.

**Concern:** 0.2-0.8 is a VERY wide range. For the pilot, the team should:
- Choose a point estimate (e.g., 0.5 as moderate assumption)
- Or show sensitivity analysis across range

---

### 6. Wind Useful Life (35 years)

**My concern:** Most sources cite 20-25 years for wind turbines, not 35 years.

**Status:** NEEDS VERIFICATION

**Industry Standard:**
- NREL typically assumes 20-25 year asset life for wind
- Some newer turbines rated for 25-30 years
- 35 years seems OPTIMISTIC

**Recommendation:** 
- Verify source for 35-year wind EUL
- Consider using 25 years as default (more conservative)
- Or justify 35 years based on specific equipment specs

---

## Summary of Required Corrections

### CRITICAL (Must Fix):

1. **CMIP5 vs CMIP6 Clarification**
   - Add note that team's proposal references CMIP5, not CMIP6
   - Do not conflate rsds availability across different CMIP generations
   - Ask team to clarify intended data source

2. **Mark Illustrative Examples Clearly**
   - All EFR values (0.5%, 0.3%, 0.2%)
   - All HCR values (+8%, +30%, etc.)
   - All SCVR values (+20%, +15%, +10%)
   - NAV impairment example (27.6%)

### MODERATE (Should Address):

3. **Wind EUL (35 years)**
   - Verify this is reasonable or provide source
   - 25 years is more standard

4. **WACC Sensitivity**
   - Show range (6%, 8%, 10%) rather than single value
   - 10% is conservative but may be high for contracted assets

### MINOR (Nice to Have):

5. **Turbine-Specific Parameters**
   - Cut-out speeds
   - Power curves
   - Specific equipment at sample sites

---

## Corrected Analysis Document Status

After these corrections, the analysis document should:

1. ✅ Accurately reflect what the TEAM proposed
2. ✅ Clearly mark what I ADDED as illustrative
3. ✅ Note the CMIP5 vs CMIP6 clarification needed
4. ✅ Flag items requiring external verification
5. ✅ Show appropriate uncertainty/ranges where relevant

---

*This verification log should be reviewed by the team to confirm accuracy of the analysis document.*


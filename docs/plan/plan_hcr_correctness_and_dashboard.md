# HCR Correctness Review & Dashboard Integration Plan

## Context

The LTRisk pipeline computes NAV impairment for renewable energy assets: **SCVR → HCR → EFR → NAV**. SCVR (Stage 2) is complete and live on the Streamlit dashboard. HCR (Stage 3) is implemented in NB04 with outputs committed, but a thorough review has uncovered correctness issues that must be fixed before adding HCR to the dashboard and proceeding to EFR.

---

## Part 1: Correctness Issues Found

### Issue 1 — freeze_thaw HCR direction is WRONG (Critical)

| | Pathway A (used) | Pathway B (actual counts) |
|---|---|---|
| SSP245 | **+14.4%** (more events) | 45.71 → 34.31 days/yr = **−25%** |
| SSP585 | **+17.4%** (more events) | 45.71 → 31.55 days/yr = **−31%** |

**Root cause:** `HCR = SCVR_tasmin × 1.0`. Tasmin SCVR is positive (nights warming faster), so HCR comes out positive. But warming **reduces** 0°C crossings — fewer days where `tasmin < 0 AND tasmax > 0`.

**Fix:** Either:
- (a) Change freeze_thaw scaling from `+1.0` to a negative value (e.g., `−1.0`), OR
- (b) Route freeze_thaw to Pathway B (which already shows the correct direction)
- **Recommended: (b)** — Pathway B captures the actual physical mechanism. Freeze-thaw depends on a specific 0°C threshold crossing, not a linear scaling of mean shift.

### Issue 2 — Three hazards produce IDENTICAL HCR values

frost_days, cold_wave, and ice_storm all output **−0.043243** (SSP245) and **−0.05207** (SSP585).

**Root cause:** All three use `SCVR_tasmin × −0.3` — same input variable, same scaling factor.

**Problem:** These hazards have very different physical sensitivities:
- **Frost days** (simple: tasmin < 0°C) — should decrease moderately with warming
- **Cold waves** (compound: 3+ consecutive days, both temps < P10) — should decrease MORE (compound events are rarer and more sensitive)
- **Ice storms** (4-way compound: tasmin < 0, tasmax > 0, pr > 0.5mm, hurs > 85%) — should decrease differently based on all 4 variables

**Fix:** Route cold_wave and ice_storm to Pathway B for differentiated HCR values. Keep frost_days on Pathway A if scaling is validated, or also route to B.

### Issue 3 — fire_weather sign conflict under SSP585

| | Pathway A (used) | Pathway B counts |
|---|---|---|
| SSP245 | +10.3% | 33.81 → 34.10 (+0.9% actual) |
| SSP585 | +12.0% | 33.81 → 33.37 (**−1.3% actual**) |

**Root cause:** The FWI proxy (composite of 4 variables) under SSP585 may flip sign because humidity and precipitation changes counteract temperature increase at this site.

**Fix:** Route fire_weather to Pathway B (at least for SSP585), or flag with a confidence warning. The 1.5× scaling doesn't capture the multivariate interaction.

### Issue 4 — Pathway routing should be expanded

**Current routing:** All temperature/proxy hazards → Pathway A, all precipitation → Pathway B.

**Proposed routing update:**

| Hazard | Current | Proposed | Reason |
|--------|---------|----------|--------|
| heat_wave | A | **A** (keep) | 2.5× validated by Pathway B cross-check |
| cold_wave | A | **B** | Compound event, differentiated from frost_days |
| frost_days | A | **A or B** | Simple threshold, A is OK if scaling validated |
| freeze_thaw | A | **B** | Wrong sign on Pathway A (Issue 1) |
| extreme_precip | B | **B** (keep) | Jensen's inequality, SCVR ≈ 0 |
| flood_rx5day | B | **B** (keep) | Same |
| dry_spell | B | **B** (keep) | Same |
| fire_weather | A | **B** | Sign conflict under SSP585 (Issue 3) |
| ice_storm | A | **B** | Compound event, identical to frost_days on A |
| wind_extreme | A | **A** (keep) | Low signal either way, 0 baseline days |

**Net effect:** 4 more hazards route to Pathway B (cold_wave, freeze_thaw, fire_weather, ice_storm).

---

## Part 2: Notebook Fixes (NB04)

### Step 2.1 — Update HAZARD_CONFIG routing
- In the routing cell, change freeze_thaw, cold_wave, fire_weather, ice_storm to Pathway B
- Keep heat_wave on A (validated), wind_extreme on A (negligible signal)

### Step 2.2 — Update scaling factors for Pathway A hazards still on A
- heat_wave: **2.5** (keep — cross-validated)
- frost_days: Update from −0.3 to **implied scaling from Pathway B** (recalibrate)
- wind_extreme: **1.0** (keep — near-zero signal)

### Step 2.3 — Re-run NB04 and regenerate outputs
- Re-execute all cells
- Verify freeze_thaw HCR is now negative
- Verify cold_wave ≠ frost_days ≠ ice_storm (differentiated values)
- Verify fire_weather SSP585 direction matches empirical counts
- Regenerate `hcr_annual.parquet` and `hcr_results.json`

### Step 2.4 — Update cross-validation table and plots
- The cross-validation cells should now show closer A≈B agreement for remaining Pathway A hazards
- Document the routing change rationale in the notebook markdown cells

---

## Part 3: Dashboard Integration

### Step 3.1 — Add HCR data loading to dashboard
- File: `scripts/presentation/scvr_dashboard.py`
- Read `data/output/hcr/<site_id>/hcr_results.json` and `hcr_annual.parquet`
- Follow same pattern as SCVR data loading

### Step 3.2 — HCR Summary Card
- Show 10 hazards with severity color coding (similar to SCVR variable cards)
- Display: hazard name, epoch HCR (%), direction arrow (↑ worsening / ↓ improving), confidence badge
- Color: red = worsening hazard, blue = improving (e.g., frost reduction)

### Step 3.3 — HCR Timeline Plot
- Annual HCR progression (2026–2055) per hazard
- SSP245 vs SSP585 comparison (solid vs dashed lines)
- Split into positive hazards (top) and negative hazards (bottom)
- Reuse Plotly charting pattern from SCVR section

### Step 3.4 — HCR Heatmap
- 10 hazards × 30 years, color-coded by HCR magnitude
- Red (positive/worsening) to Blue (negative/improving)
- Shows full hazard evolution at a glance

### Step 3.5 — Pathway routing & confidence display
- Show which pathway was used per hazard and why
- Display absolute counts (baseline vs future days/yr) for interpretability
- Methodology expander (similar to SCVR methodology section)

---

## Part 4: Verification

- [ ] freeze_thaw HCR is negative (matches physical reality)
- [ ] cold_wave, frost_days, ice_storm have differentiated HCR values
- [ ] fire_weather SSP585 direction matches Pathway B empirical counts
- [ ] heat_wave HCR unchanged (~17% SSP245, ~20% SSP585)
- [ ] Precipitation hazards unchanged (already on Pathway B)
- [ ] Dashboard loads and renders HCR section without errors
- [ ] All 10 hazards × 2 scenarios × 30 years visible in timeline
- [ ] Heatmap renders with correct color scale

---

## Open Questions for Team

1. **frost_days routing:** Keep on Pathway A with recalibrated scaling, or move to Pathway B for consistency?
2. **wind_extreme:** Currently 0 baseline days at Hayhurst (15 m/s threshold never exceeded for daily mean). Drop from dashboard display, or show with "N/A" badge?
3. **Scaling factor recalibration:** Should we update doc 07 scaling factors based on NB04 Pathway B implied values? Or keep docs as-is and let notebook override?

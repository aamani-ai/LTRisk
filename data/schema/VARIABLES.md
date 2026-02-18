# Climate Variables — Reference Guide

Human-readable companion to `variables.json`.  
Last verified: 2026-02-18 via `scripts/tests/probe_openmeteo_variables.py`.

---

## Priority Tiers

| Tier | Meaning |
|---|---|
| **P1 — Core** | Required for SCVR computation. Notebook 01 cannot run without these. |
| **P2 — Performance** | Required for Pathway B (asset generation modeling). Not needed for SCVR alone. |
| **P3 — Additional** | Improves model quality; can be deferred to later notebooks. |

---

## P1 — Core Variables (SCVR)

These 6 variables feed directly into the SCVR calculation and the extreme indices
(heat waves, frost days, dry spells, wind cut-out days, Fire Weather Index).

| Variable | Full Name | Unit | Open-Meteo Param | Confirmed? | Used For |
|---|---|---|---|---|---|
| `tasmax` | Daily Max Temperature | °C | `temperature_2m_max` | ✅ Yes | Heat waves, icing days, EFR temp coefficient |
| `tasmin` | Daily Min Temperature | °C | `temperature_2m_min` | ✅ Yes | Cold waves, frost days, freeze-thaw EFR |
| `tas` | Daily Mean Temperature | °C | `temperature_2m_mean` | ✅ Yes | Peck's aging model, FWI, trend check |
| `pr` | Daily Precipitation | mm/day | `precipitation_sum` | ✅ Yes | Flood HCR (Rx5day), dry spells, FWI |
| `sfcWind` | Daily Mean Wind Speed | m/s | `wind_speed_10m_mean` | ✅ Yes | Wind extremes, cut-out days, Palmgren-Miner |
| `hurs` | Daily Mean Rel. Humidity | % | `relative_humidity_2m_mean` | ✅ Yes | Peck's model, icing condition (T<0 AND RH>75%) |

> **Note on `tas`:** Available directly from the API. Can also be derived as `(tasmax + tasmin) / 2`
> as a fallback if a future model does not provide it.

---

## P2 — Performance Variable

Required for Pathway B (solar generation modeling with pvlib). Not needed for SCVR.

| Variable | Full Name | Unit | Open-Meteo Param | Confirmed? | Used For |
|---|---|---|---|---|---|
| `rsds` | Surface Downwelling Shortwave Radiation | MJ/m²/day | `shortwave_radiation_sum` | ✅ Yes | Direct GHI input to pvlib; solar performance model |

> **Model caveat:** `CMCC_CM2_VHR4` does **not** provide `rsds`. Always use `EC_Earth3P_HR`
> or another confirmed model when solar performance is needed.

---

## P3 — Additional Variables

Available from the API but not used in current notebooks. Noted for future work.

| Variable | Open-Meteo Param | Notes |
|---|---|---|
| `wind_speed_10m_max` | `wind_speed_10m_max` | Better gust proxy than daily mean; for structural fatigue HCR calibration |
| `cloud_cover_mean` | `cloud_cover_mean` | Correlated with rsds; useful for solar model cross-check |
| `et0_fao_evapotranspiration_sum` | `et0_fao_evapotranspiration_sum` | Drought index; relevant to wildfire fuel drying |
| `soil_moisture_0_to_10cm_mean` | `soil_moisture_0_to_10cm_mean` | Wildfire risk context; vegetation dryness |

> NOAA ground station data (`tmax`, `tmin`, `prcp`, `awnd`) is also P3 — validation only.
> See `noaa_schema.json`.

---

## Confirmed Working Models

Verified by `scripts/tests/probe_openmeteo_variables.py` against the
Open-Meteo Climate API (`climate-api.open-meteo.com`).

| Model | All P1+P2 vars? | rsds? | Historical range | Future range | Notes |
|---|---|---|---|---|---|
| `EC_Earth3P_HR` | ✅ All 7 | ✅ Yes | 1950–2014 | 2015–2050 | **Primary model. Use this.** |
| `NICAM16_8S` | ✅ All 7 | ✅ Yes | 1950–2014 | 2015–2050 | Good ensemble alternative |
| `FGOALS_f3_H` | ✅ All 7 | ✅ Yes | 1950–2014 | 2015–2050 | Good ensemble alternative |
| `HiRAM_SIT_HR` | ✅ All 7 | ✅ Yes | 1950–2014 | 2015–2050 | Good ensemble alternative |
| `CMCC_CM2_VHR4` | ⚠️ 6/7 | ❌ No rsds | 1950–2014 | 2015–2050 | Missing rsds — do not use for solar |
| `MRI_ESM2_0` | ❌ Invalid | — | — | — | **Invalid model name on this API** |
| `MPI_ESM1_2_HR` | ❌ Invalid | — | — | — | **Invalid model name on this API** |

---

## ERA5 Archive (Observational Baseline — Optional)

The Open-Meteo **archive API** (`archive-api.open-meteo.com`) provides ERA5
reanalysis data (actual observations, not a climate model).

| Variable | Available? | Notes |
|---|---|---|
| `tasmax`, `tasmin`, `tas` | ✅ Yes | |
| `pr` | ✅ Yes | |
| `sfcWind` (`wind_speed_10m_mean`) | ✅ Yes | |
| `hurs` (`relative_humidity_2m_mean`) | ✅ Yes | |
| `rsds` (`shortwave_radiation_sum`) | ✅ Yes | |

> **When to use ERA5:** Only for cross-validation of the CMIP6 historical run.
> For SCVR computation, use the CMIP6 model's own historical run (same model → apples-to-apples).
> Do **not** use ERA5 as the baseline when comparing to a CMIP6 future projection.
> The archive API requires **no `models` parameter** — omit it from the request.

---

## SCVR Computation Logic (Variable → Index → SCVR)

```
tasmax  ──►  heat_wave_days   ──►  SCVR_heat_wave
            icing_days        ──►  SCVR_icing

tasmin  ──►  frost_days       ──►  SCVR_frost
            (+ tasmax for heat/cold wave detection)

pr      ──►  rx5day           ──►  SCVR_precip_extreme
            max_dry_days      ──►  SCVR_dry_spell

sfcWind ──►  wind_cutout_days ──►  SCVR_wind_extreme

hurs  ─┐
tas   ─┼─►  FWI_mean         ──►  SCVR_fire_weather
sfcWind┤
pr    ─┘

SCVR values ──► HCR (Hazard Change Ratio)  ──► BI losses
             └► EFR (Equipment Failure Ratio) ──► IUL shortening
```

---

## Downstream Use Map

| SCVR Index | → HCR Hazard | → EFR Mechanism |
|---|---|---|
| `heat_wave_days` / `tasmax` | — | Temp coefficient power loss; Peck's aging |
| `frost_days` + `heat_wave_days` | Icing (rime/glaze) | Coffin-Manson freeze-thaw fatigue |
| `rx5day` (precip extreme) | Pluvial flood, hail | — |
| `max_dry_days` | Dust storm (soiling) | — |
| `wind_cutout_days` | Structural damage | Palmgren-Miner fatigue |
| `FWI_mean` | Wildfire | — |

---

*Source of truth for variable definitions: `variables.json`*  
*Source of truth for column dtypes: `cmip6_raw_schema.json`*  
*API verification log: `scripts/tests/probe_results.json`*

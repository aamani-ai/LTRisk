# Climate Science Fundamentals

> This guide covers the basic climate science concepts you need to understand before diving into the LTRisk codebase. No prior climate science knowledge is assumed.

---

## 1. Climate vs Weather

These two words mean very different things:

| | Weather | Climate |
|---|---|---|
| **What** | Atmospheric conditions right now (or this week) | Statistical summary of weather over decades |
| **Timescale** | Hours to ~10 days | 30+ years |
| **Predictable?** | Only a few days ahead | Trends are predictable decades ahead |
| **Example** | "It will rain in Austin on Tuesday" | "Austin gets ~34 inches of rain per year, trending upward" |

**Why this matters for LTRisk**: We never predict individual weather events. We predict how the *statistical distribution* of weather shifts over the lifetime of an asset (30 years). A solar farm doesn't care if July 14, 2041 is hot — it cares if the *overall frequency of extreme heat days* increases.

---

## 2. The Greenhouse Effect

The basic physics driving everything in this project:

```
                    SUNLIGHT
                       |
                       v
    =====================================
    |           ATMOSPHERE              |  <-- greenhouse gases (CO2, CH4, N2O)
    =====================================
                       |
                       v
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    |           EARTH SURFACE           |
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                       |
                       v
              INFRARED RADIATION
              (heat radiating back up)
                       |
                       v
    =====================================
    |           ATMOSPHERE              |  <-- traps some of this heat
    |     CO2: 280 ppm (1850)           |      and re-radiates it back down
    |     CO2: 425 ppm (2024)           |
    =====================================
                       |
              some escapes to space
              (less than before)
```

**How it works**:
1. Sunlight passes through the atmosphere and warms the Earth's surface
2. The surface radiates heat (infrared) back upward
3. Greenhouse gases in the atmosphere **absorb and re-emit** some of this heat
4. More greenhouse gases = more heat trapped = warmer planet

**The numbers**:
- Pre-industrial CO2: ~280 ppm (parts per million)
- Current CO2: ~425 ppm (52% higher)
- This has already caused ~1.2C of global warming
- Every additional degree has compounding effects on extreme weather

---

## 3. What "Global Warming" Actually Means for Assets

Global warming is not uniform. The global average temperature has risen ~1.2C, but:

```
WARMING IS NOT UNIFORM

                              Arctic: +3 to +4C
                                  /
Global average: +1.2C --------- Land: +1.7C (faster than oceans)
                                  \
                              Oceans: +0.8C (absorb heat slowly)

AND within "land":
  - Desert/arid zones: more extreme heat peaks
  - Coastal zones: sea level + hurricane intensity
  - Continental interiors: wider temperature swings
```

**For Texas specifically** (where our assets are):
- Summer maximum temperatures: increasing
- Winter minimum temperatures: ALSO increasing (fewer freeze days overall, BUT more extreme cold snaps when polar vortex disrupts — see Texas Feb 2021)
- Precipitation: more intense bursts, longer dry spells (both extremes get worse)
- Wind patterns: complex — slight changes in mean, potentially more variability

---

## 4. The Six Climate Variables We Track

These are the variables that directly affect solar and wind infrastructure:

### Temperature Variables

```
Daily Temperature Profile

Temp  40C ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  * ─ ─ ─ ─  <- tasmax (daily maximum)
(C)       |                    / \
      35C |                   /   \
          |                  /     \
      30C |        ________/       \______  <- tas (daily mean)
          |       /
      25C |      /
          |     /
      20C | ──*─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  <- tasmin (daily minimum)
          └──────────────────────────────────
          midnight  6am    noon    6pm    midnight
```

| Variable | Full Name | Unit | Why It Matters |
|---|---|---|---|
| **tasmax** | Daily Maximum Temperature | C | Heat stress on panels, icing detection (tasmax < 0C) |
| **tasmin** | Daily Minimum Temperature | C | Frost days (tasmin < 0C), freeze-thaw cycling |
| **tas** | Daily Mean Temperature | C | Overall thermal aging (Peck's model), fire weather |

### Other Variables

| Variable | Full Name | Unit | Why It Matters |
|---|---|---|---|
| **pr** | Daily Precipitation | mm/day | Flood risk (extreme rain), dry spell risk (soiling, fire) |
| **sfcWind** | Daily Mean Wind Speed | m/s | Turbine cut-out (>25 m/s), structural fatigue |
| **hurs** | Daily Mean Relative Humidity | % | Corrosion, icing (T<0 AND hurs>75%), Peck's aging model |
| **rsds** | Surface Downwelling Shortwave Radiation | MJ/m2/day | Solar energy input (GHI equivalent) — solar sites only |

### Priority Tiers

```
P1_core (required for SCVR):    tasmax, tasmin, tas, pr, sfcWind, hurs
P2_performance (solar only):    rsds
P3_additional (deferred):       wind_speed_10m_max, noaa_tmax
```

---

## 5. What Makes Climate "Extreme"

It's not about averages — it's about the tails of the distribution:

```
DISTRIBUTION OF DAILY MAXIMUM TEMPERATURES

Number
of days
  |
  |          Baseline (1985-2014)
  |              /\
  |             /  \
  |            /    \         Future (2026-2055)
  |           /      \           /\
  |          /        \         /  \
  |         /          \       /    \
  |        /            \     /      \
  |       /              \   /        \
  |      /                \ /          \
  |     /                  X            \
  |    /                  / \            \
  |___/                  /   \____________\___
  └──────────────────────────────────────────── Temperature
       20C    30C    40C    45C    50C

  Normal days              |  EXTREME TAIL  |
  (most of the data)       |  (this is what |
                           |   damages      |
                           |   equipment)   |
```

**Key insight**: A 2C shift in the mean can cause a **much larger** increase in extreme days. If your equipment fails at 45C, and the distribution shifts right by 2C, the number of days above 45C might double or triple — even though the average only moved a little.

This is exactly what SCVR measures: how much the *entire distribution* shifts, with emphasis on the tails.

---

## 6. Feedback Loops and Compound Events

Climate change doesn't just shift one variable — it creates cascading effects:

```
COMPOUND EVENT CHAIN (Texas example)

  Higher temperatures
        |
        v
  Longer dry spells ──────> Soil dries out
        |                        |
        v                        v
  Vegetation dies ──────> Dust/soiling on panels
        |                        |
        v                        v
  Wildfire risk UP          Panel efficiency DOWN
        |
        v
  When rain finally comes:
  dry soil can't absorb ──> Flash flooding
        |
        v
  Infrastructure damage
```

**For our assets**:
- Solar: Heat reduces panel efficiency (roughly -0.4%/C above 25C for crystalline silicon), dust from drought reduces output, hail from intense storms causes physical damage
- Wind: Icing reduces generation and adds structural load, extreme wind causes cut-out (lost generation) or structural failure, temperature swings cause material fatigue

---

## 7. Why 30 Years?

Climate is typically defined over 30-year windows (called "climate normals" by the WMO — World Meteorological Organization):

```
Why 30 years?

Too short (5-10 years):
  ├── Dominated by natural variability (El Nino, volcanic eruptions)
  ├── Cannot distinguish climate signal from noise
  └── Statistically insufficient for tail estimation

Just right (30 years):
  ├── Smooths out inter-annual variability
  ├── ~10,950 daily values per variable per model
  ├── Enough data points for robust exceedance curves
  └── Matches typical asset operational lifespans

Too long (60+ years):
  ├── Climate is actively changing — distant past is irrelevant
  ├── Mixes different climate states together
  └── Exceeds asset lifetime — wasted computation
```

This is why our baseline is 30 years (1985-2014) and our future window is 30 years (2026-2055, matching the asset lifetime).

---

## Next

- [02 - CMIP6 and Climate Models](02_cmip6_and_climate_models.md) — How scientists actually simulate future climate

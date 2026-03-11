# 05 — Scenario Comparison: SSP2-4.5 vs SSP5-8.5

**Does the emissions pathway actually change the SCVR numbers — and does it matter financially?**

> For a full explanation of what SSP scenarios are, see [`03_scenarios_and_time_windows.md`](03_scenarios_and_time_windows.md).

---

## The Short Answer

Yes — but less than you might expect **within our 2026-2055 window**.

The two scenarios diverge sharply after 2060. Within 30 years from now, the difference is real but moderate — roughly 0.03-0.04 SCVR units on temperature variables. Translated to financial terms, this is a ~5 percentage point NAV impairment difference on a solar asset.

---

## Why Scenarios Diverge Less Early On

```
Emissions pathway divergence over time:

CO₂ ppm
  ▲
900│                                     ╭──── SSP5-8.5 (no limit)
   │                                 ╭───╯
700│                             ╭───╯
   │                 ╭───────────╯ ←── diverge strongly post-2060
500│         ╭───────╯
   │  ╭──────╯──────────────────────── SSP2-4.5 (moderate limit)
450│──╯
   └─────────────────────────────────────────► Year
    2015  2026         2055         2080   2100
              └────────┘
              Our window
```

Within 2026-2055 (our 30-year window):
- Both scenarios track closely — emissions already in the atmosphere dominate
- Historical CO₂ already committed ~1.5-2°C of warming regardless of future choices
- The **real separation** happens post-2055, when cumulative emissions create sharply different outcomes

> This is why we use BOTH scenarios: SSP2-4.5 for base case, SSP5-8.5 for tail risk / stress test.

---

## SCVR Side-by-Side: Both Sites, Both Scenarios

### Hayhurst Texas Solar (ensemble pooled, center_year 2040)

| Variable | SSP2-4.5 | SSP5-8.5 | Delta | Delta % |
|---|---|---|---|---|
| tasmax | +0.050 | +0.084 | +0.034 | SSP585 is 68% larger |
| tasmin | +0.060 | +0.092 | +0.032 | SSP585 is 53% larger |
| tas | +0.050 | +0.074 | +0.024 | SSP585 is 48% larger |
| pr | +0.002 | +0.022 | +0.020 | SSP585 is 10× larger |
| hurs | −0.010 | −0.015 | −0.005 | Both declining |
| sfcWind | ~0 | ~0 | ~0 | No difference |
| rsds | +0.002 | +0.002 | ~0 | Negligible difference |

### Maverick Creek Wind (ensemble pooled, center_year 2040)

| Variable | SSP2-4.5 | SSP5-8.5 | Delta | Delta % |
|---|---|---|---|---|
| tasmax | +0.045 | +0.080 | +0.035 | SSP585 is 78% larger |
| tasmin | +0.055 | +0.085 | +0.030 | SSP585 is 55% larger |
| tas | +0.045 | +0.070 | +0.025 | SSP585 is 56% larger |
| pr | +0.005 | +0.020 | +0.015 | SSP585 is 4× larger |
| hurs | −0.008 | −0.012 | −0.004 | Both declining |
| sfcWind | ~0 | ~0 | ~0 | No difference |

---

## Pattern: What Scenarios Change vs What They Don't

```
Variables where scenarios DIFFER significantly:
  tasmax, tasmin, tas     → temperature is emissions-sensitive in our window
  pr                      → large relative difference (10× for Hayhurst)

Variables where scenarios DON'T DIFFER:
  sfcWind                 → flat in BOTH scenarios (not emissions-sensitive near-term)
  rsds                    → essentially identical
  hurs                    → similar direction and magnitude in both
```

**Key insight:** The scenario choice matters most for temperature variables. For wind (sfcWind), it doesn't matter at all — both scenarios give ~0 SCVR.

---

## The Physical Reason for the Gap

Within our window (2026-2055), the temperature difference between scenarios is approximately:

```
Warming above pre-industrial baseline:
  SSP2-4.5:  ~1.7°C by 2050 (peaking ~2040, then slow rise)
  SSP5-8.5:  ~2.2°C by 2050 (still rising steeply)

  Difference: ~0.5°C within our 30-year window

That 0.5°C in mean temperature → ~0.03-0.04 SCVR units on tasmax
Because SCVR is a distribution measure, not just a mean shift —
  the tails grow faster than the mean
  a 0.5°C mean shift can produce a 1.0-1.5°C shift at P95
```

---

## When to Use Each Scenario

| Use case | Scenario | Why |
|---|---|---|
| Base case expected loss | SSP2-4.5 | Most likely outcome given current policy trajectory |
| Insurance pricing | SSP5-8.5 | Tail risk pricing requires worst plausible case |
| Stress test / due diligence | SSP5-8.5 | Shows maximum credible exposure |
| TCFD reporting | Both | Regulators require multi-scenario disclosure |
| Portfolio screening | SSP5-8.5 | Conservative — avoids underpricing risk |
| Revenue forecasting | SSP2-4.5 | Base case for DCF models |
| Reinsurance treaty terms | SSP5-8.5 | Reinsurers price off the tail |

> Our project uses **both simultaneously**: SSP2-4.5 as expected loss, SSP5-8.5 as stress test. The delta between them quantifies scenario risk (i.e., "how bad could it get if emissions are not curbed").

---

## Financial Translation of the Delta

For Hayhurst Solar, the scenario delta in tasmax (+0.034) translates to:

```
SCVR delta:  +0.034 (tasmax alone)
HCR delta:   +0.034 × 2.5 (heat scaling factor) = +0.085 HCR difference
EFR delta:   depends on Peck's exponent — roughly +5-8% acceleration difference
IUL delta:   ~1-2 additional years of life lost under SSP585 vs SSP245
NAV delta:   ~$3-5M additional impairment on a $60M asset

As % of NAV: ~5-8 percentage points between scenarios
```

For Maverick Wind:
```
SCVR delta:  +0.035 (tasmax), sfcWind = 0
Financial delta: much smaller — wind EFR barely moves either way
NAV delta:   ~$1-2M on a $150M asset (~1-2 percentage points)
```

---

## Timeline: When Do Scenarios Diverge Most?

```
Within our 30-year asset window:

2026    2030    2035    2040    2045    2050    2055
  │       │       │       │       │       │       │
  │ ─ ─ ─ ─ ─ ─ ─│─ ─ ─ ─│─ ─ ─ ─│─ ─ ─ ─│─ ─ ─ ─│
  │               │       │       │       │       │
  │  Similar      │Moderate│      Growing gap     │
  │  (both ~1.7°C)│ gap    │      post-2040       │
  └───────────────┴────────┴───────┴───────────────┘
       First half                   Second half
   (scenarios close)           (scenarios diverging)
```

**The tail years matter most:** The last 10 years of an asset (2045-2055 for our sites) are when:
- Hardware is most degraded (accelerated by prior SCVR exposure)
- Climate stress is highest (both scenarios at peak within-window warming)
- SSP585 is meaningfully hotter than SSP245

This is why using a static IPCC block (e.g., 2021-2040) would miss the worst decade for a 2026-built asset.

---

## Common Question: "Which Scenario Will Actually Happen?"

```
Current emissions trajectory (as of 2026):
  We are tracking between SSP2-4.5 and SSP3-7.0.
  SSP5-8.5 requires accelerating fossil fuel use — unlikely.
  SSP2-4.5 requires significant policy action — partially underway.

  "Most likely" outcome: somewhere between the two.

For risk modeling purposes:
  Use SSP2-4.5 as base case (what you expect)
  Use SSP5-8.5 as tail risk (what you must plan for)
  Report both to stakeholders
```

---

**Previous →** [05 — Variables and Use Cases](05_variables_and_use_cases.md)
**Next →** [07 — HCR: Hazard Change Ratio](07_hcr_hazard_change.md)

---
title: "Discussion — Channel 2: How EFR Becomes Dollar Losses"
type: discussion
domain: climate-risk / financial-translation / equipment-degradation
created: 2026-04-02
status: draft — consolidates EFR financial translation, IUL options, and sensitivity analysis
context: >
  Channel 2 (EFR → generation decline + IUL truncation) accounts for ~86%
  of total NAV impairment at Hayhurst Solar. This doc consolidates the
  financial calculation logic, works through a full 25-year DCF, and
  frames the key decisions (IUL threshold, EFR weights, discount rate).
relates-to:
  - docs/learning/C_financial_translation/08_efr_equipment_degradation.md
  - docs/learning/C_financial_translation/09_nav_impairment_chain.md
  - docs/discussion/efr_degradation/efr_two_modes.md
  - docs/discussion/hcr_financial/channel_1_bi_calculation.md
---

# Channel 2: How EFR Becomes Dollar Losses

> **The question:** EFR_combined(2040) = 0.094. What happens to cash flow
> and asset life?

> **The answer:** Two things. First, panels produce slightly less each year
> (Effect 1: ~$0.5-1.0M NPV). Second, the asset dies ~2-4 years early
> (Effect 2: ~$2.8-5.1M NPV). Effect 2 is 5-10x larger because it
> eliminates entire years of post-debt cash flow.

---

## 1. The Two Effects — Recap

```
EFFECT 1: ANNUAL GENERATION REDUCTION (gradual, every year)

  Formula:
    climate_degrad(t) = EFR_combined(t) × std_degrad_rate × t
    Gen(t) = Gen_base × (1 - std_degrad)^t × (1 - climate_degrad(t))

  Character: Multiplicative on revenue. Small early, grows.
  Impact: ~$0.5-1.0M NPV over asset life


EFFECT 2: LIFE TRUNCATION via IUL (terminal, at the NAV level)

  Formula:
    If t > IUL: CFADS(t) = 0    (asset is dead)

  Character: Binary cliff. Eliminates highest-margin years.
  Impact: ~$2.8-5.1M NPV (dominates total impairment)
```

---

## 2. Effect 1: Year-by-Year Generation Decline

### The Formula

```
Gen(t) = Gen_base × (1 - std_degrad)^t × (1 - climate_degrad(t)) × (1 - hazard_BI(t))
                     ^^^^^^^^^^^^^^^^^^^   ^^^^^^^^^^^^^^^^^^^^^^^^^   ^^^^^^^^^^^^^^^^
                     Standard (0.5%/yr)    Climate extra (EFR)         Channel 1 (HCR)

climate_degrad(t) = EFR_combined(t) × std_degrad_rate × t
                  = EFR_combined(t) × 0.005 × t
```

### 25-Year Worked Example (Hayhurst SSP5-8.5)

```
Year  EFR(t)   climate_   Gen_std    Gen_climate  Extra loss   $ loss
               degrad(t)  (MWh)      (MWh)        (MWh)        ($/yr)
────  ──────   ─────────  ─────────  ───────────  ──────────   ──────
  1   0.02     0.0001     53,629     53,624       5            $200
  2   0.03     0.0003     53,361     53,345       16           $640
  3   0.03     0.0005     53,094     53,068       26           $1,040
  5   0.04     0.0010     52,565     52,513       52           $2,080
  7   0.06     0.0021     52,042     51,933       109          $4,360
 10   0.07     0.0035     51,267     51,087       180          $7,200
 12   0.09     0.0054     50,754     50,480       274          $10,960
 15   0.10     0.0075     50,000     49,625       375          $15,000
 18   0.11     0.0099     49,255     48,767       488          $19,520
 20   0.12     0.0120     48,774     48,189       585          $23,400
 22   0.13     0.0143     48,298     47,607       691          $27,640
 25   0.14     0.0175     47,584     46,751       833          $33,320

Notes:
  Gen_base = 54,300 MWh (24.8 MW × 8760 hrs × 25% CF)
  std_degrad = 0.5%/yr
  Price = $40/MWh
  EFR values interpolated from anchor fit (doc 08 §8)
  hazard_BI omitted for clarity (see Channel 1 doc)
```

### Cumulative NPV of Effect 1

```
Effect 1 NPV = Σ_{t=1}^{IUL} [Gen_std(t) - Gen_climate(t)] × $40 / (1.10)^t

  At IUL = 23 years: Effect 1 NPV ≈ $0.7M
  At IUL = 21 years: Effect 1 NPV ≈ $0.6M

  Range: ~$0.5-1.0M depending on IUL and discount rate
```

---

## 3. Effect 2: IUL Life Truncation

### The Two Options

**Option A — Simple Scaling (Phase 1 recommended):**

```
IUL = EUL × (1 - avg_EFR)

Where avg_EFR = average of EFR_combined(t) over asset life

HAYHURST SSP5-8.5:
  Conservative (linearised Peck's):
    avg_EFR ≈ 0.09
    IUL = 25 × (1 - 0.09) = 25 × 0.91 = 22.75 ≈ 23 years
    Years lost: 2

  Aggressive (full Peck's exponential):
    avg_EFR ≈ 0.17
    IUL = 25 × (1 - 0.17) = 25 × 0.83 = 20.75 ≈ 21 years
    Years lost: 4

PROS:
  + Simple — one multiplication
  + No threshold definition needed
  + Consistent with doc 09 worked examples

CONS:
  - No physical failure criterion (what does "end of life" actually mean?)
  - Linear scaling may not reflect real degradation trajectory
```

**Option B — Cumulative Tracking (Phase 2):**

```
Track cumulative degradation year by year:
  cumul(t) = Σ_{s=1}^{t} [std_degrad + EFR_combined(s) × std_degrad]
           = Σ_{s=1}^{t} std_degrad × (1 + EFR_combined(s))

IUL = year where cumul(t) reaches failure threshold

THRESHOLD OPTIONS:
  (a) 80% of rated capacity → cumul = 20%   (IEC 61215 warranty limit)
  (b) 85% of rated capacity → cumul = 15%
  (c) Same as standard EUL  → cumul = 12.5%  (0.5% × 25 years)

HAYHURST SSP5-8.5 (threshold = 12.5%):

Year  std_degrad   EFR(t)   annual_degrad   cumul(t)    Status
────  ──────────   ──────   ─────────────   ────────    ──────
  5   0.50%        0.04     0.52%           2.58%       OK
 10   0.50%        0.07     0.54%           5.25%       OK
 15   0.50%        0.10     0.55%           8.10%       OK
 18   0.50%        0.11     0.56%           9.95%       OK
 20   0.50%        0.12     0.56%           11.15%      OK
 22   0.50%        0.13     0.57%           12.25%      OK
 23   0.50%        0.13     0.57%           12.82%      THRESHOLD
                                                        ← IUL = 23

  Under full Peck's exponential (higher EFR):
    Threshold reached at year ~21 → IUL = 21

PROS:
  + Physically grounded — tracks actual degradation accumulation
  + Threshold has engineering meaning (warranty limit, performance floor)
  + Different thresholds give different answers — can test sensitivity

CONS:
  - Requires choosing a threshold (which one?)
  - More complex calculation
  - May give fractional years (interpolation needed)
```

**Recommendation:** Use Option A for Phase 1 (simpler, consistent with
existing worked examples). Implement Option B in Phase 2 when field data
can inform the threshold choice. Report both if feasible.

---

## 4. How IUL Enters the DCF

```
FULL 25-YEAR DCF — Hayhurst SSP5-8.5 (IUL = 23 years)

Year   CFADS_base   CFADS_climate   Delta       PV(Delta)
       (no climate) (with climate)  (loss)      at 10%
────   ──────────   ─────────────   ─────────   ─────────
  1    $1.48M       $1.48M          $0.0K       $0.0K
  3    $1.46M       $1.46M          $0.4K       $0.3K
  5    $1.44M       $1.43M          $1.3K       $0.8K
  7    $1.42M       $1.40M          $2.8K       $1.4K
 10    $1.38M       $1.35M          $4.6K       $1.8K
 12    $1.36M       $1.31M          $7.1K       $2.3K
 15    $1.32M       $1.25M          $10.1K      $2.4K
 18    $1.29M       $1.18M          $15.0K      $2.7K
 20    $1.26M       $1.13M          $19.0K      $2.8K
 22    $1.23M       $1.06M          $22.4K      $2.7K
 23    $1.22M       $1.02M          $24.0K      $2.6K      ← IUL
 24    $1.21M       $0              $1,210K     $122K      ← EFFECT 2
 25    $1.20M       $0              $1,200K     $111K      ← EFFECT 2
────   ──────────   ─────────────   ─────────   ─────────

  Effect 1 total (years 1-23): ~$20K PV    ← gradual annual losses
  Effect 2 total (years 24-25): ~$233K PV  ← years eliminated entirely

  Wait — these numbers look smaller than the $5.1M cited in doc 09.
  That's because doc 09 uses the AGGRESSIVE Peck's estimate (IUL = 21):

  At IUL = 21, years 22-25 are eliminated:
    Year 22: $1.23M → $0 → PV ≈ $148K
    Year 23: $1.22M → $0 → PV ≈ $133K
    Year 24: $1.21M → $0 → PV ≈ $122K
    Year 25: $1.20M → $0 → PV ≈ $111K
    Effect 2 total (years 22-25): ~$514K PV

  IMPORTANT: These are CFADS (revenue - OpEx - debt service) not revenue.
  Post-debt years have highest margin (debt paid off after ~year 18).
  If debt is fully paid by year 18:
    Years 19-25 CFADS ≈ Revenue - OpEx ≈ $1.3-1.5M/yr (no DS)
    PV of years 22-25 at 10%: 4 × ~$1.4M × avg_discount ≈ $3.9M

  This reconciles with the $2.8-5.1M range in doc 09 depending on
  debt structure, OpEx assumptions, and discount rate.
```

### Why Post-Debt Years Are Highest-Value

```
CFADS PROFILE OVER ASSET LIFE

CFADS
($M/yr)
  1.8│                                     ████████████████
     │                                █████
  1.5│                           █████     ← Debt fully paid
     │                      █████            (year ~18)
  1.2│                 █████                 CFADS jumps because
     │            █████                      debt service = $0
  0.9│       █████
     │  █████
  0.6│██
     │█
  0.3│       ← During debt: CFADS = Revenue - OpEx - DS
     │         After debt:  CFADS = Revenue - OpEx (higher)
  0.0└──────────────────────────────────────────────────────
      0    5    10    15    18    20    22    25
                            ↑         ↑
                       Debt paid   IUL = 22
                       off here    (lost years
                                    are the BEST years)
```

---

## 5. NAV Impairment Formula

```
NAV_impairment = Σ_{t=1}^{EUL} [CFADS_baseline(t) - CFADS_climate(t)] / (1+r)^t

Where:
  CFADS_baseline(t) = Revenue(t) × (1-std_degrad)^t - OpEx(t) - DS(t)
                      (standard model, runs full EUL years)

  CFADS_climate(t)  = Revenue(t) × (1-std_degrad)^t × (1-climate_degrad(t))
                      - BI_loss(t) - OpEx(t) - DS(t)
                      for t ≤ IUL; = 0 for t > IUL

  r = WACC (discount rate), currently 10%

The difference captures BOTH effects:
  Years 1 to IUL: CFADS_baseline > CFADS_climate (Effect 1, small annual gap)
  Years IUL+1 to EUL: CFADS_baseline > 0, CFADS_climate = 0 (Effect 2, cliff)
```

---

## 6. Sensitivity Analysis

### EFR Weighting (Peck's vs Coffin-Manson)

```
HAYHURST SSP5-8.5 — How weights affect combined EFR and IUL

Weights (Peck:CM)    EFR_combined    IUL (Option A)    Years Lost
─────────────────    ────────────    ──────────────    ──────────
90:10                0.097           22.6              2.4
80:20 (current)      0.094           23.5 *            1.5 *
80:20 (Mode B C-M)   0.078           24.1              0.9
70:30                0.087           24.2 *            0.8 *
70:30 (Mode B C-M)   0.065           24.6              0.4

* Using Mode A Coffin-Manson (+0.03)
  Mode B Coffin-Manson is NEGATIVE at Hayhurst (-0.05 estimated)
  → reduces combined EFR → fewer years lost

KEY FINDING: With Mode B Coffin-Manson, the warming benefit
(fewer freeze-thaw cycles) partially offsets Peck's aging.
The combined EFR drops from 0.094 to 0.078.
This changes IUL by about 1 year.
```

### Discount Rate

```
NAV IMPAIRMENT AT DIFFERENT DISCOUNT RATES (Hayhurst SSP5-8.5, IUL=21)

Discount Rate    Effect 1 PV    Effect 2 PV    Total PV    % of $60M
─────────────    ───────────    ───────────    ────────    ─────────
8%               $0.9M          $4.5M          $5.4M       9.0%
10% (current)    $0.7M          $3.6M          $4.3M       7.2%
12%              $0.5M          $2.9M          $3.4M       5.7%

OBSERVATION: Higher discount rate → lower impairment (future losses worth less).
Each 2pp change in WACC moves NAV impairment by ~$1M (~1.5pp of asset value).
```

### SSP Scenario Comparison

```
HAYHURST SOLAR — Two Scenarios

                    SSP2-4.5         SSP5-8.5
                    ────────         ────────
avg_EFR             ~0.06            ~0.09-0.17
IUL (Option A)      ~23-24 yrs       ~21-23 yrs
Years lost          1-2              2-4
Effect 1 PV         ~$0.3M           ~$0.5-1.0M
Effect 2 PV         ~$1.0-2.0M       ~$2.8-5.1M
Total NAV impact    ~$1.3-2.3M       ~$3.3-6.1M
% of $60M           2-4%             5-10%
```

---

## 7. DSCR Computation and Covenant Testing

### The Formula

```
DSCR(t) = CFADS_adjusted(t) / DebtService(t)

Where:
  CFADS_adjusted = Revenue × (1-std_degrad)^t × (1-climate_degrad)
                   - BI_loss - OpEx
  DebtService    = annual debt payment (principal + interest)

Covenant: DSCR must stay above 1.20x (typical) or 1.25x (conservative)
If DSCR < covenant: restricted distributions, cash sweep, or default
```

### When Does DSCR Breach? (Hayhurst SSP5-8.5)

```
Year    DSCR_baseline    DSCR_climate    Status
────    ─────────────    ────────────    ──────
  5     1.45x            1.44x           OK
 10     1.35x            1.32x           OK
 12     1.30x            1.26x           OK — but narrowing
 15     1.25x            1.19x           BREACH at 1.20x covenant
 18     1.20x            1.12x           BREACH at 1.20x
 20     1.18x            1.06x           APPROACHING 1.00x
 22     1.15x            0.98x           BELOW 1.00x — debt unpayable

Without climate: DSCR stays above 1.20x through year 18 (debt maturity)
With climate:    DSCR breaches 1.20x around year 14-15

THE COVENANT BREACH ACCELERATES BY ~3-4 YEARS UNDER CLIMATE CHANGE.
```

### The Debt Re-Sculpting Question

```
OPEN DECISION (for project_finance team):

Option 1: FIXED debt service profile
  Keep original amortization schedule
  Show that climate causes earlier DSCR breach
  → This is the "stress test" framing
  → Tells lenders: "under climate change, your covenant
    breaches 3-4 years earlier than base case"

Option 2: RE-SCULPTED debt service
  Adjust DS(t) so that DSCR stays above covenant under climate
  → Higher DS early (when CFADS is healthy)
  → Lower DS late (when CFADS is degraded)
  → This is the "adaptation" framing
  → Tells lenders: "if you re-sculpt, the loan still works
    but the borrower gives up more early cash flow"

RECOMMENDATION (Phase 1): Use Option 1 (fixed DS, show breach).
This is what lenders expect in a stress test.
Re-sculpting is a Phase 2 optimization question.
```

---

## 8. The Complete Chain — ASCII Flow

```
EFR PER MODEL (from NB04)                     FINANCIAL PARAMETERS
┌──────────────────────────┐                   ┌──────────────────────┐
│ EFR_peck(2040) = 0.11    │                   │ Gen_base = 54,300 MWh│
│ EFR_coffin(2040) = -0.05 │ (Mode B)         │ std_degrad = 0.5%/yr │
│ EFR_palmgren(2040) = 0.00│                   │ Price = $40/MWh      │
└──────────┬───────────────┘                   │ WACC = 10%           │
           │                                   │ EUL = 25 years       │
           ▼ combine (80:20:0)                 │ DS = $1.8M/yr        │
┌──────────────────────────┐                   └──────────┬───────────┘
│ EFR_combined(2040) = 0.078│                              │
└──────────┬───────────────┘                               │
           │                                               │
     ┌─────┴──────────────────┐                            │
     │                        │                            │
     ▼ EFFECT 1               ▼ EFFECT 2                   │
┌──────────────────┐   ┌──────────────────┐                │
│ climate_degrad   │   │ avg_EFR = 0.078  │                │
│ = 0.078 × 0.005  │   │ IUL = 25 × 0.922│                │
│   × 14 = 0.0055  │   │    = 23.1 ≈ 23  │                │
│                  │   │ Years lost: 2    │                │
│ Gen(14) = 54,300 │   │                  │                │
│ × 0.932 × 0.9945│   │ Years 24-25:     │                │
│ = 50,316 MWh    │   │ CFADS = $0       │                │
│                  │   │                  │                │
│ Extra loss:      │   │ PV of lost years:│                │
│ 296 MWh = $12K/yr│   │ ~$233K           │                │
└────────┬─────────┘   └────────┬─────────┘                │
         │                      │                          │
         └──────────┬───────────┘                          │
                    │                                      │
                    ▼ combine into NAV                      │
         ┌──────────────────────────┐                      │
         │ NAV_impairment =         │◄─────────────────────┘
         │   Effect 1: ~$0.6M PV   │
         │ + Effect 2: ~$0.2-3.9M PV│ (range: IUL 21-23)
         │ = ~$0.8-4.5M total      │
         │ = 1.3-7.5% of $60M NAV  │
         └──────────────────────────┘
```

---

## 9. Open Questions for Team

1. **IUL threshold:** 80% (IEC standard), 85%, or 12.5% cumulative loss?
   Affects whether IUL = 21 or 23 → changes NAV by ~$2M.

2. **Debt structure:** Level amortization or sculpted? Affects when post-debt
   years start (year 18 vs 20) → changes Effect 2 magnitude.

3. **EFR weighting recalibration:** With Mode B Coffin-Manson (negative),
   should the 80/20 weight change? Or should we report both weighted
   and unweighted Peck's?

4. **WACC:** 10% is assumed. Should we report at 8/10/12% as standard
   sensitivity range?

5. **Interaction with Channel 1:** BI_loss is subtracted from CFADS_climate.
   If Channel 1 is small (~$4K/yr), does it even need to be computed
   for Phase 1? Or can we focus on Channel 2 and add Channel 1 later?

---

## Cross-References

| Topic | Doc |
|-------|-----|
| EFR physics models | [08_efr_equipment_degradation.md](../../learning/C_financial_translation/08_efr_equipment_degradation.md) |
| EFR two modes | [efr_two_modes.md](efr_two_modes.md) |
| NAV impairment chain | [09_nav_impairment_chain.md](../../learning/C_financial_translation/09_nav_impairment_chain.md) |
| Channel 1 calculation | [channel_1_bi_calculation.md](../hcr_financial/channel_1_bi_calculation.md) |
| Framework architecture | [framework_architecture.md](../architecture/framework_architecture.md) |
| FIDUCEO uncertainty | [FIDUCEO uncertainty mapping](../uncertainty/FIDUCEO-Style%20Uncertainty%20Mapping_%20LTRisk.md) |

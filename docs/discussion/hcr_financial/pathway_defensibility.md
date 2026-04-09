---
title: "Discussion — Why Pathway A Is Preferred: Defensibility of Computation Approaches"
type: discussion
domain: climate-risk / methodology / defensibility
created: 2026-04-09
status: final — documents the rationale for the two-pathway architecture
context: >
  A reviewer asked why the framework uses two computation pathways rather
  than standardising on one. This doc explains that Pathway A (SCVR-based
  scaling) is preferred when defensible because it avoids subjective
  threshold definitions, while Pathway B (direct daily counting) is the
  mandatory fallback when A gives mathematically wrong answers. The same
  logic applies to EFR's Mode A/B distinction.
relates-to:
  - docs/learning/C_financial_translation/07_hcr_hazard_change.md
  - docs/discussion/hcr_financial/hcr_pathway_a_vs_b.md
  - docs/discussion/hcr_financial/jensen_inequality_hcr_scvr.md
  - docs/discussion/efr_degradation/efr_two_modes.md
  - docs/learning/C_financial_translation/06b_climate_risk_orchestrator.md
---

# Why Pathway A Is Preferred

> **The question:** "Why not just use Pathway B for everything? It counts
> actual events from daily data — isn't that always more accurate?"

> **The answer:** Pathway B requires you to DEFINE what counts as an event
> — which thresholds, which variable combinations, which durations. Each
> definition choice is subjective, changes the answer by 2-10×, and
> needs its own justification. Pathway A avoids all of this by working
> with the mean shift directly. We prefer A when it works, and fall back
> to B only when A gives wrong answers.

---

## 1. The Two Approaches — What Each Requires From You

### Pathway A: SCVR × Scaling Factor

```
INPUT YOU PROVIDE:
  1. SCVR (computed, not a choice — comes from data)
  2. Scaling factor (from published literature)

EXAMPLE:
  SCVR_tasmax = +0.074 (computed from 28 CMIP6 models, proven = mean ratio)
  Scaling factor = 2.5 (from Diffenbaugh et al. 2017, Cowan et al. 2017)
  HCR_heat = 0.074 × 2.5 = +0.185

WHAT A REVIEWER CAN CHALLENGE:
  "Why 2.5 and not 2.0 or 3.0?"
  → Answer: published range is 2.0-3.0, we use midpoint,
    cross-validated against Pathway B (implied scaling = 2.7, within range)

WHAT A REVIEWER CANNOT CHALLENGE:
  - The SCVR value (it's a mathematical fact from the data)
  - The multiplication (it's arithmetic)
  - The concept (mean shift × amplification = hazard change)

DEFENSIBILITY: HIGH
  Every step traces to data or published literature.
  No subjective threshold definitions.
```

### Pathway B: Direct Threshold Counting

```
INPUT YOU PROVIDE:
  1. Threshold definition (YOUR CHOICE — subjective)
  2. Compound logic (YOUR CHOICE — subjective)
  3. Duration requirement (YOUR CHOICE — subjective)
  4. Daily data (computed, not a choice)

EXAMPLE (heat wave):
  Which threshold?
    Option 1: tasmax > 40°C absolute           → X heat days/year
    Option 2: tasmax > per-DOY P90              → Y heat days/year
    Option 3: tasmax > per-DOY P90 AND
              tasmin > per-DOY P90              → Z heat days/year
    Option 4: same as 3 but require 3+
              consecutive days                  → W heat days/year
  
  At Hayhurst (SSP245):
    Option 1: HCR ≈ +45%    (many days cross 40°C)
    Option 2: HCR ≈ +177%   (P90 exceedance amplification)
    Option 3: HCR ≈ +120%   (compound reduces count)
    Option 4: HCR ≈ +17%    (consecutive requirement reduces further)

  THE SAME DATA GIVES 4 DIFFERENT ANSWERS (4× to 45× range)
  depending on which threshold you define.

WHAT A REVIEWER CAN CHALLENGE:
  "Why P90 and not P95? Why 3 consecutive days and not 5?
   Why per-DOY and not fixed? Why compound and not single?"
  → Each choice needs its own justification.
  → Each justification is debatable.

DEFENSIBILITY: MODERATE
  The counting itself is correct (no math errors).
  But the DEFINITION of what you're counting is a design choice
  that significantly affects the answer.
```

---

## 2. Why Pathway A Is Preferred When It Works

### 2A. No Threshold Subjectivity

```
Pathway A says: "The mean shifted +7.4%. Literature says heat events
amplify by ~2.5× per unit of mean shift. Therefore +18.5% more events."

This doesn't require defining:
  - What temperature is "hot enough" to count
  - Whether to use per-DOY or absolute thresholds
  - How many consecutive days matter
  - Which variables must co-occur

The amplification factor (2.5×) absorbs all of this — it was derived
from studies that already made those threshold choices and measured
the empirical amplification.
```

### 2B. Published, Peer-Reviewed Scaling Factors

```
The scaling factors come from specific papers:
  Heat: 2.0-3.0× (Diffenbaugh et al. 2017; Cowan et al. 2017)
  Flood: ~7%/°C (Clausius-Clapeyron, IPCC AR6 Chapter 11)

These were published in PNAS, Scientific Reports, and IPCC.
A reviewer can look them up and verify.

By contrast, Pathway B's thresholds are OUR choices.
"We defined a heat wave as 3+ consecutive days where both tasmax
and tasmin exceed per-DOY P90 with ±15-day smoothing."
  → This is defensible but not published.
  → Every term (3+, both, P90, ±15) is a parameter choice.
```

### 2C. Pathway B Validates A (Cross-Check)

```
The strongest position is: use A as primary, validate against B.

NB04 cross-validation:
  Pathway A (heat_wave): HCR = 0.074 × 2.5 = +0.185
  Pathway B (compound heat wave, 3+ days): implied scaling = 2.7
  
  Agreement: within 8%. Scaling 2.5 is validated.
  
This gives you BOTH:
  1. A simple, traceable primary answer (A)
  2. Empirical validation that it's in the right ballpark (B)

If someone challenges the 2.5× scaling, you can point to B:
  "Our direct counting gives implied scaling of 2.7 — consistent."
```

---

## 3. When Pathway A Fails — And Why B Becomes Mandatory

### 3A. Jensen's Inequality (Precipitation)

```
The fatal case:

  SCVR_pr = -0.001 (mean precipitation barely changed)
  Pathway A: HCR_flood = -0.001 × 1.75 = -0.002 (NEGATIVE)
  
  But Pathway B (count actual Rx5day events): HCR_flood = +0.04 (POSITIVE)
  
  Pathway A gives the WRONG SIGN.
  
Why: The mean doesn't capture what's happening in the tail.
  Mean precipitation is flat, but extreme events intensify.
  Scaling the mean by any constant cannot fix a sign error.
  No scaling factor makes -0.001 × X = +0.04 (would need X < 0).

This is Jensen's inequality: for non-linear functions,
  f(E[X]) ≠ E[f(X)]
  
The threshold-crossing function is non-linear.
Applying it to the mean gives a different answer than
applying it to each day and averaging.
```

### 3B. The Report Card Tells You When A Fails

```
The SCVR Report Card's Tail Confidence flag:

  HIGH:      Mean and tail agree → A is safe
  MODERATE:  Some disagreement → A with caution, prefer B alongside
  LOW:       Weak linkage → B preferred
  DIVERGENT: Mean and tail point OPPOSITE DIRECTIONS → A gives wrong answer

For precipitation: Tail Confidence = DIVERGENT
  → Pathway B is MANDATORY (not a preference — a requirement)

For tasmax: Tail Confidence = HIGH
  → Pathway A is safe (validated by B cross-check)

The routing is DATA-DRIVEN, not arbitrary.
```

---

## 4. The Threshold Problem — Why B Is Hard to Defend

### 4A. The 2.5× vs 26× Example

NB04 revealed this dramatically:

```
SAME DATA, TWO THRESHOLD DEFINITIONS:

  Definition 1 (compound heat wave):
    tasmax > per-DOY P90 AND tasmin > per-DOY P90
    3+ consecutive days
    Baseline: ~1.5 compound heat wave days/year
    Future:   ~14 days/year
    Implied scaling from SCVR: ~2.5×

  Definition 2 (simple P90 exceedance):
    tasmax > per-DOY P90 (any single day)
    Baseline: ~36.5 days/year (10% by construction)
    Future:   ~101 days/year
    Implied scaling from SCVR: ~26×

  BOTH ARE CORRECT for their threshold definition.
  But 2.5× vs 26× is a 10× difference in the HCR number.
  
  Which one feeds the BI model? That's a design choice:
    - Compound (2.5×) = meaningful for inverter shutdown BI
    - Simple P90 (26×) = meaningful for derating BI
    
  The threshold definition determines what financial mechanism
  you're modeling. This is a CONCEPTUAL choice, not a math error.
```

### 4B. Every Threshold Parameter Is Debatable

```
"Why per-DOY P90 and not absolute 40°C?"
  Per-DOY adapts to seasonality (a hot March day ≠ a hot July day)
  Absolute is simpler but ignores acclimatisation
  → Both are defensible. Choice changes the count.

"Why 3 consecutive days and not 5?"
  3 days is the Copernicus EDO standard for European heat waves
  5 days is more conservative (fewer events, larger per-event impact)
  → Both are defensible. 3-day count is ~3× higher than 5-day.

"Why ±15-day smoothing window for per-DOY thresholds?"
  ±15 prevents sharp day-to-day jumps in the threshold
  ±7 would be more localized, ±30 would blur seasonality
  → All are defensible. Changes threshold by ~0.5°C.

"Why compound (both tasmax AND tasmin)?"
  Compound captures nighttime heat stress (no recovery)
  Single-variable captures daytime shutdown only
  → Both are defensible. Compound count is ~10× lower.

EACH of these is reasonable. But the COMBINATION of all four choices
produces a specific number that is very sensitive to the combination.
Pathway A sidesteps ALL of them.
```

---

## 5. The Same Logic Applies to EFR

### Mode A (Peck's — preferred)

```
SCVR_tas → ΔT → AF = 2^(ΔT/10) → EFR_peck

No thresholds needed:
  - Temperature goes into the Arrhenius equation directly
  - The equation is published physics (IEC 61215)
  - The "10°C doubles" linearisation is standard in reliability engineering
  - Each step is traceable: SCVR → °C → acceleration factor → EFR

DEFENSIBILITY: HIGH
```

### Mode B (Coffin-Manson — mandatory fallback)

```
Count freeze-thaw cycles: days where tasmin < 0°C AND tasmax > 0°C

Threshold choices:
  - Why 0°C? (physics: water freezes at 0°C — this one IS defensible)
  - But: does it count days where tasmin = -0.1°C and tasmax = +0.1°C?
    That's a 0.2°C swing — not a real freeze-thaw cycle.
  - Should there be a minimum ΔT per cycle? (e.g., ΔT > 5°C)
  - What about multi-day freeze events (stays below 0 for 3 days)?

Mode B is mandatory here because Mode A gives wrong direction:
  Mode A: SCVR says tasmin warming → ΔT change → EFR = +0.03 (more damage)
  Mode B: Actual cycle count → 25% fewer 0°C crossings → EFR = -0.25 (benefit)
  
  Mode A gets the SIGN wrong (same problem as precipitation).
  So we accept Mode B's threshold dependency as the lesser evil.

DEFENSIBILITY: MODERATE (but necessary)
```

---

## 6. The Decision Hierarchy

```
FOR EACH HAZARD / DEGRADATION MODEL:

  Step 1: Check Tail Confidence for the input variable
  
  Step 2: If HIGH → Use Pathway/Mode A (preferred)
           Reason: defensible, no thresholds, literature-backed
           Cross-validate against B for extra confidence
           
  Step 3: If DIVERGENT or A gives wrong sign → Use Pathway/Mode B (mandatory)
           Reason: A is mathematically wrong, B is the only option
           Accept B's threshold dependency as necessary
           Document threshold choices and their justification
           
  Step 4: If MODERATE → Use A as primary, report B alongside
           Flag the gap between A and B
           Let the reviewer decide which to trust
           

THIS IS NOT "A is always better" — it's:
  "A is preferred when it works, because it's more defensible.
   B is mandatory when A fails, even though B has threshold subjectivity.
   The Report Card tells you which case you're in."
```

### How NB04 Implements This

```
HAZARD              Pathway  Reason
──────────────────  ───────  ──────────────────────────────────
heat_wave           A (2.5×) Tail Confidence HIGH, scaling validated
extreme_precip      B        Tail Confidence DIVERGENT, A gives wrong sign
flood_rx5day        B        Same — mandatory for all pr-based hazards
wind_extreme        A (1.0×) Small signal, linear approximation OK
icing_shutdown      B        Compound threshold, B more physical

Peck's (EFR)        Mode A   Tail Confidence HIGH for tas, no thresholds needed
Coffin-Manson (EFR) Mode B   Mode A gives wrong direction at Hayhurst
Palmgren-Miner      Mode A   SCVR_sfcWind ≈ 0, both modes give ≈ 0
```

---

## 7. What to Say When Asked

### "Why not just use Pathway B everywhere?"

> "Pathway B requires defining what counts as a hazard event — which
> thresholds, which variable combinations, which durations. Each choice
> is debatable and changes the answer by up to 10×. We showed that two
> reasonable heat wave definitions give 2.5× vs 26× scaling — same data,
> different answer. Pathway A avoids this subjectivity by working with
> the mean shift and published amplification factors. We use B only where
> A is mathematically wrong, which the SCVR Report Card identifies
> automatically."

### "Why not just use Pathway A everywhere?"

> "For precipitation, Pathway A gives the wrong sign. Mean precipitation
> barely changes (SCVR ≈ 0) but extreme rainfall events increase
> significantly. No scaling factor can fix a sign error. This is Jensen's
> inequality — the mean-based approximation fails for non-linear threshold
> functions. The Report Card flags this as DIVERGENT confidence, and
> Pathway B becomes mandatory."

### "How do you know when A fails?"

> "The SCVR Report Card computes 6 companion metrics including P95 SCVR
> and Mean-Tail Ratio. When the mean and tail point in opposite directions
> (mean negative, tail positive), the Tail Confidence flag is set to
> DIVERGENT. This is a data-driven signal, not a judgment call."

---

## Cross-References

| Topic | Doc |
|-------|-----|
| Pathway A vs B mechanics | [hcr_pathway_a_vs_b.md](hcr_pathway_a_vs_b.md) |
| Jensen's inequality proof | [jensen_inequality_hcr_scvr.md](jensen_inequality_hcr_scvr.md) |
| EFR Mode A vs B | [efr_two_modes.md](../efr_degradation/efr_two_modes.md) |
| Report Card routing | [04_scvr_methodology.md §4](../../learning/B_scvr_methodology/04_scvr_methodology.md) |
| Orchestrator routing table | [06b_climate_risk_orchestrator.md §5](../../learning/C_financial_translation/06b_climate_risk_orchestrator.md) |
| NB04 implementation | [04_hcr_hazard_change_ratio.ipynb](../../notebook_analysis/04_hcr_hazard_change_ratio.ipynb) |

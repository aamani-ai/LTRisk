---
title: "Discussion — Published Scaling vs Direct Computation: Why Two Pathways Exist"
type: discussion
domain: climate-risk / methodology / defensibility
created: 2026-04-09
updated: 2026-04-09
status: revised — reframed from "A preferred / B fallback" to "published scaling where available, direct computation where necessary"
context: >
  A reviewer asked why the framework uses two computation pathways. This doc
  explains that both pathways are grounded in the same empirical method
  (counting threshold exceedances from climate model output). Pathway A
  reuses published scaling factors from peer-reviewed literature. Pathway B
  computes directly from our own daily data. The choice depends on whether
  a reliable published scaling factor exists for the hazard — not on a
  preference hierarchy.
relates-to:
  - docs/learning/C_financial_translation/07_hcr_hazard_change.md
  - docs/discussion/hcr_financial/hcr_pathway_a_vs_b.md
  - docs/discussion/hcr_financial/jensen_inequality_hcr_scvr.md
  - docs/discussion/efr_degradation/efr_two_modes.md
  - docs/learning/C_financial_translation/06b_climate_risk_orchestrator.md
---

# Published Scaling vs Direct Computation

> **The question:** "Why does the framework use two computation pathways
> instead of standardising on one?"

> **The answer:** Both pathways compute the same thing — how many more
> hazard events does climate change produce. Pathway A reuses a published,
> peer-reviewed scaling factor (someone else's empirical result). Pathway B
> computes directly from our own daily data. We use A where a reliable
> published factor exists because it's traceable and defensible. We use B
> where no published factor exists because we have no choice. Both are
> grounded in the same empirical method.

---

## 1. The Key Insight: A IS Borrowed B

Pathway A looks different from B, but scientifically they're the same thing:

```
WHAT DIFFENBAUGH ET AL. (2017, PNAS) DID:
  1. Took CMIP5 daily temperature data
  2. Defined heat wave thresholds
  3. Counted heat wave events in baseline and future
  4. Compared to mean temperature shift
  5. Found: ~2.5× amplification per unit of mean shift
  → They did PATHWAY B and published the result.

WHAT WE DO WITH PATHWAY A:
  1. Take their published result (2.5×)
  2. Multiply by our SCVR (our mean shift)
  3. Get HCR
  → We REUSE their Pathway B result as a scaling factor.

WHAT WE DO WITH PATHWAY B:
  1. Take our own CMIP6 daily data (28 models)
  2. Define thresholds (per-DOY P90, compound, 3+ consecutive days)
  3. Count events in baseline and future
  4. Compare
  → We do the SAME empirical work ourselves.

WHEN WE CROSS-VALIDATE A vs B:
  We're comparing: literature's empirical result vs our empirical result
  Hayhurst: A gives 2.5×, B gives implied 2.7×
  → They agree. This validates both the published scaling AND our counting.
```

**Pathway A is not a different method. It's a shortcut that reuses someone
else's empirical work.** This is standard scientific practice — you don't
re-derive every result yourself if a peer-reviewed study already established it.

---

## 2. When Published Scaling Is Available — Use It

Currently, only **heat wave** has a peer-reviewed, site-validated scaling factor:

```
HEAT WAVE:
  Published scaling: 2.5× (Diffenbaugh et al. 2017, PNAS; Cowan et al. 2017, Sci. Reports)
  Our cross-validation: implied scaling 2.7× (from NB04a Pathway B)
  Agreement: within 8%
  
  → Use published scaling (Pathway A). It's:
    - Peer-reviewed (PNAS)
    - Validated by our own data (2.7× matches 2.5×)
    - Traceable (SCVR × 2.5 = HCR)
    - No threshold subjectivity on our part
```

**Why this is more defensible than Pathway B alone:**

Pathway A: "We use the 2.5× amplification factor from Diffenbaugh et al.
(2017, PNAS), validated against our direct computation which gives 2.7×."

Pathway B alone: "We defined a heat wave as 3+ consecutive days where
both tasmax and tasmin exceed per-DOY P90 with ±15-day smoothing, and
counted events directly."

The first statement cites a published source. The second requires
justifying every parameter choice (why P90? why 3 days? why ±15?).

---

## 3. When No Published Scaling Exists — Compute Directly

For most of our hazards, no reliable published scaling factor exists:

```
EXTREME PRECIPITATION:
  Published: Clausius-Clapeyron ~7%/°C for moisture, but this is NOT
  a site-level flood event frequency scaling factor.
  Problem: mean precipitation SCVR ≈ 0 at Hayhurst, but extreme events
  increase. No constant × 0 = positive number (Jensen's inequality).
  → Must compute directly (Pathway B). No published shortcut available.

FLOODING (Rx5day):
  Published: No site-specific Rx5day scaling factor.
  Same Jensen's issue as extreme precipitation.
  → Must compute directly (Pathway B).

ICING SHUTDOWN:
  Published: No published scaling for compound icing events
  (requires tasmin < 0 AND hurs > 90% simultaneously).
  → Must compute directly (Pathway B).

WIND EXTREME:
  Published: No reliable scaling (daily mean ≠ gusts).
  SCVR_sfcWind ≈ 0 anyway — the choice doesn't matter.
  → Use Pathway A with 1.0× (linear, essentially zero signal).
```

**This is not "falling back" to B. It's the only option.** You can't use
a published scaling factor that doesn't exist. Pathway B is the necessary
computation when the scientific literature hasn't done the work for you.

---

## 4. The Threshold Subjectivity Problem (When We Must Use B)

When we compute directly (Pathway B), every threshold definition is a
design choice that affects the answer:

```
THE 2.5× vs 26× EXAMPLE (from NB04a):

  Same data, two threshold definitions:

  Definition 1 (compound heat wave):
    tasmax > per-DOY P90 AND tasmin > per-DOY P90, 3+ consecutive days
    Implied scaling: ~2.5×

  Definition 2 (simple P90 exceedance):
    tasmax > per-DOY P90 (any single day)
    Implied scaling: ~26×

  10× difference from the SAME DATA.
  Both are correct for their definition.

  This is why published scaling is preferred where it exists —
  it avoids this subjectivity entirely. Diffenbaugh et al. already
  made these choices, published them, and had them peer-reviewed.
```

When we must use B (precipitation, icing), we accept this subjectivity
as the cost of computing something no one has published yet. We document
our threshold choices and their justification.

---

## 5. The Same Pattern for EFR

The EFR channel has the identical structure:

```
PECK'S THERMAL AGING (Mode A — published physics):
  Published: Arrhenius equation with Ea = 0.7 eV (IEC 61215)
  "10°C doubles degradation" linearisation (standard reliability engineering)
  → Use published physics (Mode A). Traceable, peer-reviewed.

COFFIN-MANSON CYCLING (Mode B — direct computation):
  Published: The formula N_f = C × (ΔT)^(-β) is published.
  But: applying it via SCVR mean approximation gives WRONG DIRECTION.
  Mode A says +3% (more damage). Actual daily counts say -25% (fewer cycles).
  → Must compute directly from daily data (Mode B).
  Threshold choice: 0°C for freeze-thaw (physics-based, defensible).

PALMGREN-MINER (Mode A — published physics):
  Published: S-N curve framework (IEC 61400)
  SCVR_sfcWind ≈ 0 → effectively zero regardless of mode.
  → Use published framework (Mode A).
```

---

## 6. The Decision Logic

```
FOR EACH HAZARD OR DEGRADATION MODEL:

  Does a reliable, peer-reviewed scaling factor or physics model exist?
  ├── YES: Use it (Pathway A / Mode A)
  │        - Cite the source
  │        - Cross-validate against our direct computation (B)
  │        - If A and B agree: confidence is high
  │        - If A and B disagree: investigate, report both
  │
  └── NO: Compute directly from daily data (Pathway B / Mode B)
           - Document threshold definitions and their justification
           - Acknowledge the subjectivity
           - This is necessary, not a compromise

  Does the SCVR Report Card flag the variable as DIVERGENT?
  ├── YES: Published scaling (A) gives wrong sign
  │        → Direct computation (B) is mandatory
  │        → Even if a scaling factor existed, it wouldn't work
  │
  └── NO: Published scaling (A) is mathematically valid
          → Use it if available, compute directly if not

CURRENT STATE (Hayhurst Solar):
  Hazard          Published scaling?   Tail Conf.   Computation
  ──────────────  ──────────────────   ──────────   ──────────────
  heat_wave       YES (2.5×, PNAS)     HIGH         Published scaling
  extreme_precip  NO                   DIVERGENT    Direct counting
  flood_rx5day    NO                   DIVERGENT    Direct counting
  wind_extreme    NO (1.0× assumed)    MOD          Published (trivial)
  icing_shutdown  NO                   MOD          Direct counting
  Peck's          YES (Arrhenius,IEC)  HIGH         Published physics
  Coffin-Manson   NO (A gives wrong)   HIGH(temp)   Direct counting
  Palmgren-Miner  YES (S-N, IEC)       MOD          Published physics
```

---

## 7. What to Say When Asked

### "Why two pathways instead of one?"

> "Both pathways compute the same thing — hazard frequency change from
> climate data. Pathway A reuses published, peer-reviewed scaling factors
> from studies that already did the empirical work. Pathway B computes
> directly from our own daily CMIP6 data. We use published scaling where
> it exists (heat wave: 2.5× from Diffenbaugh et al., PNAS) and compute
> directly where it doesn't (precipitation, icing). Our cross-validation
> shows the published scaling agrees with our direct computation within 8%."

### "Why not just use Pathway B everywhere?"

> "We could — and we do compute B for all hazards as a cross-check. But
> citing a peer-reviewed scaling factor is more defensible than presenting
> our own threshold definitions. When we say 'HCR = SCVR × 2.5', a reviewer
> can look up the 2.5 in PNAS. When we say 'we defined a heat wave as 3+
> consecutive days with both temperatures above per-DOY P90 with ±15-day
> smoothing', every term is a parameter choice that invites challenge.
> For precipitation, no published scaling exists, so direct computation
> is the only option."

### "Why not just use Pathway A everywhere?"

> "For precipitation, Pathway A gives the wrong sign. Mean precipitation
> barely changes (SCVR ≈ 0) but extreme rainfall events increase. No
> scaling factor can fix a sign error — this is Jensen's inequality.
> And for icing and Coffin-Manson, no published scaling factor exists
> that captures the compound threshold behaviour correctly."

### "How do you know when published scaling is reliable?"

> "The SCVR Report Card computes Tail Confidence — when the mean and tail
> agree (HIGH), the mean-based scaling is reliable. When they disagree
> (DIVERGENT), the scaling would give wrong answers regardless of what
> factor you multiply by. This is a data-driven signal, not a judgment."

---

## Cross-References

| Topic | Doc |
|-------|-----|
| Pathway A vs B mechanics | [hcr_pathway_a_vs_b.md](hcr_pathway_a_vs_b.md) |
| Jensen's inequality proof | [jensen_inequality_hcr_scvr.md](jensen_inequality_hcr_scvr.md) |
| EFR Mode A vs B | [efr_two_modes.md](../efr_degradation/efr_two_modes.md) |
| Report Card routing | [04_scvr_methodology.md §4](../../learning/B_scvr_methodology/04_scvr_methodology.md) |
| Orchestrator routing table | [06b_climate_risk_orchestrator.md §5](../../learning/C_financial_translation/06b_climate_risk_orchestrator.md) |
| NB04a implementation | [04a_hcr_hazard_change_ratio.ipynb](../../notebook_analysis/04a_hcr_hazard_change_ratio.ipynb) |

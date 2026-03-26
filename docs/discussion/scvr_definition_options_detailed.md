# SCVR Definition Options — Detailed Framework

---

## 0. Purpose

This document formalizes **all viable ways to define SCVR (Shift in Climate Variable Risk)** and evaluates them from:

- Mathematical correctness
- Interpretability
- Compatibility with physical models (HCR / EFR)
- Usability in financial translation (CFADS / NAV)

---

## 1. First Principles

We compare two distributions:

- Baseline: f_B(x)
- Future: f_F(x)

Goal:

> Quantify how distribution change translates into risk

---

## 2. PDF-Based Methods

### 2.1 Full Area Difference

SCVR_pdf = ∫ |f_F(x) - f_B(x)| dx

Meaning:
- Total shape difference

Problem:
- mixes mean, variance, tails
- no direction
- not interpretable

---

### 2.2 Positive Area Only

SCVR_pdf+ = ∫ max(f_F - f_B, 0) dx

Meaning:
- probability mass shifted to new regions

Key issue:
- does not tell *where* change happened
- cannot derive threshold probabilities

---

## 3. Exceedance-Based Methods

Let S(x) = P(X > x)

---

### 3.1 Mean-Based

E[X] = ∫ S(x) dx

SCVR_mean = (E[X_F] - E[X_B]) / E[X_B]

Use:
- cumulative processes (temperature → degradation)

---

### 3.2 Threshold-Based

SCVR_K = P_F(X > K) - P_B(X > K)

Use:
- hazards (precip, floods, heatwaves)

---

### 3.3 Tail-Integrated

∫_K^∞ S(x) dx

Use:
- severity + frequency

---

### 3.4 Weighted General Form

SCVR(w) = ∫ w(x)[S_F(x) - S_B(x)] dx

Key insight:
- all SCVR variants are special cases of this

---

## 4. SCVR Report (Current System)

Not a single metric.

Components:
- Mean shift
- Tail metrics
- Model spread
- Confidence
- Routing

Pipeline:

Climate → SCVR Report → Routing → HCR/EFR → CFADS → NAV

---

## 5. Why PDF Metrics Fail in Pipeline

EFR requires:
- physical scale (temperature)

HCR requires:
- threshold exceedance

PDF metric provides:
- geometric difference only

Thus:

PDF metric → ❌ cannot map to HCR/EFR directly

---

## 6. Examples

### tasmax

- Mean ↑ → degradation ↑
- SCVR_mean works

PDF metric:
- cannot map to temperature

---

### precipitation

- Mean ≈ 0
- Tail ↑

SCVR report:
- uses threshold

PDF metric:
- mixes all effects → misses hazard signal

---

## 7. Final Philosophy

There is no universal SCVR.

Correct approach:

- Mean → cumulative mechanisms
- Threshold → event mechanisms
- Report → decision layer

---

## 8. Final Takeaway

SCVR is not a number.

SCVR is a **translation layer from climate to risk**.

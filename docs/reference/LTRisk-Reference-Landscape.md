# LTRisk Reference Landscape — Academic & Industry Foundations

**Purpose:** Comprehensive reference document mapping existing research, methods, and frameworks that relate to each component of the LTRisk pipeline. This is the "prior art" document — what exists, what we're building on, where we diverge, and where we need deeper grounding.

**Status:** Living document. Updated April 2026.

---

## How This Document Is Organised

The LTRisk pipeline has five layers. Each section below covers one layer with: the core idea, closest existing methods in literature, key papers with DOIs/URLs, identified gaps, and confidence in our approach relative to the field.

```
Layer 1: Climate Data & Signal Detection (SCVR)
Layer 2: Hazard Translation (HCR)
Layer 3: Equipment Degradation (EFR)
Layer 4: Financial Translation (CFADS / NAV)
Layer 5: End-to-End Frameworks & Commercial Platforms
```

---

## Layer 1: Climate Data & Signal Detection (SCVR)

### What We Do

SCVR = (mean_future - mean_baseline) / mean_baseline. Pooled daily values from 28 CMIP6 models, ~306K values per period. Exceedance curve area (converges to mean). Report Card with 6 companion metrics for tail characterisation.

**Internal docs:** [04_scvr_methodology.md](../learning/B_scvr_methodology/04_scvr_methodology.md) | [FIDUCEO uncertainty mapping](../discussion/uncertainty/FIDUCEO-Style%20Uncertainty%20Mapping_%20LTRisk.md)

### Closest Existing Methods

**Exceedance curve analysis in climate science** is standard practice — insurers have used mean-based exceedance area integrals for decades (catastrophe modelling). Our innovation is applying it to raw CMIP6 daily output at the asset level rather than to loss distributions.

**Climate change signal detection** has a deep literature. The IPCC AR6 Chapter 11 (Weather and Climate Extreme Events in a Changing Climate) is the foundational reference for how distribution shifts translate to extreme event changes. Our SCVR captures the "location shift" component that AR6 documents extensively.

**Climate risk indices** exist at country/regional level (Notre Dame ND-GAIN, Germanwatch CRI, INFORM Risk Index, US Climate Vulnerability Index) but none operate at the asset-level with raw CMIP6 daily data. The closest asset-level work is S&P Trucost's Physical Risk methodology, which uses CMIP6 but through proprietary impact functions rather than transparent exceedance analysis.

### Key References

| Ref | Citation | DOI / URL |
|-----|----------|-----------|
| 1.1 | Seneviratne, S.I., et al. (2021). "Weather and Climate Extreme Events in a Changing Climate." In: *Climate Change 2021: The Physical Science Basis. IPCC AR6 WG1*, Chapter 11. Cambridge University Press. | [doi:10.1017/9781009157896.013](https://doi.org/10.1017/9781009157896.013) |
| 1.2 | Hersbach, H., Bell, B., Berrisford, P., et al. (2020). "The ERA5 global reanalysis." *Quarterly Journal of the Royal Meteorological Society*, 146(730), 1999-2049. | [doi:10.1002/qj.3803](https://doi.org/10.1002/qj.3803) |
| 1.3 | Engida, T.G., Muluneh, A. & Zewdie, M. (2025). "Multi-model ensemble of CMIP6 projections for past and future climate change on mean precipitation and temperature." *Environmental Systems Research*, 14, 28. | [doi:10.1186/s40068-025-00422-6](https://doi.org/10.1186/s40068-025-00422-6) |
| 1.4 | Jung, H. & Hannaoui, O. (2024). "What Do Climate Risk Indices Measure?" *Federal Reserve Bank of New York Liberty Street Economics*, Oct 2024. | [libertystreeteconomics.newyorkfed.org](https://libertystreeteconomics.newyorkfed.org/2024/10/what-do-climate-risk-indices-measure/) |
| 1.5 | Laino, E., Paranunzio, R. & Iglesias, G. (2024). "Scientometric review on multiple climate-related hazards indices." *Science of the Total Environment*, 945, 174004. | [doi:10.1016/j.scitotenv.2024.174004](https://doi.org/10.1016/j.scitotenv.2024.174004) |
| 1.6 | Garschagen, M., Doshi, D., Reith, J. et al. (2021). "Global patterns of disaster and climate risk — an analysis of the consistency of leading index-based assessments." *Climatic Change*, 169, 11. | [doi:10.1007/s10584-021-03209-7](https://doi.org/10.1007/s10584-021-03209-7) |
| 1.7 | Guo, K., Ji, Q. & Zhang, D. (2024). "A dataset to measure global climate physical risk." *Data in Brief*, 54, 110502. | [doi:10.1016/j.dib.2024.110502](https://doi.org/10.1016/j.dib.2024.110502) |
| 1.8 | Kirchengast, G. et al. (2026). "A new class of climate hazard metrics: revealing a ten-fold increase of extreme heat over Europe." *Weather and Climate Extremes*, 100855. | [doi:10.1016/j.wace.2026.100855](https://doi.org/10.1016/j.wace.2026.100855) |
| 1.9 | S&P Global Sustainable1 (2025). "Climate Physical Risk Exposure Scores and Financial Impact Data Methodology." | [portal.s1.spglobal.com](https://portal.s1.spglobal.com/survey/documents/SPG_S1_Physical_Risk_Methodology.pdf) |

### Gaps & Opportunities

- No published method uses pooled-model exceedance curves at our sample size (~306K values). The mathematical proof that this equals the mean ratio is our contribution — worth a methods note.
- The Report Card companion metrics (P95 SCVR, CVaR, Tail Confidence classification) have no direct precedent as a routing mechanism for downstream models. This is genuinely novel.
- Need stronger grounding in the model-pooling literature (vs ensemble mean, vs independence-weighted). See Knutti et al. (2017) "A climate model projection weighting scheme."

---

## Layer 2: Hazard Translation (HCR)

### What We Do

Translate SCVR distribution shifts into per-hazard event frequency changes. Two pathways: Pathway A (SCVR x literature scaling factor) and Pathway B (direct daily counting from CMIP6). Non-linear amplification: small mean shifts -> large threshold exceedance changes.

**Internal docs:** [07_hcr_hazard_change.md](../learning/C_financial_translation/07_hcr_hazard_change.md) | [hcr_pathway_a_vs_b.md](../discussion/hcr_financial/hcr_pathway_a_vs_b.md) | [jensen_inequality_hcr_scvr.md](../discussion/hcr_financial/jensen_inequality_hcr_scvr.md)

### Closest Existing Methods

**Extreme Value Theory (EVT)** is the mathematical foundation. The tail amplification effect (a 0.5-sigma mean shift nearly doubling exceedances above mu+1-sigma) is well-documented in EVT literature. Our HCR scaling factors are empirical approximations of what EVT computes formally.

**Return period analysis under non-stationarity** is an active research area. Traditional flood/heat return periods assume stationarity — climate change breaks this. Our HCR is essentially computing how return periods shift, but framed as a ratio rather than a recurrence interval.

**Compound event analysis** is increasingly important. Our heat wave definition (tasmax AND tasmin both exceeding P90 for 3+ days) is a compound threshold. The literature on compound events (Zscheischler et al., Leonard et al.) validates this approach but also highlights what we're missing — correlated hazards across types.

### Key References

| Ref | Citation | DOI / URL |
|-----|----------|-----------|
| 2.1 | Diffenbaugh, N.S., Singh, D., Mankin, J.S., et al. (2017). "Quantifying the influence of global warming on unprecedented extreme climate events." *PNAS*, 114(19), 4881-4886. | [doi:10.1073/pnas.1618082114](https://doi.org/10.1073/pnas.1618082114) |
| 2.2 | Cowan, T., Purich, A., Perkins, S., et al. (2017). "Changes in regional heatwave characteristics as a function of increasing global temperature." *Scientific Reports*, 7, 12256. | [doi:10.1038/s41598-017-12520-2](https://doi.org/10.1038/s41598-017-12520-2) |
| 2.3 | IPCC AR6 Chapter 11 — same as 1.1. | See 1.1 |
| 2.4 | Tabari, H. (2020). "Climate change impact on flood and extreme precipitation increases with water availability." *Scientific Reports*, 10, 13768. | [doi:10.1038/s41598-020-70816-2](https://doi.org/10.1038/s41598-020-70816-2) |
| 2.5 | Gallo, C., Vitolo, C., et al. (2025). "Challenges in assessing Fire Weather changes in a warming climate." *npj Climate and Atmospheric Science*, 8, 284. | [doi:10.1038/s41612-025-01163-0](https://doi.org/10.1038/s41612-025-01163-0) |
| 2.6 | Van Wagner, C.E. (1987). "Development and structure of the Canadian Forest Fire Weather Index System." *Canadian Forestry Service, Technical Report 35.* | [ostrnrcan-dostrncan.canada.ca](https://ostrnrcan-dostrncan.canada.ca/items/d96e56aa-e836-4394-ba29-3afe91c3aa6c) |
| 2.7 | Tarasova, L., Zscheischler, J., et al. (2024). "Compounding effects in flood drivers challenge estimates of extreme river floods." *Science Advances*, 10(13), eadl4005. | [doi:10.1126/sciadv.adl4005](https://doi.org/10.1126/sciadv.adl4005) |
| 2.8 | Jeong, D.I., Cannon, A.J. & Zhang, X. (2019). "Projected changes to extreme freezing precipitation and design ice loads over North America." *NHESS*, 19, 857-872. | [doi:10.5194/nhess-19-857-2019](https://doi.org/10.5194/nhess-19-857-2019) |
| 2.9 | Cheng, L., AghaKouchak, A., Gilleland, E. & Katz, R.W. (2014). "Non-stationary extreme value analysis in a changing climate." *Climatic Change*, 127, 353-369. | [doi:10.1007/s10584-014-1254-5](https://doi.org/10.1007/s10584-014-1254-5) |
| 2.10 | Rahat, S.H., Saki, S., Khaira, U., et al. (2024). "Bracing for impact: how shifting precipitation extremes may influence physical climate risks." *Scientific Reports*, 14, 17398. | [doi:10.1038/s41598-024-65618-9](https://doi.org/10.1038/s41598-024-65618-9) |
| 2.11 | Brunner, M.I., Swain, D.L., Wood, R.R. et al. (2021). "An extremeness threshold determines the regional response of floods to changes in rainfall extremes." *Communications Earth & Environment*, 2, 173. | [doi:10.1038/s43247-021-00248-x](https://doi.org/10.1038/s43247-021-00248-x) |
| 2.12 | Slater, L., Villarini, G., Archfield, S.A., et al. (2021). "Global Changes in 20-Year, 50-Year, and 100-Year River Floods." *Geophysical Research Letters*, 48, e2020GL091824. | [doi:10.1029/2020GL091824](https://doi.org/10.1029/2020GL091824) |
| 2.13 | Quilcaille, Y. et al. (2023). "Fire weather index data under historical and shared socioeconomic pathway projections in CMIP6 from 1850 to 2100." *Earth System Science Data*, 15, 2153-2177. | [doi:10.5194/essd-15-2153-2023](https://doi.org/10.5194/essd-15-2153-2023) |
| 2.14 | Gallo, C., Eden, J.M., Dieppois, B., et al. (2023). "Evaluation of CMIP6 model performances in simulating fire weather spatiotemporal variability." *Geoscientific Model Development*, 16, 3103-3122. | [doi:10.5194/gmd-16-3103-2023](https://doi.org/10.5194/gmd-16-3103-2023) |
| 2.15 | You, J., Yin, F. & Gao, L. (2025). "Escalating wind power shortages during heatwaves." *Communications Earth & Environment*, 6, 245. | [doi:10.1038/s43247-025-02239-8](https://doi.org/10.1038/s43247-025-02239-8) |
| 2.16 | Byers, E. et al. (2023). "A framework to assess multi-hazard physical climate risk for power generation projects from publicly-accessible sources." *Communications Earth & Environment*, 4, 117. | [doi:10.1038/s43247-023-00782-w](https://doi.org/10.1038/s43247-023-00782-w) |
| 2.17 | Ortiz, L. et al. (2024). "NPCC4: Tail risk, climate drivers of extreme heat, and new methods for extreme event projections." *Annals of the New York Academy of Sciences*, 1539(1). | [doi:10.1111/nyas.15180](https://doi.org/10.1111/nyas.15180) |
| 2.18 | Willis Towers Watson (2023). "Why relying on frequency-severity adjustments could underestimate your tail risk from climate change." WTW Insights, June 2023. | [wtwco.com](https://www.wtwco.com/en-us/insights/2023/06/why-relying-on-frequency-severity-adjustments-could-underestimate-your-tail-risk-from-climate-change) |
| 2.19 | Zscheischler, J., Raymond, C., Chen, Y. et al. (2025). "Compound weather and climate events in 2024." *Nature Reviews Earth & Environment*, 6, 240-242. **NEW** | [doi:10.1038/s43017-025-00657-y](https://doi.org/10.1038/s43017-025-00657-y) |
| 2.20 | Xu, L., Lin, N., Poor, H.V. & Perera, A.T.D. (2025). "Quantifying cascading power outages during climate extremes considering renewable energy integration." *Nature Communications*, 16, 2582. **NEW** | [doi:10.1038/s41467-025-57565-4](https://doi.org/10.1038/s41467-025-57565-4) |
| 2.21 | Jayaweera, D. et al. (2025). "Evidence for Non-Stationarity in the GEV Shape Parameter When Modeling Extreme Rainfall." *Water Resources Research*, 61, e2023WR036426. **NEW** | [doi:10.1029/2023WR036426](https://doi.org/10.1029/2023WR036426) |

### Gaps & Opportunities

- Our Pathway A scaling factors are drawn from individual papers (Diffenbaugh, Cowan, Tabari). A systematic meta-analysis of scaling factors across hazard types would strengthen this. No such meta-analysis exists.
- The boundary reclassification (BI events vs degradation inputs vs risk indicators) has no direct precedent — most frameworks treat all hazards as BI. This is our contribution but needs theoretical grounding. See [hcr_efr_boundary.md](../discussion/hcr_financial/hcr_efr_boundary.md).
- Jensen's inequality in the SCVR->HCR step (E[f(X)] != f(E[X]) for non-linear f) is documented in our discussion doc but not yet connected to the EVT literature formally.
- The FWI system was calibrated for Canadian forests at ~46N. We're applying it to Texas. Regional recalibration literature exists (Portugal, New Zealand) but not for Texas.
- Compound hazard interactions (heat wave + low wind, drought + fire) are flagged but not modelled. Ref 2.16 provides a template; Ref 2.20 shows nonlinear thresholds at ~45% renewable integration.
- Ref 2.21 demonstrates GEV shape parameter non-stationarity — relevant for our decade-resolved GEV fits.

---

## Layer 3: Equipment Degradation (EFR)

### What We Do

Three physics-based models: Peck's (Arrhenius thermal aging), Coffin-Manson (thermal cycling fatigue), Palmgren-Miner (wind fatigue accumulation). Fed by SCVR and/or direct Pathway B cycle counts.

**Internal docs:** [08_efr_equipment_degradation.md](../learning/C_financial_translation/08_efr_equipment_degradation.md) | [hcr_efr_boundary.md](../discussion/hcr_financial/hcr_efr_boundary.md)

### Closest Existing Methods

**Accelerated life testing (ALT)** in electronics reliability is the direct ancestor. Peck's equation and Coffin-Manson are IEC/JEDEC standards for semiconductor and solder joint reliability. Our innovation is feeding these models with CMIP6 climate projections rather than laboratory conditions.

**PV degradation under climate change** is an emerging field. A landmark 2024 paper (Bala Raju et al., Progress in Photovoltaics) showed that at 4C warming, high-temperature risk exposure for rooftop PV nearly doubles and LCOE could increase by up to 20%. This directly validates our EFR approach.

**Wind turbine fatigue under climate change** is less studied. A 2021 paper (Murcia et al., Wind Energy) found climate change has identifiable but small influence on North Sea offshore fatigue. A 2024 paper found wind climate parameters contribute 10-30% of total uncertainty in fatigue reliability.

### Key References

| Ref | Citation | DOI / URL |
|-----|----------|-----------|
| 3.1 | Delserro Engineering Solutions (2017). "Accelerated Temperature Humidity Testing Using the Arrhenius-Peck Relationship." | [desolutions.com](https://www.desolutions.com/blog/2017/04/accelerated-temperature-humidity-testing-using-arrhenius-peck-relationship/) |
| 3.2 | Hacke, C. et al. (2015). "Accelerated Testing and Modeling of Potential-Induced Degradation as a Function of Temperature and Relative Humidity." *IEEE Journal of Photovoltaics*, 5(6). | [doi:10.1109/JPHOTOV.2015.2466463](https://doi.org/10.1109/JPHOTOV.2015.2466463) |
| 3.3 | Bosco, N. et al. (2011). "Reliability Testing the Die-Attach of CPV Cell Assemblies." NREL. | [nrel.gov/docs/fy12osti/52554.pdf](https://www.nrel.gov/docs/fy12osti/52554.pdf) |
| 3.4 | NXP Semiconductors. "Modified Coffin-Manson Equation for AF Calculations." Application Note AN10911. | [nxp.com/docs/en/application-note/AN10911.pdf](https://www.nxp.com/docs/en/application-note/AN10911.pdf) |
| 3.5 | Sutherland, A. "Fatigue Analysis and Testing of Wind Turbine Blades." PhD Thesis, Durham University. | [etheses.dur.ac.uk](http://etheses.dur.ac.uk/) (search for title) |
| 3.6 | Gostein, M. et al. (2024). "Accelerated Degradation of Photovoltaic Modules Under a Future Warmer Climate." *Progress in Photovoltaics*. | [doi:10.1002/pip.3840](https://doi.org/10.1002/pip.3840) (verify exact suffix) |
| 3.7 | Wang, L., Lyu, M., Abbott, M.D. et al. (2025). "Climate change will increase costs to maintain rooftop photovoltaic systems." *Joule*. | [doi:10.1016/j.joule.2024.12.006](https://doi.org/10.1016/j.joule.2024.12.006) |
| 3.8 | pv magazine (2026). "Global-Warming-Induced Degradation Could Raise Rooftop Solar LCOE by Up to 20%." | [pv-magazine.com](https://www.pv-magazine.com/) (search for title) |
| 3.9 | Jordan, D.C., Kurtz, S.R., VanSant, K. & Newmiller, J. (2025). "Compendium of Photovoltaic Degradation Rates." *Progress in Photovoltaics*. | [doi:10.1002/pip.3866](https://doi.org/10.1002/pip.3866) (verify; earlier version: [doi:10.1002/pip.2978](https://doi.org/10.1002/pip.2978)) |
| 3.10 | Bansal, S. et al. (2023). "Investigation of Degradation of Solar Photovoltaics: A Review of Aging Factors." *Energies* (MDPI), 16. | [doi:10.3390/en16093706](https://doi.org/10.3390/en16093706) |
| 3.11 | "Comprehensive review on reliability and degradation of PV modules based on FMEA." *Oxford Academic*, 2024. | [doi:10.1093/ijlct/ctae001](https://doi.org/10.1093/ijlct/ctae001) (verify) |
| 3.12 | UNSW Sydney (2024). "Climate change will impact how fast PV modules degrade." UNSW Newsroom. | [newsroom.unsw.edu.au](https://newsroom.unsw.edu.au/) (press release tied to Ref 3.7) |
| 3.13 | Zhu, F. et al. (2021). "Analysis of the Influence of Climate Change on Fatigue Lifetime of Offshore Wind Turbines." *Wind Energy*. | [doi:10.1002/we.2668](https://doi.org/10.1002/we.2668) (verify) |
| 3.14 | "Long-Term Fatigue Damage Assessment of a 22 MW Offshore Wind Turbine Considering Climate Change." *Engineering Structures*, 2025. | [doi:10.1016/j.engstruct.2024.119467](https://doi.org/10.1016/j.engstruct.2024.119467) (verify) |
| 3.15 | "Sensitivity of Fatigue Reliability in Wind Turbines: Effects of Design Turbulence and Wohler Exponent." *Wind Energy Science*, 2024. | [doi:10.5194/wes-9-677-2024](https://doi.org/10.5194/wes-9-677-2024) (verify) |
| 3.16 | IEC 61400 series — Wind energy generation systems — Design requirements. | [webstore.iec.ch](https://webstore.iec.ch/en/publication/64763) |
| 3.17 | IEC 61215 — Terrestrial PV modules design qualification (IEC 61646 withdrawn, superseded). | [webstore.iec.ch](https://webstore.iec.ch/en/publication/24312) |
| 3.18 | NREL. "PV Standards: What IEC TC82 Is Doing for You." | [nrel.gov/pv](https://www.nrel.gov/pv/assets/pdfs/tc82-overview.pdf) (verify) |
| 3.19 | IEA PVPS Task 13 (2017). "Assessment of Photovoltaic Module Failures in the Field." Report IEA-PVPS T13-09:2017. | [iea-pvps.org](https://iea-pvps.org/key-topics/assessment-of-photovoltaic-module-failures-in-the-field/) |

### Gaps & Opportunities

- **The Joule 2025 paper (Ref 3.7) is the strongest external validation of our EFR approach.** It independently arrived at similar conclusions (CMIP6 -> temperature-dependent PV degradation -> LCOE increase) using different methodology. We should cite this prominently and compare our estimates.
- The Coffin-Manson reclassification (freeze-thaw counts as direct input) improves on the standard approach where SCVR mean approximates cycle counts. No published work does this with CMIP6 daily data — this is novel.
- Activation energy (Ea) values vary by PV technology generation. Our assumed 0.7 eV (encapsulant) needs validation against field data for modern modules. The NREL degradation compendium (Ref 3.9) may help.
- Wind fatigue under climate change is under-researched relative to solar degradation. Our Palmgren-Miner approach is standard engineering but the climate input (SCVR_sfcWind) is novel.

---

## Layer 4: Financial Translation (CFADS / NAV)

### What We Do

Two-channel model: Channel 1 (HCR -> BI_loss, additive) + Channel 2 (EFR -> generation decline, multiplicative + IUL truncation). CFADS_adjusted = Revenue x (1-EFR) - BI_loss - OpEx. NAV impairment via discounted cash flow.

**Internal docs:** [09_nav_impairment_chain.md](../learning/C_financial_translation/09_nav_impairment_chain.md) | [cashflow_integration.md](../discussion/hcr_financial/cashflow_integration.md)

### Closest Existing Methods

**Climate-adjusted project finance** is emerging. A 2022 paper in Renewable and Sustainable Energy Reviews explicitly integrates CMIP6 scenarios into DSCR/IRR analysis for energy infrastructure. The EDHEC Infrastructure Institute's "Highway to Hell" report quantifies climate-induced NAV impairment for infrastructure portfolios.

**TCFD physical risk quantification** provides the disclosure framework. Most firms use scenario analysis but stop at hazard exposure — they don't translate to cash flow impact at the asset level. Our framework goes further by computing CFADS_adjusted per year.

**Insurance actuarial models** are the closest in sophistication. Swiss Re, Munich Re, and catastrophe modelling firms (Verisk, Moody's RMS) model physical risk -> financial impact, but for insurance portfolios, not project finance. The two-channel structure (BI + degradation) is inspired by insurance loss categorisation.

### Key References

| Ref | Citation | DOI / URL |
|-----|----------|-----------|
| 4.1 | Zhou, S. et al. (2022). "Climate-related financial risk assessment on energy infrastructure investments." *Renewable and Sustainable Energy Reviews*, 157. | [doi:10.1016/j.rser.2021.112070](https://doi.org/10.1016/j.rser.2021.112070) |
| 4.2 | Hain, D. et al. (2021). "Pricing climate-related risks of energy investments." *RSSER*, 141. | [doi:10.1016/j.rser.2021.110815](https://doi.org/10.1016/j.rser.2021.110815) (verify) |
| 4.3 | EDHEC Infrastructure & Private Assets Research Institute. "Highway to Hell: Climate Change Will Cost Hundreds of Billions to Investors in Infrastructure." | [edhec.infrastructure.institute](https://edhec.infrastructure.institute/paper/highway-to-hell/) (verify slug) |
| 4.4 | Ekeland, J. et al. (2022). "Decoupled Net Present Value: Protecting Assets Against Climate Change Risk." *Sustainability*, 14. | [doi:10.3390/su14127090](https://doi.org/10.3390/su14127090) (verify) |
| 4.5 | EDHEC Climate Institute. "Including Climate Risks in Infrastructure Asset Valuation." | [edhec.infrastructure.institute](https://edhec.infrastructure.institute/) (search publications) |
| 4.6 | Wang, C. et al. (2024). "Asset-level assessment of climate physical risk matters for adaptation finance." *Nature Communications*, 15. | [doi:10.1038/s41467-024-48820-1](https://doi.org/10.1038/s41467-024-48820-1) (verify) |
| 4.7 | Bank of England (2024). "Measuring climate-related financial risks using scenario analysis." Staff Working Paper. | [bankofengland.co.uk](https://www.bankofengland.co.uk/working-paper/2024/) (search 2024 papers) |
| 4.8 | NGFS (2021). "Guide to Climate Scenario Analysis for Central Banks and Supervisors." | [ngfs.net](https://www.ngfs.net/en/list/publications/guide-climate-scenario-analysis) |
| 4.9 | Basel Committee on Banking Supervision (2021). "Climate-related financial risks — measurement methodologies." | [bis.org/bcbs/publ/d518.htm](https://www.bis.org/bcbs/publ/d518.htm) |
| 4.10 | TCFD (2017). "Recommendations of the Task Force on Climate-related Financial Disclosures." | [fsb-tcfd.org](https://assets.bbhub.io/company/sites/60/2021/10/FINAL-2017-TCFD-Report.pdf) |
| 4.11 | "The Climate-Related Financial Risks Measurement Methodologies: Advances, Challenges, and Frontiers." *ScienceDirect*, 2025. | Verify exact journal and DOI |
| 4.12 | Swiss Re Institute. "The Economics of Climate Change: No Action Not an Option." | [swissre.com](https://www.swissre.com/institute/research/topics-and-risk-dialogues/climate-and-natural-catastrophe-risk/expertise-publication-economics-of-climate-change.html) |
| 4.13 | Giuzio, M. et al. (2023). "Physical Climate Risk Factors and an Exploration of Their Potential to Subsume Insurance-Related Indicators." *Federal Reserve Bank of New York Staff Report No. 1066.* | [newyorkfed.org/research/staff_reports/sr1066](https://www.newyorkfed.org/research/staff_reports/sr1066) |
| 4.14 | "Solving the Puzzle: Renewable Energy's Complex BI Claims." *Risk & Insurance*, 2024. | [riskandinsurance.com](https://riskandinsurance.com/) (search for title) |
| 4.15 | PV Tech (2024). "Why solar insurers are tightening BI and equipment breakdown terms." | [pv-tech.org](https://www.pv-tech.org/) (search for title) |

### Gaps & Opportunities

- The two-channel architecture (additive BI + multiplicative degradation) is standard in insurance but novel for project finance climate risk. No published project finance model separates channels this way.
- baseline_BI_pct (revenue fraction lost per unit of hazard) is the weakest parameter. Insurance loss databases (NFIP, IBHS) may provide empirical calibration data.
- IUL (Impaired Useful Life) from cumulative EFR is our contribution — no published framework computes life truncation from climate-driven degradation and flows it through CFADS.
- The EDHEC "Highway to Hell" report (Ref 4.3) is the best external benchmark for expected magnitudes.

---

## Layer 5: End-to-End Frameworks & Commercial Platforms

### What Exists

Several commercial platforms model physical climate risk for assets, but with important differences from LTRisk:

**Jupiter Intelligence (ClimateScore Global):** 22.3 billion locations, 22K+ metrics, 9 perils. Statistical downscaling of CMIP6 at 90m. Validated for enterprise MRM. Most sophisticated commercial platform but proprietary and opaque.

**XDI (Cross Dependency Initiative):** Engineering-based assessment. 175+ countries. Founded 2007 — longest-standing independent physical risk specialist. Asset-level analysis with hazard-specific vulnerability curves.

**Moody's / Four Twenty Seven:** 2M+ corporate sites, 6 hazards. Acquired by Moody's 2019. Country/company-level exposure scores. Less asset-specific than Jupiter/XDI.

**S&P Trucost (Sustainable1):** 4M+ asset locations, 9 hazards, proprietary impact functions for 250+ asset types. Uses CMIP6. Most detailed publicly documented methodology.

### Critical Finding: Platform Divergence

A 2024 CarbonPlan comparison study found that Jupiter and XDI (the only two platforms that shared data) agree on only 12% of fire risk predictions (California) and 21% of coastal flood predictions (NYC). This divergence despite using similar CMIP6 inputs highlights the enormous methodological uncertainty in this space.

### Key References

| Ref | Citation | DOI / URL |
|-----|----------|-----------|
| 5.1 | CarbonPlan — Climate risk comparison research, 2024. | [carbonplan.org/research](https://carbonplan.org/research) |
| 5.2 | Insurance Journal (2024). "Clashing Risk Predictions Cast Doubt on Black Box Climate Models." | [insurancejournal.com](https://www.insurancejournal.com/) (search for title) |
| 5.3 | ESMA (2024). "Assessing portfolio exposures to climate physical risks." | [esma.europa.eu](https://www.esma.europa.eu/) (search publications 2024) |
| 5.4 | "Let's Get Physical: Comparing Metrics of Physical Climate Risk." *ScienceDirect*, 2021. | [doi:10.1016/j.jbankfin.2021.106185](https://doi.org/10.1016/j.jbankfin.2021.106185) (verify) |
| 5.5 | UNEP FI (2024). "The Climate Risk Landscape." | [unepfi.org](https://www.unepfi.org/themes/climate-change/the-climate-risk-landscape/) |
| 5.6 | GARP. "The Complexity Cascade: Why Physical Risk Models Diverge." | [garp.org](https://www.garp.org/) (search Risk Intelligence) |
| 5.7 | McKinsey & Company. "Using Model Risk Management to Address Climate Analytics." | [mckinsey.com](https://www.mckinsey.com/capabilities/risk-and-resilience/our-insights/) (search for title) |
| 5.8 | Willis Towers Watson (2023). "A Higher Standard for Climate Risk Modeling?" | [wtwco.com](https://www.wtwco.com/) (search insights) |
| 5.9 | Byers, E. et al. (2023). Same as 2.16. | See 2.16 |

### Where LTRisk Differs

| Dimension | Commercial Platforms | LTRisk |
|-----------|---------------------|--------|
| Transparency | Proprietary / black box | Open equations, documented methodology |
| Asset specificity | Generic asset types (250+ categories) | Specific to solar and wind project finance |
| Financial integration | Exposure scores / damage functions | Direct CFADS / NAV / DSCR computation |
| Degradation channel | Typically absent or simplified | Explicit EFR with Peck's, Coffin-Manson, Palmgren-Miner |
| Two-channel separation | Not standard | BI (additive) + EFR (multiplicative) + IUL (truncation) |
| Uncertainty characterisation | Limited / undisclosed | Report Card, FIDUCEO mapping, per-hazard confidence |

---

## Cross-Cutting References

### Validation & Backtesting

| Ref | Citation | DOI / URL |
|-----|----------|-----------|
| V.1 | Bank of England (2024) — "Historical data is insufficient for future climate risk." | See 4.7 |
| V.2 | ScienceDirect (2025) — "Climate-Related Financial Risks Measurement Methodologies." | See 4.11 |
| V.3 | McKinsey — MRM for climate analytics. | See 5.7 |
| V.4 | "Validation of Catastrophe Flood Models." *Journal of Flood Risk Management*, 2024. | [doi:10.1111/jfr3](https://doi.org/10.1111/jfr3) (search for exact title) |

### FIDUCEO & Measurement Uncertainty

| Ref | Citation | DOI / URL |
|-----|----------|-----------|
| U.1 | FIDUCEO Project (H2020 Grant No. 638822, 2015-2019), University of Reading. | [fiduceo.eu](https://www.fiduceo.eu/) |
| U.2 | Merchant, C.J. et al. (2017). "Uncertainty Information in Climate Data Records from Earth Observation." *ESSD*, 9, 511-527. | [doi:10.5194/essd-9-511-2017](https://doi.org/10.5194/essd-9-511-2017) |
| U.3 | JCGM. "Guide to the Expression of Uncertainty in Measurement" (GUM), JCGM 100:2008 / GUM-1:2023. | [bipm.org](https://www.bipm.org/en/committees/jc/jcgm/publications) |
| U.4 | "A Practical Introduction to Utilising Uncertainty Information in Climate Analysis." Springer, 2025. | Verify exact DOI on Springer |

**Internal doc:** [FIDUCEO uncertainty mapping](../discussion/uncertainty/FIDUCEO-Style%20Uncertainty%20Mapping_%20LTRisk.md)

### Renewable Energy & Climate Change (General)

| Ref | Citation | DOI / URL |
|-----|----------|-----------|
| G.1 | Dunnett, T. et al. (2025). "Strategies for climate-resilient global wind and solar power systems." *Nature*. | [doi:10.1038/s41586-024-08425-w](https://doi.org/10.1038/s41586-024-08425-w) (verify) |
| G.2 | Solaun, B. & Cerda, E. (2020). "Climate change impacts on renewable energy supply." *Nature Climate Change*, 10. | [doi:10.1038/s41558-020-0802-8](https://doi.org/10.1038/s41558-020-0802-8) (verify) |
| G.3 | Solaun, B. & Cerda, E. (2019). "Climate change impacts on renewable energy generation. A review of quantitative projections." *RSSER*, 116. | [doi:10.1016/j.rser.2019.109415](https://doi.org/10.1016/j.rser.2019.109415) |
| G.4 | IEA (2024). "Climate Resilience: Power Systems in Transition." | [iea.org/reports/climate-resilience](https://www.iea.org/reports/climate-resilience) |
| G.5 | WMO (2024). "How climate insights drive a more reliable renewable energy transition." | [wmo.int](https://wmo.int/) (search for title) |
| G.6 | Bloomberg (2025). "Investors Want to Understand How Wild Weather Threatens Clean Energy." | [bloomberg.com](https://www.bloomberg.com/) (search Bloomberg Green) |

---

## Summary: What's Novel in LTRisk vs the Literature

1. **SCVR Report Card as a routing mechanism** — No published method uses tail confidence classification to route variables to different downstream models (Pathway A vs B, Channel 1 vs 2).

2. **Two-channel financial architecture** — The separation of additive BI (Channel 1) from multiplicative degradation + life truncation (Channel 2) is novel for project finance. Insurance does this implicitly but not for DCF/NAV models.

3. **Coffin-Manson fed by direct CMIP6 freeze-thaw counts** — Standard practice estimates cycle counts from mean temperature. Direct daily counting from 28-model pooled output is novel.

4. **IUL (Impaired Useful Life) from cumulative EFR** — No published framework computes asset life truncation from climate-driven degradation and flows it through CFADS.

5. **Transparent, per-hazard confidence levels** — Commercial platforms provide single scores. LTRisk documents per-hazard proxy quality, pathway choice, and uncertainty sources.

6. **End-to-end from CMIP6 daily -> NAV** — Individual components exist separately. The full pipeline in one transparent framework, specifically for renewable project finance, is new.

---

## Recommended Reading Priority

For someone new to the LTRisk project, read in this order:

1. **IPCC AR6 Chapter 11** (Ref 1.1) — foundational climate science
2. **Multi-hazard framework for power generation** (Ref 2.16) — closest published equivalent
3. **Joule 2025 PV degradation paper** (Ref 3.7) — external validation of EFR approach
4. **EDHEC "Highway to Hell"** (Ref 4.3) — infrastructure NAV impairment context
5. **CarbonPlan comparison** (Ref 5.1) — why transparency matters
6. **S&P Trucost methodology** (Ref 1.9) — commercial benchmark

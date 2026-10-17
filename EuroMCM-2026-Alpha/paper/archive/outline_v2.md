# Archived v2 outline — superseded by paper/outline.md

Working title: **Resource Competition, Recursive Self-Improvement, and the Conditions for Human Viability**

> **Compilation status:** the LaTeX draft has not been compiled because no LaTeX engine is installed in the current environment. The `.tex` source is provided for the next teammate to compile and edit.

## Abstract

A unified resource-allocation framework is used to connect historical hominin competition with conditional future RSI scenarios. The same weighted proportional-fair operator is used in both. Historical compatibility is treated as an order-of-magnitude exercise, not causal validation. Future outcomes are conditional scenario calculations, not forecasts. The main analytic results are a single-resource allocation formula, a relative-advantage condition, an efficiency-expansion threshold, an industrial self-sufficiency threshold, and a conditional forward-invariance certificate for a human population floor. Numerical experiments show a narrow historical compatibility region, a conservative alignment certificate, and a strong dependence of outcome probabilities on the disclosed parameter measure, with a clear separation between the pre-specified measures and the post-hoc stress-augmented measure.

## 1. Introduction and modeling philosophy

- Research question and scope.
- Why historical and future cases must share one allocation operator.
- Evidence hierarchy: SOURCE / ESTIMATE / ASSUMPTION.
- What the paper does not claim.

## 2. Unified resource-allocation framework

- State, demands, supplies, weights, units.
- Fixed-proportion satisfaction and weighted proportional fairness.
- KKT conditions and shadow prices.
- Boundary extension and zero populations.
- Proposition 1 (single-resource formula).
- Exact two-group polygon solver.

## 3. Historical competition and compatibility

- Historical states and resources.
- Historical ODE and effective extinction threshold.
- Proposition 2 (relative advantage).
- Boundary equilibria and invasion conditions.
- Compatibility set and non-identifiability.
- Results: baseline `T_rep = 2867.46 yr`; 14/650 European-compatible; H0/H1 both compatible.
- Figures 1–2, Table of sensitivity.

## 4. Resource-constrained RSI dynamics

- `H`, `A`, `q`; operational vs construction energy; land partition.
- Manufacturing and industrial dependency.
- Proposition 3 (efficiency–expansion).
- Proposition 4 (industrial self-sufficiency).
- Finite-horizon extinction screen.
- Scenario results A/B/C/stress; human-free counterfactual.
- Controlled human-demography x AI-pressure factorial.
- Figures 3–4 and Figure S8.

## 5. Alignment and human viability

- Operational alignment definition; `b_H`, `s_H >= a b_H`.
- Endpoint-consistent construction budget.
- Three exhaustive outcomes.
- Proposition 5 (population-floor invariance) and `a_safe`.
- Stress phase diagram; `a_safe=0.6`, numerical `a_num_pop=0.4`.
- Fixed-policy safe slices and horizon sensitivity.
- Figure 5, supplemental figures.

## 6. Uncertainty and structural robustness

- Three pre-specified measures; iid sampling; failed-run handling.
- Separate post-hoc `stress_augmented` exploratory measure, clearly labeled.
- Wilson intervals; probability table for both blocks.
- Controlled 2x2 human-demography x AI-pressure factorial.
- Rank sensitivity and dual candidate measurement priorities (pre-specified vs exploratory).
- Structural robustness over 80 tested pairs for both libraries; pre-specified robust population-floor set `{0.2,0.4,0.6,0.8,1.0}`, exploratory `{0.6,0.8,1.0}`; robust non-marginal empty in both.
- Figure 6 and supplemental Figures S4-S7.

## 7. Discussion and limitations

- Historical non-identifiability and missing mechanisms.
- RSI parameter uncertainty and aggregate modeling.
- The population-floor certificate is not a welfare guarantee.
- Scenario probabilities are not real-world extinction probabilities.
- Numerical non-monotonicity and finite-library robustness.
- Outstanding problem requirements: interventions/timing, ENOCH letter, summary sheet, references, AI-use report.

## Appendices

- A. Parameter provenance table (excerpt).
- B. Numerical verification and tests.
- C. Reproduction commands.

## Figure/table mapping

- Fig. 1: `results/figures/fig1_historical_trajectories.pdf`
- Fig. 2: `results/figures/fig2_historical_compatibility.pdf`
- Fig. 3: `results/figures/fig3_rsi_scenarios.pdf`
- Fig. 4: `results/figures/fig4_rsi_resources.pdf`
- Fig. 5: `results/figures/fig5_alignment_phase.pdf`
- Fig. 6: `results/figures/fig6_uq_probabilities.pdf`
- Tables: `results/tables/parameter_table.csv`, `historical_sensitivity.csv`, `rsi_scenario_summary.csv`, `alignment_summary.txt`, `uq_probabilities.csv`, `structural_robustness_summary.csv`.

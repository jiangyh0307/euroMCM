# ARCHIVED v2 limitations — current document is docs/limitations.md

# Limitations

## Reliability revision notes (v2)

- The v1 allocator could return a spurious optimum for extremely small positive populations because the tiny group's resource use fell below the feasibility tolerance while its utility gain did not. A follow-up audit also found that the single-resource relaxation included zero-demand groups in its analytic weight denominator. Both are fixed; the denominator now uses only positive-demand groups, and regression tests cover populations down to `1e-40` and the zero-demand case. The historical and RSI experiments were re-run after the fixes.
- The previously observed adaptive-integrator chatter was partly caused by this allocator defect, not only by non-smooth `min`/active-set switches. The adaptive solver now completes the previously hanging case and agrees with fixed-step RK4 on a regression test. Fixed-step RK4 remains the default for robustness, but the earlier claim that the chatter was purely structural was too strong.
- The three primary UQ measures are now the original pre-specified ranges. The narrow stress-like measure is retained as `stress_augmented`, explicitly labeled post-hoc and exploratory. The earlier v1 report incorrectly treated the post-hoc range as the main aggressive measure.
- A controlled 2x2 factorial now separates human demography from AI pressure. Extinction in the joint stress scenario requires both faster human demography and stress AI in this design; neither alone produces extinction within the horizon.
- Alignment phase diagrams and safe-state slices now use actual grid coordinates (`pcolormesh`), not equal-spacing `imshow` with log axes.

## Historical

- The exercise is a **compatibility** analysis, not causal validation of Neanderthal disappearance.
- The parameter family is strongly non-identifiable. Common weight scaling, resource-unit scaling, population/supply scaling, and demographic time scaling leave observables unchanged; the extinction threshold is an extra convention. The 2.2% compatible fraction is specific to the grid design and fixed remaining parameters.
- Adult energy ranges are extrapolated to whole-population effective demand without age/sex structure. The disputed 10:1 density ratio is not imposed as a European initial condition.
- The model omits migration, spatial contact, stochasticity, disease, assimilation, and local resource depletion. It uses a homogeneous region and constant supplies.
- The land resource is not binding in the baseline; the fit is driven mainly by energy demand and demography. Other parameter choices could produce compatibility for different reasons.
- `T_rep` is a threshold-crossing time, not an observed extinction date. Censored runs are not replaced by the horizon.

## RSI

- No RSI parameter is empirically calibrated. The hardware unit, AI energy intensity, capability index, acquisition weight, automation threshold, manufacturing capacity, and construction energy are scenario assumptions.
- The model is aggregate and deterministic. It omits supply chains, rare-component constraints, grid stability, cooling water, permitting, finance, policy, and spatial land competition.
- Energy supply is exogenous. The human-free counterfactual therefore does not prove autonomous power-plant operation or full industrial autarky.
- The three-state model treats resource-driven hardware loss as completed decommissioning. It does not represent idle-but-unremoved capacity, repair, or partial reuse. Facility land is a fixed precommitment, not an endogenous market.
- The manufacturing function is a reduced-form aggregate. The diminishing human term is an assumption; the additive alternative can produce different transient behaviour.
- The allocation is weighted proportional fairness with a human floor. It is not a behavioural model of AI or human institutions. The priority rule is a structural stress test, not a predicted policy.
- The fixed-step RK4 integrator is used because the min/active-set switches can make adaptive error control chatter. Time-step convergence was checked on representative scenarios, but no formal global error bound is claimed. `solve_ivp` remains available for smooth comparisons.

## Alignment and viability

- Alignment is an operational resource-protection parameter, not a measure of AI intent, corrigibility, or institutional enforcement.
- The population-floor certificate is sufficient under strong assumptions: uniform resource floors, exact floor enforcement, locally Lipschitz well-posed dynamics, and forward invariance of all other state constraints. If these fail, the certificate does not apply.
- The certificate does not guarantee resource welfare, social stability, or non-marginal survival. A safe population floor can coexist with `s_H < s_min`.
- `a_safe` can exceed 1; this means the certificate is unavailable, not that extinction is certain.
- Numerical safe sets are fixed-policy finite-horizon grids, not control viability kernels. They depend on initial `H0`, the `(A0,q0)` grid, thresholds, and horizon.
- Numerical results are not monotone in alignment; no unique critical alignment is claimed. The observed non-monotonicity is retained and reported.

## Uncertainty and robustness

- Scenario probabilities are not objective probabilities of real-world extinction. The labels conservative/central/aggressive describe the pre-specified RSI expansion-pressure design, not verified bounds on harm. The `stress_augmented` measure is post-hoc and must not be presented as a pre-registered comparison or forecast.
- Independent sampling and the chosen supports are assumptions. Correlated inputs, structural breaks, and model misspecification are not represented.
- Wilson intervals cover sampling error only. Rank correlations are associations; they do not identify causal mechanisms. The candidate measurement ranking is model- and measure-dependent: the pre-specified measures emphasize land service and human demography, while the post-hoc stress measure emphasizes AI energy intensity. `E_total` and `xi` are the only inputs near the top of both rankings.
- The robust alignment set is an intersection over a finite tested library. It is not a continuous robust viability kernel and does not cover untested model structures.
- No Expected Value of Information calculation is reported; the EVPI framework is left for P1.

## Paper-level

- The draft is a first technical version, not a 25-page competition paper. The summary sheet, ENOCH letter, reference verification, AI-use report, and final typesetting remain outstanding.
- The original problem also requires at least two human intervention policies and timing comparisons (Part V). These are not implemented here. The current results should not be presented as a complete answer to the problem.

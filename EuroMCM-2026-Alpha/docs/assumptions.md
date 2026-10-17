# Assumptions and evidence hierarchy

## Evidence labels

Every numerical input in `results/tables/parameter_table.csv` has one of:

- **SOURCE** — reported in the problem statement or independently verifiable. The historical bands, density ratio, adult energy ranges, and IEA data-centre statistics are in this category. We have not independently re-checked the underlying publications.
- **ESTIMATE** — a transparent derivation from evidence with an explicit approximation, such as the rounded IEA-implied electricity scale. The selected whole-population energy means are instead ASSUMPTION: no age/sex aggregation was supplied to derive them.
- **ASSUMPTION** — an exploratory scenario value with no empirical calibration. All demographic rates, acquisition weights, RSI capability/energy parameters, land budgets, thresholds, and horizons are in this category unless noted.

A derived quantity is not promoted to SOURCE because it appears in an equation. The executable provenance registry is `src/alpha/parameters.py`; the CSV is generated from it.

## Historical model

1. **Common region and scale.** `N` and `M` are persons in one fixed, spatially homogeneous region. Migration and local contact geography are omitted.
2. **Resources.** Food energy (`kcal/yr`) and effective land/habitat access (`km^2`) are separate resources with separate units. The energy requirement is `365 m_i` kcal/person/year. `m_i` is a whole-population adult-equivalent approximation; the problem's 3,000–7,000 kcal/day figures are adult estimates. The 100–350 kcal/day difference is applied to effective per-person demand only under this approximation.
3. **Fixed-proportions satisfaction.** A group's satisfaction `s_i` scales its entire resource bundle. One resource cannot substitute for another.
4. **Proportional fairness.** The baseline allocation is weighted proportional fairness with weights `W_i = w_i P_i`. Land and food are not added together; the optimizer handles each constraint in its own unit.
5. **No extra carrying capacity.** Resource scarcity is the only density-dependent feedback in the baseline. If `beta_i < delta_i`, a group declines even at full satisfaction; such a run is not evidence of competition.
6. **Effective extinction.** `N_crit = kappa N_ref` is a convention, not an observed extinction event. Deterministic positive trajectories do not reach zero in finite time. Runs without a crossing are right-censored.
7. **Compatibility, not validation.** A parameter set that produces 2,600–5,400 years is compatible with the reported European duration. It is not a causal explanation, a posterior probability, or a calibrated history. The France/northern Spain band and the disputed 10:1 density ratio are treated as separate regional constraints, not as a European initial condition.

## RSI model

1. **Hardware units.** `A` is in hardware-equivalent units. The mapping from these units to real accelerators, power, or cost is not empirically calibrated. `q` is a dimensionless capability index; hardware scale and capability are separate.
2. **Resource services.** Human energy `e_H` is essential electricity/service energy, not metabolic calories. AI energy `e_A(q)=e_0 q^{-xi}` is a scenario law. Land service `ell_A A` is allocable supporting land; facility footprint `ell_site A` is a separate, precommitted physical stock.
3. **Construction budget.** The baseline is endpoint-consistent: `R_build = min(rho E_total, [E_total - a b_H^tot e_H H]_+)`, and the allocation uses `E_op = E_total - R_build`. The fixed-split rule `R_build = rho E_total` is retained only as a comparison. Unused construction budget is not automatically reallocated.
4. **Stock-flow separation.** Operational energy and construction energy are separate flows and never draw on the same MWh twice. Hardware addition is bounded by desired expansion, manufacturing, construction energy, and site capacity. Installed hardware occupies its facility site.
5. **Decommissioning.** The `delta_A A + mu_A(1-s_A)A` terms are interpreted as **completed physical decommissioning** for the three-state model. A merely powered-down but unremoved machine still occupies land. A four-state idle-capacity model is left for P1.
6. **Human industrial dependence.** Manufacturing is an aggregate `min(M_max, c_H(1-zeta)H/H_ref + c_A zeta A s_A)` in the baseline. This is not a chip-supply-chain model. The diminishing human term is a substantive substitution assumption; the additive alternative is a structural check.
7. **Exogenous power.** `E_total` is a prescribed annual energy flow. The baseline does not model power-plant operation or its dependence on human industry. The human-free counterfactual therefore conditions on continued power supply.
8. **Land partition.** `L_total = L_site + L_service + L_other` is a fixed disjoint simplification. Facility land is never reallocated as human land service. Idle or decommissioned equipment does not automatically return its site unless the decommissioning flow is explicit.
9. **RSI laws.** The saturating capability law and the automation function are scenario functions, not empirical laws. The non-saturating alternative is a structural sensitivity. `omega`, `xi`, `gamma`, `q_c`, `nu`, and all rates are ASSUMPTION values.

## Alignment and outcomes

1. **Operational definition.** `a` is the protected fraction of the human physically attainable basic satisfaction `b_H`. It is not a measurement of AI intent or a guarantee about goals.
2. **Construction endpoint.** The endpoint-consistent budget is needed so that `a = 1` cannot be defeated by a fixed construction reservation. The proof is relative to the precommitted land partition.
3. **Thresholds.** `H_ext`, `H_min`, `s_min`, `T`, `W_window`, and `p_tol` are classification conventions. Baseline values are not observed human-safety standards. The final-window bad fraction uses a strict inequality; equality at a threshold passes.
4. **Three outcomes.** Extinction, marginal survival, and non-marginal survival are mutually exclusive and exhaustive for successful runs. Failed/infeasible runs are reported separately and excluded from the probability denominator.
5. **Certificate.** `a_safe = delta_H/(beta_H b_under)` is a sufficient population-floor condition under the stated resource-floor, regularity, and forward-invariance assumptions. It is not necessary, does not guarantee `s_H >= s_min`, and is not an absolute real-world safety guarantee.

## Uncertainty

1. **Scenario measures, not reality.** `Pi_conservative`, `Pi_central`, and `Pi_aggressive` are earlier broad exploratory ranges. None is preregistered. The broad aggressive measure covers high RSI pressure but is not the later narrow stress corner. Frequencies are conditional on the range and model structure, and jointly vary demography and resources in the old experiments.
2. **Post-hoc stress-augmented measure.** `Pi_stress_augmented` was constructed after exploratory runs to exercise the extinction boundary. It is explicitly post-hoc, not pre-registered, and is reported separately. It is not a forecast and is excluded from the primary measurement ranking.
3. **Independence.** The baseline Monte Carlo samples inputs independently. This is an assumption, not a claim about real-world dependence.
4. **Intervals.** Wilson intervals cover pointwise iid sampling error only. They exclude structural uncertainty, scenario-prior error, and dependence.
5. **Sensitivity.** Spearman correlations are associations under exploratory ranges, not causal effects or variance decompositions. The old rankings are conditional and not unique measurement priorities. The later stress range must be distinguished from the earlier broad ranges.
6. **Robustness.** The structural intersection is over a finite tested library (20 samples x 4 structures x 6 alignments), separately for broad aggressive and later narrow stress ranges. It is not a continuous-domain robust viability kernel. Failed runs must prevent a claim that the entire library is safe.

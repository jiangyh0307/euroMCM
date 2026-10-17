# ARCHIVED v2 results — superseded by docs/results.md and docs/p0_acceptance.md

Historical snapshot only. In particular, the pre-specified terminology and
full-validation implications below are not current claims. All ranges were exploratory.

# Computed results (v2, reliability-revised)

All numbers below were produced by the scripts in `experiments/` and the tests in `tests/`. They are conditional on the scenario assumptions recorded in `src/alpha/parameters.py`, `src/alpha/scenarios.py` and `configs/`. They are **not** empirical estimates of Neanderthal demography, future AI behaviour, or real-world extinction risk.

Reproduction:

```bash
PYTHONPATH=src python3 experiments/run_historical.py
PYTHONPATH=src python3 experiments/run_rsi.py
PYTHONPATH=src python3 experiments/run_alignment.py
PYTHONPATH=src python3 experiments/run_uq.py --n 100 --seed 2026 --dt 1.0
PYTHONPATH=src python3 -m pytest -q tests
```

## 0. Reliability revision (what changed from v1)

- **Tiny-population allocator bug fixed.** With a population such as `1e-20`, the v1 polygon solver could return satisfaction `[1.0, 0.5]` where the analytic single-resource solution is `[0.5, 0.5]`, because the tiny group's resource use was below the feasibility tolerance while its utility gain was not. The allocator now uses a robust single-resource relaxation before polygon enumeration. Regression tests cover `1e-8` through `1e-40`.
- **Zero-demand group fix.** The first version of the single-resource relaxation included zero-demand groups in the analytic weight denominator, which could return `s=[0.25,1]` instead of `[0.5,1]` for a zero-demand second group. The denominator now uses only positive-demand groups; the existing zero-demand test is part of the 41-test suite.
- **Integrator chatter traced and tested.** The previously hanging adaptive `solve_ivp` case now completes in about 0.6 s and agrees with fixed-step RK4 at `1e-5` relative tolerance in `H`. A regression test compares the two integrators.
- **Scenario transparency restored.** The three pre-specified measures are conservative, central and aggressive. The aggressive measure is the original broad range. The earlier, post-hoc narrow measure is now called `stress_augmented` and is reported separately as exploratory, not as a pre-registered comparison.
- **Controlled 2x2 stress factorial added.** Human demography (baseline/fast) is crossed with AI pressure (baseline/stress) to separate the effect of AI from the effect of human demographic assumptions.
- **Alignment figures use actual grid coordinates.** `pcolormesh` replaces the distorted equal-spacing `imshow` for the phase diagram and safe-state slices.
- Current tests: **41 passed**.

## 1. Historical compatibility

Baseline (`HistoricalParameters` defaults): `T_rep = 2867.46 yr`, `N_crit = 500`, not censored. The baseline trajectory is in `fig1_historical_trajectories.png/pdf` and `historical_baseline_trajectory.csv`. The allocator fix did not change the historical results.

Full compatibility grid: 26 acquisition-weight values x 25 birth-rate values (650 cells), including the H0 point, with `w_M/w_N` in [0.2, 2.0], `beta_M/beta_N` in [0.5, 1.5], all other parameters fixed at the baseline.

|Quantity|Value|
|---|---|
|Valid runs|650|
|Errors|0|
|European-compatible (`2600 <= T_rep <= 5400`)|14 (2.15%)|
|Regional-compatible (`1400 <= T_rep <= 2900`)|30 (4.62%)|
|Censored (`T_rep > 10,000`)|325|
|Median crossed `T_rep`|525.64 yr|
|Minimum / maximum crossed `T_rep`|260.28 / 9538.87 yr|
|H0 cell (`w_M/w_N = beta_M/beta_N = 1`)|`T_rep = 2869.10 yr`, compatible|

The compatible region is a narrow diagonal band (Figure 2). H0 has a compatible cell; H1 has 13 compatible cells (6 with `w_M/w_N > 1`, 7 with `< 1`). Thus this exercise does **not** distinguish H0 from H1; both can be made compatible by changing the birth-rate ratio and acquisition weights. The fraction is a design-measure fraction, not a posterior probability.

### Sensitivity (baseline elsewhere)

|Analysis|Value|`T_rep` (yr)|Status|
|---|---|---:|---|
|threshold fraction `kappa`|0.001|3757.29|crossed|
||0.005|3135.76|crossed|
||0.01|2867.46|crossed|
||0.02|2598.23|crossed|
||0.05|2239.09|crossed|
|initial ratio `M0/N0`|0.01|3696.24|crossed|
||0.05|3118.87|crossed|
||0.1|2867.46|crossed|
||0.5|2281.20|crossed|
||1.0|2033.65|crossed|
||10.0|1211.30|crossed|
|energy difference `m_N-m_M`|100|5593.98|crossed|
||200|2867.46|crossed|
||350|1698.22|crossed|
|H0 (`w_M=w_N`), `beta_M/beta_N`|0.9|censored|>10,000|
||1.0|2867.46|crossed|
||1.1|1310.64|crossed|
|H1 (`w_M=1.2 w_N`), `beta_M/beta_N`|0.9|1456.20|crossed|
||1.0|887.72|crossed|
||1.1|664.74|crossed|

The extinction-threshold and initial-ratio choices materially change the reported time. The energy difference has a strong effect: the problem-reported 100-350 kcal/day range maps to roughly 1,700-5,600 years in this baseline scenario, spanning both compatibility bands. This is an order-of-magnitude compatibility result, not a calibration.

## 2. RSI scenarios

`rsi_scenario_summary.csv` contains all values. Key results at `a = 0.5`:

|Scenario|Outcome|`min H`|Final `H`|Final `A`|Final `q`|Final `s_H`|`q_self` crossed?|
|---|---|---:|---:|---:|---:|---:|---|
|A: low RSI growth|non-marginal|8.00e9|2.16e10|1.68e5|5.22|0.926|no|
|B: moderate RSI growth|non-marginal|8.00e9|2.11e10|4.26|100.00|0.853|yes|
|C: rapid RSI/automation|marginal|8.00e9|8.87e9|9.08e5|100.00|0.500|yes|
|Stress (joint human+AI)|marginal|7.48e7|7.48e7|9.03e5|100.00|0.500|yes|

At `a = 0`, the joint stress scenario reaches `H = H_ext = 1e6` at `t = 68.86 yr` (extinction). At `a = 1`, no scenario reaches extinction by 100 years; the low and moderate scenarios are non-marginal, and the rapid/stress scenarios are marginal because human resource adequacy falls below `s_min = 0.8`. Scenario A's AI is not self-sustaining in the human-free counterfactual (`A_end/A_0 = 0.0073`); B, C and stress are self-sustaining in that counterfactual (`A_end/A_0` about 90.5-90.9). The counterfactual still assumes exogenous electricity supply.

### Controlled 2x2 stress factorial

`controlled_stress_factorial.csv` separates human demography from AI pressure. At `a=0`:

|Arm|Outcome|`min H`|Extinction time|
|---|---|---:|---:|
|baseline human + baseline AI|non-marginal|8.00e9|—|
|baseline human + stress AI|marginal|3.57e9|—|
|fast human + baseline AI|marginal|1.00e8|—|
|fast human + stress AI|extinction|1.00e6|68.86 yr|

Neither faster human demography alone nor stress AI alone produces extinction in this 2x2 design. Extinction requires both in this scenario. The baseline-human + stress-AI arm remains above the finite-horizon lower bound. This is a model-scenario result, not a claim about real human demography.

## 3. Alignment and viability

Stress scenario, `a` grid 0 to 1 in 0.1 steps, `eta` grid {0.02, 0.05, 0.1, 0.2, 0.5, 1.0}:

- Analytic sufficient population-floor threshold: `a_safe = 0.600` (`b_under = 1.0`, `r_H = 0.6`).
- Numerical minimum population-floor alignment on the 0.1 grid: `a_num_pop = 0.4` (at `eta = 0.5`).
- The analytic certificate is conservative: it guarantees the floor at `a >= 0.6`, while the numerical grid first satisfies the floor at `a = 0.4`.
- Non-marginal survival was not achieved in the stress scenario at any tested `(a, eta)`; the phase diagram is extinction at low `a` and higher `eta`, marginal elsewhere. The green category is therefore empty in Figure 5.
- Safe initial-state slices (actual grid coordinates): at `a = 0` and `a = 0.2`, all tested `(A_0, q_0)` combinations fail the population floor; at `a = 0.4`, the lower-left region is safe and high `A_0/q_0` remains unsafe (Figure S2).
- Horizon sensitivity: at `T = 50`, `a = 0` gives `min H = 9.0e6` (just below `H_min = 1e7`); at `T = 100`, `a = 0` reaches extinction; at `T = 150`, `a = 0` and `a = 0.25` reach extinction. Classification is horizon-dependent, and the numerical results are not monotone in `a` (see `alignment_scan.csv`, `p_bad` at `a = 0.8` vs `0.9`).

The analytic certificate is for the population floor only. It does not imply `s_H >= s_min`; in the stress scenario the population floor can be safe while resource adequacy remains below `s_min`.

## 4. Uncertainty quantification

100 iid draws per measure, 11 alignment values, fixed seed 2026, no failed runs. The first three measures are the pre-specified comparison; the fourth is an explicitly exploratory, post-hoc stress measure.

### Pre-specified measures

|Measure|a|P(extinction)|P(marginal)|P(non-marginal)|
|---|---:|---:|---:|---:|
|Conservative|0|0.00|1.00|0.00|
|Conservative|0.5|0.00|1.00|0.00|
|Conservative|1.0|0.00|1.00|0.00|
|Central|0|0.00|0.98|0.02|
|Central|0.5|0.00|0.98|0.02|
|Central|1.0|0.00|0.98|0.02|
|Aggressive|0|0.02 [0.006, 0.070]|0.95|0.03|
|Aggressive|0.5|0.00 [0.00, 0.037]|0.97|0.03|
|Aggressive|1.0|0.00 [0.00, 0.037]|0.96|0.04|

The pre-specified measures are dominated by marginal survival. The broad aggressive measure has a small extinction frequency at `a=0` and a few non-marginal cases; it does not show the dramatic alignment transition of the post-hoc stress measure.

### Exploratory stress-augmented measure (not pre-registered)

|a|P(extinction)|P(marginal)|P(non-marginal)|
|---:|---:|---:|---:|
|0|0.42 [0.33, 0.52]|0.58|0.00|
|0.5|0.00 [0.00, 0.037]|1.00|0.00|
|1.0|0.00 [0.00, 0.037]|0.81|0.19 [0.13, 0.28]|

This measure was constructed after exploratory runs to exercise the extinction boundary. It is not a forecast and must not be presented as a pre-registered comparison. Its transition is also non-monotone: the non-marginal fraction is about 0.43 at `a=0.8` and 0.19 at `a=1.0`.

## 5. Sensitivity screening

Rank-based screening uses `log10(min H)` at `a=0.5` and extinction at `a=0.0`; `H0` is excluded as an initial condition. These are associations under the sampled measures, not causal effects.

Pre-specified measures (top five):

|Rank|Input|Mean absolute rho|
|---:|---|---:|
|1|`L_service`|0.151|
|2|`beta_H`|0.135|
|3|`E_total`|0.128|
|4|`xi`|0.096|
|5|`omega`|0.088|

Exploratory stress-augmented measure (top five):

|Rank|Input|Mean absolute rho|
|---:|---|---:|
|1|`e0`|0.466|
|2|`r_H`|0.252|
|3|`E_total`|0.205|
|4|`xi`|0.203|
|5|`beta_H`|0.140|

The ranking is measure-dependent. Under the pre-specified measures, land-service availability and human demography dominate; under the post-hoc stress measure, AI energy intensity dominates. `E_total` and `xi` appear near the top in both. The candidate measurement list is therefore conditional: energy-supply scale and the AI energy-efficiency response are common candidates, while `e0` is a stress-conditional candidate. This is not a causal importance ranking.

Industrial-threshold timing is recorded as `q_self_crossed`/`t_q_self`; censored non-crossings are reported separately and are not imputed.

## 6. Structural robustness

20 sampled parameter vectors x {proportional, priority} x {saturating, non-saturating} x 6 alignments (80 pairs per alignment).

Pre-specified aggressive library:

- Population-floor safe fraction: 78/80 at `a=0`, 80/80 for `a>=0.2`.
- Robust population-floor set over the tested library: `{0.2, 0.4, 0.6, 0.8, 1.0}`.
- Non-marginal safe fraction: 0 at `a<=0.6`, 2/80 at `a=0.8`, 4/80 at `a=1.0`.
- Robust non-marginal set: empty.

Exploratory stress-augmented library:

- Population-floor safe fraction: 60/80 at `a=0`, 66/80 at `a=0.2`, 74/80 at `a=0.4`, 80/80 for `a>=0.6`.
- Robust population-floor set: `{0.6, 0.8, 1.0}`.
- Non-marginal safe fraction: 6/80 at `a<=0.6`, 18/80 at `a=0.8`, 16/80 at `a=1.0`.
- Robust non-marginal set: empty.

The stress-augmented 0.6 transition coincides with the analytic `a_safe=0.6`; the pre-specified aggressive library is safe at lower alignments because its population-floor failures are rarer. Both are empirical over the tested library, not continuous-domain guarantees.

## 7. Analytic finite-horizon screen

Because `H_dot = H(beta_H s_H - delta_H) >= -delta_H H`, every trajectory satisfies `H(t) >= H(0) exp(-delta_H t)`. With the baseline `H(0) = 8e9`, `delta_H = 0.01/yr`, `T = 100 yr`, the lower bound is `2.95e9`, far above `H_ext = 1e6`. Therefore **extinction within 100 years is impossible under the baseline demographic assumption regardless of alignment or AI behaviour** in this model. The conservative and central UQ results (no extinction) are consistent with this bound. The pre-specified aggressive extinction cases at `a=0` come from sampled faster-demography/high-pressure combinations; they are not baseline-demography forecasts. The controlled factorial confirms that stress AI alone with baseline human demography does not reach extinction within the horizon.

## 8. Figure and table index

|Figure|File|Content|
|---|---|---|
|1|`results/figures/fig1_historical_trajectories.png/pdf`|Historical `N`, `M`, satisfaction and `T_rep` versus compatibility bands|
|2|`results/figures/fig2_historical_compatibility.png/pdf`|`T_rep` map over `w_M/w_N` and `beta_M/beta_N`, H0 baseline, European/regional bands|
|3|`results/figures/fig3_rsi_scenarios.png/pdf`|`H`, `A`, `q`, `zeta` for scenarios A/B/C at `a = 0.5`|
|4|`results/figures/fig4_rsi_resources.png/pdf`|AI energy demand/allocation, human adequacy, construction bottlenecks, thresholds (stress, `a = 0.5`)|
|5|`results/figures/fig5_alignment_phase.png/pdf`|Alignment-RSI phase diagram and fixed-`eta` minimum population vs `a_safe`|
|6|`results/figures/fig6_uq_probabilities.png/pdf`|Outcome probabilities under the three pre-specified measures, Wilson intervals|
|S1|`figS_historical_sensitivity.png/pdf`|Threshold, initial-ratio and energy-difference sensitivity|
|S2|`figS_safe_initial_states.png/pdf`|Fixed-policy population-floor safe slices at `a = 0, 0.2, 0.4`|
|S3|`figS_alignment_horizon.png/pdf`|Horizon sensitivity of minimum population|
|S4|`figS_uq_sensitivity.png/pdf`|Rank-based sensitivity bars for the pre-specified aggressive measure|
|S5|`figS_structural_robustness.png/pdf`|Structural robustness, pre-specified aggressive library|
|S6|`figS_uq_stress_augmented.png/pdf`|Exploratory stress-augmented outcome probabilities (post-hoc)|
|S7|`figS_structural_robustness_stress_augmented.png/pdf`|Structural robustness, exploratory stress-augmented library|
|S8|`figS_controlled_stress.png/pdf`|Controlled 2x2 human-demography x AI-pressure factorial|

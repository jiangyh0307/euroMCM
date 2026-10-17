# ARCHIVED v2 Part IV — superseded by docs/results.md and docs/p0_acceptance.md

Historical snapshot only. Its pre-specified labels do not establish preregistration.

# Part IV — Uncertainty quantification and robustness

## Design

Three **pre-specified** measures are sampled independently with a fixed seed:

- Conservative: low RSI expansion pressure, higher energy supply, slower automation.
- Central: intermediate ranges.
- Aggressive: broad high-pressure ranges.

A fourth measure, `stress_augmented`, is an explicitly **post-hoc exploratory stress measure**. It was constructed after exploratory runs to exercise the extinction boundary, is not pre-registered, and is not a forecast. It is reported separately and excluded from the primary measurement ranking.

Each draw is simulated over 11 alignment values. Outcomes are coded as extinction, marginal, non-marginal, or failed. Wilson intervals are pointwise iid sampling-error intervals; they exclude structural uncertainty and scenario-prior error.

## Results (N = 100)

### Pre-specified measures

|Measure|`a=0` extinction|`a=0.5` extinction|`a=1` non-marginal|
|---|---:|---:|---:|
|Conservative|0.00|0.00|0.00|
|Central|0.00|0.00|0.02|
|Aggressive|0.02 [0.006, 0.070]|0.00 [0.00, 0.037]|0.04 [0.016, 0.098]|

The pre-specified measures are dominated by marginal survival. The broad aggressive measure has a small extinction frequency at `a=0` and a few non-marginal cases; it does not show the dramatic transition of the post-hoc stress measure. All runs completed; `P_ext + P_marg + P_nm = 1` in every cell.

### Exploratory stress-augmented measure (post-hoc)

|a|P(extinction)|P(marginal)|P(non-marginal)|
|---:|---:|---:|---:|
|0|0.42 [0.33, 0.52]|0.58|0.00|
|0.5|0.00 [0.00, 0.037]|1.00|0.00|
|1.0|0.00 [0.00, 0.037]|0.81|0.19 [0.13, 0.28]|

The transition is non-monotone: the non-marginal fraction is about 0.43 at `a=0.8` and 0.19 at `a=1.0`. This measure must not be presented as a pre-registered comparison or a real-world probability.

## Sensitivity

Rank-based screening uses `log10(min H)` at `a=0.5` and extinction at `a=0.0`; `H0` is excluded as an initial condition. These are associations under the sampled measures, not causal effects.

Pre-specified measures (top five): `L_service` (0.151), `beta_H` (0.135), `E_total` (0.128), `xi` (0.096), `omega` (0.088).

Exploratory stress-augmented measure (top five): `e0` (0.466), `r_H` (0.252), `E_total` (0.205), `xi` (0.203), `beta_H` (0.140).

The ranking is measure-dependent. Under the pre-specified measures, land-service availability and human demography dominate; under the post-hoc stress measure, AI energy intensity dominates. `E_total` and `xi` appear near the top in both. The candidate measurement list is conditional, not a causal or policy ranking. See `uq_priority_unknowns.txt` and `uq_priority_unknowns_stress_augmented.txt`.

The industrial-threshold timing is recorded as `q_self_crossed` and `t_q_self` in `uq_results.csv`. Because non-crossing runs are right-censored, we report crossing status separately and do not impute a time for censored runs or rank `t_q_self` as if it were fully observed.

## Structural robustness

20 sampled parameter vectors x {proportional, priority} x {saturating, non-saturating} x 6 alignments (80 pairs per alignment), run separately for the pre-specified aggressive measure and the exploratory stress-augmented measure.

Pre-specified aggressive library:

- Population-floor safe fraction: 78/80 at `a=0`, 80/80 for `a>=0.2`.
- Robust population-floor set: `{0.2, 0.4, 0.6, 0.8, 1.0}`.
- Non-marginal safe fraction: 0 at `a<=0.6`, 2/80 at `a=0.8`, 4/80 at `a=1.0`.
- Robust non-marginal set: empty.

Exploratory stress-augmented library:

- Population-floor safe fraction: 60/80 at `a=0`, 66/80 at `a=0.2`, 74/80 at `a=0.4`, 80/80 for `a>=0.6`.
- Robust population-floor set: `{0.6, 0.8, 1.0}`.
- Non-marginal safe fraction: 6/80 at `a<=0.6`, 18/80 at `a=0.8`, 16/80 at `a=1.0`.
- Robust non-marginal set: empty.

The stress-augmented `0.6` transition coincides with the analytic `a_safe=0.6`; the pre-specified aggressive library is safe at lower alignments because population-floor failures are rarer. Both are empirical over the tested library, not continuous-domain guarantees.

## Figures and tables

- `results/figures/fig6_uq_probabilities.png/pdf` (pre-specified measures)
- `results/figures/figS_uq_stress_augmented.png/pdf` (exploratory)
- `results/figures/figS_uq_sensitivity.png/pdf`
- `results/figures/figS_structural_robustness.png/pdf`
- `results/figures/figS_structural_robustness_stress_augmented.png/pdf`
- `results/figures/figS_controlled_stress.png/pdf` (Part II/IV factorial)
- `results/tables/uq_probabilities.csv`
- `results/tables/uq_probabilities_stress_augmented.csv`
- `results/tables/uq_sensitivity.csv`
- `results/tables/uq_priority_unknowns.txt`
- `results/tables/uq_priority_unknowns_stress_augmented.txt`
- `results/tables/structural_robustness_summary.csv`
- `results/tables/structural_robustness_summary_stress_augmented.csv`

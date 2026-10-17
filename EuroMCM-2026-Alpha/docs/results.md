# Results: P0 selective-verification handoff

**Part V policy results:** legacy (`H_ext=1e6`) in
[`part_v_results.md`](part_v_results.md); current risk-revised (`H_ext=1e8`,
rapid/cumulative collapse, recovery flags) in
[`part_v_risk_results.md`](part_v_risk_results.md). This file remains the
P0/Part I–IV results record.

## New runs (current implementation)

|Experiment|Actual output|Finding|
|---|---|---|
|Individual demographic bound, 400 stored vectors|`p0_sample_bound_audit.csv`, `p0_sample_bound_summary.csv`|No contradictions; bound excludes year-100 extinction for 45 conservative, 33 central, 0 aggressive, 0 later-stress vectors|
|26 targeted cases, four comparisons per case|`p0_numerical_audit.csv`, `p0_acceptance_numerics.json`|Adaptive refinement passed 26/26; RK4 1/0.5/0.25 yr saved-trajectory checks passed 5/8/23 of 26; 104/104 classes agreed|
|12 stratified random vectors, three alignments|`p0_spotcheck_selection.json`, `p0_spotcheck_results.csv`, `p0_spotcheck_summary.json`|36 completed, zero failures, zero legacy class changes|
|RSI-only controlled pilot + paired no-AI counterfactual|`p0_controlled_*`, `p0_no_ai_counterfactual.csv`, `p0_paired_rsi_*.csv`|96 vectors; 480 AI-present + 96 no-AI solves; zero failures|

All table paths are under `results/tables/`. Audit JSONs retain the initial RK4
failures; they are not deleted or reclassified as passes. Saved-trajectory errors
include interpolation between output points, not only integration error.

The adaptive refinement maximum errors across targeted cases were approximately:
relative H 2.33e-5, A normalized by site capacity 6.10e-6, relative q 3.08e-6,
final-window bad-fraction 2.52e-6. Reference solver: DOP853, rtol=1e-10,
atol=1e-12, max_step=0.125 yr. Comparison solver max_step=0.25 yr, rtol=1e-8.
These are observed errors for a finite test set, not mathematical global error bounds.

## Strictly controlled RSI-only result

Fixed across every range and alignment: beta_H=0.02, delta_H=0.01, H0=H_ref=8e9,
H_ext=1e6, H_min=1e8, s_min=0.8, E_total=3e10 MWh/yr, L_service=2e6 km²,
L_site=100 km², rho=0.1, T=100 yr, final window=10 yr, and all initial states.
Only eta, xi, omega, q_c, M_max, c_A, w_A0 and e0 vary.

N=32 vectors per range, seed=20261017, paired across a. This is an exploratory
repair pilot; its interval estimates do not include scenario-design uncertainty.

|Range|a=0|a=0.4|a=0.6|a=0.8|a=1|
|---|---:|---:|---:|---:|---:|
|conservative non-marginal count|32/32|32/32|32/32|32/32|32/32|
|central non-marginal count|32/32|32/32|32/32|32/32|32/32|
|aggressive non-marginal count|28/32|28/32|28/32|31/32|32/32|

All remaining cases were marginal; none extinct. Figure:
`results/figures/p0_controlled_rsi.png` and `.pdf`.
The baseline demographic bound already excludes extinction within this horizon:
H0 exp(-delta_H T)=2.943e9 >1e6. This proof concerns the fixed-demography pilot;
it must not be applied to every old sampled vector.

### Paired no-AI comparison

For each of the same 96 sampled RSI vectors, the no-AI counterfactual uses `A0=0`
and `rho=0`, retains human demographics, energy supply and land partition, and is
compared against the AI-present run at five alignments. The precommitted facility
site is not reassigned to human service. The no-AI runs are non-marginal in all 96
draws. In the aggressive range, at `a=0` the AI-present case lowers mean final human
population by 1.36% and final `s_H` by 0.023; the bad-time fraction rises by 0.098
(about 0.98 years of the 10-year final window), and 4/32 outcomes change from
non-marginal to marginal. At `a=0.8`, 1/32 changes class; at `a=1`, the paired
difference is numerically negligible. Conservative/central effects are small.

`min_H` is not informative in this pilot: every trajectory's minimum equals its
initial `H0`. This pairing estimates the effect of the implemented AI-sector bundle
within the chosen range, including its construction reservation; it is not a
real-world causal estimate.

## Earlier exploratory results (retained, selectively checked)

The old files and six main figures are retained for reproducibility. They are
exploratory baseline artifacts, not all independently tolerance-certified:

- Historical demonstration: T_rep=2867.46 yr; European compatibility 14/650 grid
  points; regional compatibility 30/650; 325 right-censored, no recorded errors.
  H0 and H1 both have compatible points. The means 2700/2500 kcal/person/day are
  assumptions. The compatibility fraction is grid/design dependent.
- Earlier broad-range UQ, N=100/range: conservative all marginal; central 98%
  marginal, 2% non-marginal; aggressive a=0 had 2% extinction, 95% marginal, 3%
  non-marginal. At a=1 it had 0%, 96%, 4%, respectively.
- Later outcome-informed stress range: a=0 had 42% extinction; a=1 had 19%
  non-marginal. This range was selected after inspecting outcomes. No range was
  preregistered; the 42% number is not a forecast or a confirmation result.
- Earlier joint stress scenario: effective extinction about year 68.86 at a=0.
  It changes human rates, initial population and other assumptions. The older
  2x2 experiment also changes supply and thresholds: it is a **bundle comparison**,
  not an isolated RSI or demographic causal effect. Use the new controlled pilot
  for fixed-background comparisons.
- Population certificate: a_safe=0.6 in the joint-stress scenario. The earlier
  a-grid first passed its population floor at a=0.4 (resolution 0.1). The certificate
  is sufficient, not necessary, and does not certify adequacy/welfare.

Earlier ranking lists are exploratory associations with few extinction events;
they do not establish a unique measurement priority. Broad ranges previously
emphasized land service/demography; the later stress range emphasized e0. No
universal parameter ranking or value-of-information calculation is established.

## Scope of verification

The 36 checks reuse 12 independent parameter vectors across three alignments:
they are not 36 independent parameter draws. The 26 targeted cases are intentionally
biased toward difficult boundaries. Neither supports an unbiased estimate of the
error rate over all 4,400 runs. No changed class or failed random check was found,
so no neighborhood expansion was triggered. Full-library adaptive verification
was interrupted and remains incomplete by the user's selective-verification decision.

Read `docs/p0_acceptance.md` for the final handoff boundary and known limitations.

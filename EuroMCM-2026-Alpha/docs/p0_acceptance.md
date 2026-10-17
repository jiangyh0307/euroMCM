# P0 acceptance record — selective verification

## Decision

**P0 exploratory implementation and research handoff is complete under the agreed
selective-verification scope.** This does not mean every stored numerical trajectory
is precision-certified, or that the original problem's P1/P2 deliverables are complete.
Full adaptive rechecking of the 4,400-run library is **INCOMPLETE**, not a passed check.
The user explicitly replaced that requirement with targeted and stratified checking.

## Fixes delivered

- Added a regression for common competition-weight rescaling. The capped one-resource
  fixture returned near-zero satisfaction at weight scale 1e-40; normalizing the
  multiplier calculation now preserves [1,0.4] over scales 1e-80 through 1e80.
- Retained exact positive-domain utility and boundary-aware zero handling. Inactive
  AI now remains at A=0 without logging zero or falsely occupying facilities.
- Removed silent installed-hardware clipping and per-step ceiling projection. Meaningful
  ceiling violations raise an error. Zero human land demand no longer divides by zero.
- RSI default is adaptive DOP853. Extinction uses a root event; final-window bad duration
  uses population/adequacy event intervals. Exact horizon/window endpoints are included.
- Resource adequacy and population equality comparisons use an explicitly documented
  1e-10 tolerance. This prevents floating-point equality from being counted as deprivation.
- Failed runs stay visible; an incomplete structural library cannot be declared robustly safe.
- Reclassified selected historical all-age energy means as ASSUMPTION, not ESTIMATE.
- Replaced preregistration/pre-specified implications with an accurate exploratory history.

## Executed evidence

|Check|Result|Artifact under `results/tables/`|
|---|---|---|
|Mathematical/physical/regression suite|77 passed (58 P0 + 11 Part V policy/shutdown + 8 risk); see current machine-readable report|`p0_tests.xml`|
|Demographic bound on each stored vector|400 checked; no event-bound contradictions|`p0_sample_bound_audit.csv`|
|Targeted adaptive refinement|26/26 pass; same class in all 104 solver comparisons|`p0_numerical_audit.csv`|
|Old RK4 trajectory accuracy|1 yr:5/26, 0.5 yr:8/26, 0.25 yr:23/26 pass|same CSV; failures retained|
|Stratified random checking|12 vectors x3 alignments, 36 complete, 0 failures/changes|`p0_spotcheck_results.csv`|
|Fixed-background RSI pilot|96 vectors, 480 AI-present + 96 no-AI paired solves, 0 failures|`p0_controlled_results.csv`, `p0_no_ai_counterfactual.csv`|
|Paired AI vs no-AI diagnostic|480 same-vector/Alignment comparisons|`p0_paired_rsi_effects.csv`, `p0_paired_rsi_summary.csv`|

The adaptive audit uses a tighter rtol=1e-10, atol=1e-12, max_step=0.125 reference
against rtol=1e-8, atol=1e-10, max_step=0.25. Largest observed H trajectory discrepancy
was 2.33e-5 relative; A discrepancy was 6.10e-6 of site capacity; q discrepancy 3.08e-6
relative. Errors include output interpolation. These observations are not global bounds.

The stratified sample selection was fixed with seed 20261018 before checking its
outcomes. It samples three vectors per old range, paired at a=0,0.5,1. Alignment runs
are dependent, so this is not 36 independent parameter draws. No sampled mismatch
triggered the declared neighborhood-expansion rule. The targeted set is deliberately
biased toward boundaries; do not estimate the full library error rate from it.

## Controlled design and interpretation

`configs/p0_acceptance.yaml` freezes all demographic, supply, initial-state and
classification parameters. Only eta, xi, omega, q_c, M_max, c_A, w_A0 and e0 vary.
Every effective parameter is exported and fixed-column invariance checked in code.
The AI-present arm has 96 vectors x five alignments; each vector is paired with a
no-AI arm using A0=0 and rho=0, the same human and resource background, and the same
fixed land partition. The no-AI arm does not reserve construction electricity; it
does not reallocate the reserved site to human services.

All 96 no-AI draws are non-marginal. Under AI, conservative and central draws remain
non-marginal; aggressive draws are non-marginal 28/32 at a=0,0.4,0.6, 31/32 at a=0.8,
and 32/32 at a=1. At a=0, AI lowers mean final H by 1.36% and final s_H by 0.023 for
the aggressive range; final-window bad fraction rises by 0.098 (about 0.98 years in
the 10-year window), and 4/32 draws change from non-marginal to marginal. At a=1 the
paired effect is approximately zero. Minimum H equals H0 in this pilot and is not an
informative paired effect metric. No extinction occurs.

These are conditional effects of the model's AI-present bundle. Since the no-AI arm
sets rho=0 (no construction budget) while the AI arm can reserve construction energy,
the difference includes that energy reservation as part of the AI sector. It is not a
real-world causal effect.

For the fixed pilot, H(t)>=H0 exp(-delta_H t) excludes year-100 extinction analytically.
For the old UQ, use individual parameters: the same theorem excludes extinction in
45 conservative and 33 central vectors, not all of those ranges. There are zero
contradictions with recorded events; lack of a certificate does not imply extinction.
The population-law decision, threshold formula, old/new experiment comparison and
Part V reference settings are recorded in `docs/population_protocol.md`.

## What is and is not accepted

Accepted: shared allocator and physical accounting; conditional mathematical
propositions; runnable exploratory experiments; current selective verification
record; reproducible parameter/configuration/export pipeline; English technical draft.

Retained with qualification: earlier T_rep demonstration and grid slice, old UQ
frequencies, phase diagrams and finite-grid robustness. Classes agree in checked
cases, but some old coarse saved trajectories fail precision criteria. Keep these
as exploratory artifacts and refine individual policy/threshold claims before use.

Not claimed: preregistered confirmation, causal historical validation, realistic RSI
calibration, objective extinction probabilities, a global numerical error bound,
full-library verification, a unique safe alignment, or a computed control viability kernel.

Not executed: LaTeX compilation (no engine), full Part V uncertainty distribution,
monetary-cost conversion and global optimal control. A small fallible-shutdown branch
grid and an 8-vector uncertainty pilot are executed, with assumed `p_s`/ranges.
P1/P2 still include better calibration, spatial/industrial refinements, final paper,
summary sheet, ENOCH letter, reference verification and AI-use report.

## Reproduce without the interrupted full rerun

```bash
export PYTHONPATH=src
python3 -m pytest -q tests --junitxml=results/tables/p0_tests.xml
python3 experiments/export_parameters.py
python3 experiments/run_acceptance.py --section bounds
python3 experiments/run_acceptance.py --section controlled
python3 experiments/run_acceptance.py --section numerics
python3 experiments/run_spotcheck.py
python3 experiments/finalize_handoff.py
```

The old long recheck script now checkpoints completed vectors, records elapsed time,
has a per-case 60-second budget, and defaults to eight vectors. It is optional;
it is not part of this accepted selective-verification scope.

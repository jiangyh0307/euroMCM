# EuroMCM 2026 α — Our Turn

## Current status: P0 research handoff, selectively verified

The unified model, Parts I–IV Python implementation, figures and English draft
are available. P0 reliability repairs use targeted convergence checks and
stratified spot checks, **not full re-integration of the 4,400-run library**.
Part V resource-protection R and new-installation cap C are implemented and
executed on a 25-run reference grid plus a separate exploratory stress slice;
fallible shutdown is specified but **not executed**.
The acceptance record is [`docs/p0_acceptance.md`](docs/p0_acceptance.md).

Current regression suite: **77 passed** (58 P0 + 11 Part V policy/shutdown + 8 risk). Machine-readable status, artifact hashes
and verification limits: `results/tables/p0_handoff_manifest.json`.

Question: under what resource-allocation, physical and dynamical conditions can
humanity avoid extinction and marginalization alongside hypothetical RSI?

Authoritative problem: `../2026_Problem_Alpha.pdf`. The historical and future
main models use the same weighted proportional-fair resource allocator. Alignment
adds a human satisfaction floor. Installed hardware and capability are separate;
construction energy, operations, manufacturing and facility footprint are accounted
for separately. Proofs and units: [`docs/mathematical_model.md`](docs/mathematical_model.md).

## Start here

**Part V resource protection R and new-installation cap C are implemented and
executed** on the reference grid and on legacy/risk-revised pressure slices. Read
[`docs/part_v_mathematics.md`](docs/part_v_mathematics.md) for the English theory,
[`docs/part_v_risk_results.md`](docs/part_v_risk_results.md) for the current
risk-revised results, and [`docs/part_v_handoff_zh.md`](docs/part_v_handoff_zh.md)
for the handoff. Fallible shutdown is implemented and executed as separate
success/failure branches with assumed success probabilities. The population ODE is unchanged.

1. [`docs/p0_acceptance.md`](docs/p0_acceptance.md): current findings, passed checks and limits.
2. [`docs/results.md`](docs/results.md): actual numerical results and artifact paths.
3. [`docs/population_protocol.md`](docs/population_protocol.md): population law, lower bound and Part V reference.
4. [`docs/part_v_results.md`](docs/part_v_results.md): legacy Part V policy results (`H_ext=1e6`).
5. [`docs/part_v_risk_results.md`](docs/part_v_risk_results.md): risk-revised Part V results.
6. [`docs/part_vi_results.md`](docs/part_vi_results.md): Part VI robustness and conditional policy synthesis.
7. [`docs/HANDOFF_zh.md`](docs/HANDOFF_zh.md): Chinese handoff.
8. [`paper/draft_parts_i_iv.tex`](paper/draft_parts_i_iv.tex): current English Parts I–IV draft.

The earlier v2 README/results/paper are retained under `docs/archive/` and
`paper/archive/` as historical records, not current acceptance claims.

## Installation and reproducibility

Tested with Python 3.9.6; Python 3.11+ recommended.

```bash
python3 -m pip install -r requirements.txt
export PYTHONPATH=src
python3 -m pytest -q tests
./run_all.sh
```

`run_all.sh` runs the **selective P0 checks**, not the full old Monte Carlo again:

```bash
python3 experiments/export_parameters.py
python3 experiments/run_acceptance.py --section bounds
python3 experiments/run_acceptance.py --section controlled
python3 experiments/run_acceptance.py --section numerics
python3 experiments/run_spotcheck.py
python3 experiments/run_part_v.py
python3 experiments/run_part_v_risk.py
python3 experiments/run_part_v_ponr.py --step 1
python3 experiments/run_part_v_ponr_refine.py
python3 experiments/run_part_v_shutdown.py
python3 experiments/run_part_v_uncertainty.py
python3 experiments/run_part_vi_robustness.py
python3 experiments/finalize_handoff.py
```

Legacy Part V also has a separate exploratory pressure slice (`H_ext=1e6`), not
part of the current risk-revised comparison:

```bash
python3 experiments/run_part_v_stress.py
```

The controlled pilot uses 32 parameter vectors per broad exploratory range and five
alignments (480 AI-present runs), plus 96 paired no-AI counterfactual runs; human
demography, initial states, thresholds and resource supplies are fixed. In the
aggressive range at a=0, AI lowers mean final H by 1.36%, lowers final satisfaction
by 0.023 and increases final-window bad fraction by 0.098; 4/32 draws change from
non-marginal to marginal. Minimum H remains H0 in this pilot and is uninformative.
The numerical audit uses 26 targeted cases and four comparisons
against a tighter adaptive reference. Spot checking adds 12 stratified random vectors
at three alignments (36 checks). Seeds and tolerances are saved with outputs.

Original figure commands remain available; they can overwrite earlier exploratory
outputs and can take substantially longer:

```bash
python3 experiments/run_historical.py
python3 experiments/run_rsi.py
python3 experiments/run_alignment.py
python3 experiments/run_uq.py --n 100 --seed 2026 --dt 1.0
```

RSI now defaults to adaptive DOP853 with extinction/adequacy threshold events,
not the old projected one-year RK4 integration. Use `integrator="rk4"` explicitly
only for comparisons. `dt_internal` controls RK4; `max_step`, `rtol`, `atol` control
the adaptive integrator. The current classification equality tolerance is 1e-10.

## What the new checks found

- A common-weight unit scaling bug in capped water filling was fixed. Multiplying
  all weights by 1e-80 through 1e80 now preserves the allocation in the regression fixture.
- Adaptive refinement passed **26/26 targeted cases**. The old RK4 saved trajectories
  passed the configured error tests in only 5/26 cases at one-year steps, 8/26 at
  half-year steps and 23/26 at quarter-year steps. All 104 comparisons retained their
  outcome class, but this is not enough to certify all old trajectories.
- Stratified spot checks: **36/36 completed, no legacy outcome-class changes**,
  no projection and no material physical-constraint violations.
- The stored 400 parameter vectors were checked individually against their own
  demographic extinction bound: no contradictions. The bound rules out extinction
  by year 100 for 45/100 conservative and 33/100 central vectors, not all of them.
- In the strictly controlled RSI-only pilot, no extinction occurred. Conservative
  and central ranges were non-marginal for all pilot draws; aggressive non-marginal
  frequencies were 28/32 at a=0,0.4,0.6; 31/32 at a=0.8; 32/32 at a=1.
  These are conditional pilot frequencies, not reality probabilities.
- Population law and Part V reference settings: [`docs/population_protocol.md`](docs/population_protocol.md).

## Part V policy experiments

Implemented and executed: resource-protection R and new-installation cap C, using
the same allocator and population law. The reference 25-run grid (1 no policy +
12 R + 12 C) is entirely non-marginal and shows no human-outcome improvement from
the tested policies; R can displace AI operations at a land bottleneck with only
a tiny human adequacy gain. A separate exploratory joint-stress slice shows that
early R/C can prevent extinction while many paths remain marginal, and that the
response is non-monotone in strength and timing. No global optimal policy is claimed.

Legacy results with `H_ext=1e6` remain in [`docs/part_v_results.md`](docs/part_v_results.md).
The current risk-revised results use `H_ext=1e8`, `H_min=2e8`, rapid collapse
(10-year 50% loss with a size floor), cumulative 90% loss, and explicit
first-passage/recovery flags. They are in
[`docs/part_v_risk_results.md`](docs/part_v_risk_results.md). In the revised stress
background (`H0=1e9`), no intervention reaches effective extinction at 43 years;
early R/C avoid it but remain marginal, and four late-policy cases cross then recover.
Point-of-no-return scan (R u=0.8, C/A_max=0.1): sampled preventive deadlines
about 42.75 and 42.50 years; recovery deadlines about 57.25 and 65.75 years,
giving sampled windows of about 14.5 and 23.25 years. These are finite-grid
policy results, not general monotonicity or irreversible-extinction theorems.

Fallible shutdown is now implemented and executed as separate success/failure
branches with assumed success probabilities. A small 8-vector RSI uncertainty
ensemble is also executed. Part VI repeats the two-deadline scan on four
pre-specified parameter sets: preventive deadlines are roughly 35–43 years,
recovery deadlines are later, with R windows about 14.5–15.5 years and C windows
about 23–25 years. See [`docs/part_vi_results.md`](docs/part_vi_results.md).
Monetary cost conversion and global optimal control remain **NOT EXECUTED**.
No real-world probability is claimed.

## Earlier results and provenance

The stored historical demonstration gives approximately 2,867 years, and 14/650
grid points are European-duration compatible; this is a scenario slice, not causal
validation or full empirical calibration. H0/H1 are not identified by it.

Old broad aggressive sampling gave 2/100 extinction outcomes at a=0; the later
outcome-informed narrow range gave 42/100. **All ranges are exploratory, none was
preregistered.** Changing labels cannot turn an exploratory result into confirmation.
The old UQ also changes human demography, initial population and supply, and must not
be described as measuring the isolated effect of RSI.

Parameter records: `src/alpha/parameters.py`, `results/tables/parameter_table.csv`.
Historical selected population energy means 2700/2500 kcal/day are **ASSUMPTION**,
because no age/sex aggregation was supplied. Problem-reported adult ranges and
differences are SOURCE (as reported by the problem). Future technology values are
scenario assumptions. IEA data-centre totals do not directly measure RSI demand.
Read [`docs/assumptions.md`](docs/assumptions.md) and [`docs/limitations.md`](docs/limitations.md).

## Project organization

|Location|Purpose|
|---|---|
|`src/alpha/allocation.py`|Shared allocator, bounds and boundary cases|
|`src/alpha/historical.py`|Historical dynamics and censoring|
|`src/alpha/rsi.py`|Hardware/capability/human dynamics and resource accounting|
|`src/alpha/alignment.py`, `viability.py`|Safety maps and conditional certificate|
|`src/alpha/uncertainty.py`, `scenarios.py`|Exploratory sampling and uncertainty|
|`configs/p0_acceptance.yaml`|Repair protocol, controlled design and tolerances|
|`experiments/`|Runnable experiments and selective verification|
|`results/figures/`, `results/tables/`|Generated artifacts; current audits use `p0_` prefix|
|`tests/`|Mathematical, physical and numerical regressions|
|`docs/`, `paper/`|Current derivations, results, English draft and archives|

## Handoff and remaining work

P0 delivers a runnable exploratory research model and a documented selective
verification record. It does not deliver a global numerical certificate. Recheck
specific policy or threshold conclusions at finer tolerances before adopting them.
Fixed-policy safe grids are not a control viability kernel; population-floor
certificates do not guarantee non-marginal welfare.

P1: original literature/data calibration, spatial migration, better industrial/power
and idle-hardware models, Part V uncertainty/fallible-shutdown extensions, robust
control and value of information. The minimal Part V R/C comparison is already executed. P2: final paper, Summary Sheet, ENOCH letter,
verified references, AI-use report and typesetting. LaTeX compilation is **NOT
EXECUTED** (no engine installed); compile from `paper/` when an engine is available.

The full-library adaptive verification was interrupted and is **INCOMPLETE**. Per
the user's scope decision, it is not required for this selective P0 handoff. Its
script is checkpointed and defaults to a short batch; it is not run by `run_all.sh`.

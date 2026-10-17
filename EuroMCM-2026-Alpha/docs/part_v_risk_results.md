# Part V risk-revised results

**Status: implemented and executed. The population ODE is unchanged; only the risk
adjudication changed.** The old results using `H_ext=1e6` are retained as legacy
(`docs/part_v_results.md`) and are not relabeled.

Thresholds and the executable pressure scenario are recorded in
`configs/part_v_risk.yaml` and `src/alpha/risk.py`. Part VI robustness synthesis:
[`part_vi_results.md`](part_vi_results.md).

## 1. Risk hierarchy

Let `H(t)` be the full-horizon population trajectory and `H0` its initial value.
All thresholds below are **scenario conventions**, not empirical estimates.

|Outcome|Definition|Interpretation|
|---|---|---|
|**Effective extinction**|`min_t H(t) <= H_ext = 1e8`|first passage below the absolute floor; not biological zero|
|**Rapid collapse**|no extinction, and exists `t` with `H(t+Delta) <= (1-q)H(t)` and `H(t+Delta) <= H_min`|large short-window loss while already below the minimum acceptable population|
|**Cumulative collapse**|no above, and `H(T) <= (1-q_total)H0`|large cumulative relative loss|
|**Marginal survival**|no catastrophe, but final-window `H<H_min` or `s_H<s_min`|resource-defined marginalization|
|**Non-marginal survival**|no catastrophe and adequate final window|reference success category|

The precedence is extinction > rapid collapse > cumulative collapse > marginal >
non-marginal, so the categories are mutually exclusive and exhaustive for successful
runs. Parameters:

\[
H_{ext}=10^8,\quad H_{min}=2\times10^8,\quad \Delta=10\text{ yr},\quad
q=0.5,\quad q_{total}=0.9,\quad W=10\text{ yr},\quad s_{min}=0.8.
\]

`Rapid contraction` is also recorded as a diagnostic (same loss condition without
the `H<=H_min` size floor). It is not a catastrophe category by itself, so a drop
from 8 billion to 4 billion is not called a collapse unless it also falls below
`H_min`; this avoids treating all large proportional swings as civilizational collapse.

### First passage is not irreversible extinction

A trajectory may cross below `H_ext` and later recover. The assessment records:

- `extinction`: first-passage flag;
- `terminal_extinction`: `H(T) <= H_ext`;
- `recovered_after_extinction`: first passage occurred but `H(T) > H_ext`.

Thus a path can carry the **effective-extinction event flag** while still having a
recovered final population. This is a first-passage classification, not a claim of
irreversible biological extinction. Point-of-no-return claims require an explicit
policy-recovery analysis, not just the first crossing.

## 2. Why the pressure background had to change

With `H_ext=1e8`, the old pressure background `H0=1e8` would satisfy
`H0=H_ext` at `t=0`, producing an immediate false extinction. The revised pressure
background is:

\[
H_0=10^9,\quad \beta_H=0.20,\quad \delta_H=0.12,\quad H_{ext}=10^8,\quad H_{min}=2\times10^8.
\]

The reference background remains `H0=8e9`, `beta_H=0.02`, `delta_H=0.01`, and the
new thresholds. The reference lower bound at 100 years is

\[
8\times10^9e^{-0.01\times100}=2.943\times10^9>H_{ext},
\]

so **effective extinction is still excluded** in the reference background. The
maximum 10-year loss there is at most `1-e^{-0.1}=9.5%`, and the maximum 100-year
loss is at most `1-e^{-1}=63.2%`; therefore neither rapid (50%) nor cumulative
(90%) collapse is possible under those rates. This is a property of the ODE and
parameters, not a numerical failure.

The pressure background has `delta_H=0.12`; its 10-year zero-resource loss can
reach `1-e^{-1.2}=69.9%`, so rapid/cumulative events are possible. The old
`scenario_stress()` with `H0=1e8` and `H_ext=1e6` remains a legacy scenario only.

## 3. Executed grids

Both grids use the same policies as the earlier Part V work:

- no intervention;
- `R`: `tau in {0,25,50,75}`, `u_bar in {0.5,0.8,1.0}`;
- `C`: `tau in {0,25,50,75}`, `C/A_max in {0.1,0.5,1.0}`.

The reference grid has 25 runs; the stress grid has another 25. All use full-horizon
integration (`terminate_on_extinction=False`) so first-passage flags and later
recovery/cost metrics are both retained. No runs failed.

### Reference background

All 25 runs are **non-marginal**, with no effective extinction, rapid collapse,
cumulative collapse, or recovery event. The no-intervention final H is about
`2.160588e10` and final `s_H` about `0.925632`. Policies do not change the human
outcome in this background. `R u=1.0` displaces AI operating energy at the land
bottleneck (about `6.06e9 MWh` over the horizon) while changing final human
adequacy by only about `4e-5`; `C` reduces new installation but does not change the
non-marginal human outcome.

### Pressure background

No intervention reaches effective extinction at **43.0 years** (`H_ext=1e8`), with
final H about `1.17e5` at the 100-year horizon. The paired no-AI counterfactual is
**marginal but not extinct**: H grows to about `1.67e10`, final `s_H≈0.6015`. Thus
RSI changes the survival outcome in this background, but the background itself is
already resource-marginal; this is not a claim that baseline humanity would
otherwise go extinct.

Selected actual outcomes:

|Policy|tau|strength|outcome|extinction time|final H|final s_H|recovered?|
|---|---:|---:|---|---:|---:|---:|---|
|none|—|—|extinction|43.0|1.17e5|0.00995|no|
|R|0|0.5|marginal|—|4.86e8|0.500|no|
|R|0|0.8|marginal|—|1.20e10|0.600|no|
|R|0|1.0|marginal|—|1.67e10|0.600|no|
|C|0|0.1|marginal|—|1.35e10|0.600|no|
|C|0|0.5|marginal|—|7.42e9|0.600|no|
|R|25|0.8|marginal|—|1.15e10|0.626|no|
|R|50|0.8|extinction|43.0|3.16e8|0.800|**yes**|
|R|50|1.0|extinction|43.0|2.33e9|1.000|**yes**|
|C|50|0.1|extinction|43.0|2.26e9|1.000|**yes**|
|C|50|0.5|extinction|43.0|2.26e9|1.000|**yes**|
|R|75|0.5|extinction|43.0|1.36e6|0.500|no|
|C|75|0.1|extinction|43.0|1.62e7|1.000|no|

Grid totals: 15 effective-extinction outcomes (11 terminal, 4 recovered), 10
marginal outcomes, no non-marginal outcome, 0 rapid/cumulative-only outcomes.
Rapid-collapse and cumulative-collapse flags co-occur with some of the extinction
paths; priority reporting keeps the more severe effective-extinction label. The
flags are retained in the CSV.

The four recovered cases are important: `tau=50` R/C policies cross below `H_ext`
at 43 years, before activation, and recover later; they must not be described as
irreversible extinction. Early policies at `tau=0/25` avoid the first-passage event
but remain marginal. Late policies at `tau=75` do not recover in this grid.

## 4. Paired AI effect

`D_AI(t)=1-H_AI(t)/H_NoAI(t)` is recorded as a diagnostic, not a classification.
In the pressure no-intervention case it is about `0.99999` at the final horizon.
For early R `u=0.8` it is about `0.28`, for `C=0.1` about `0.19`, and for `R u=1.0`
it is essentially zero at the final horizon. These are model contrasts within the
same background and must not be interpreted as real-world causal effects.

## 5. Files and scope

- `configs/part_v_risk.yaml` — thresholds and backgrounds.
- `src/alpha/risk.py` — risk hierarchy and paired-damage helper.
- `src/alpha/scenarios.py::scenario_collapse_stress` — revised pressure background.
- `experiments/run_part_v_risk.py` — 25 + 25 risk-revised policy runs.
- `experiments/run_part_v_ponr.py`, `run_part_v_ponr_refine.py` — deadline scans.
- `experiments/run_part_v_shutdown.py` — fallible shutdown branches.
- `experiments/run_part_v_uncertainty.py` — 8-vector RSI uncertainty pilot.
- `results/tables/part_v_risk_main_experiments.csv`,
  `part_v_risk_stress_experiments.csv`, summaries and manifest.
- `results/tables/part_v_ponr_*`, `part_v_shutdown_*`, `part_v_uncertainty_*`.
- Tests: 77 passed (58 P0 + 11 Part V policy/shutdown + 8 risk).

**Not executed:** full Part V uncertainty distribution, monetary-cost conversion,
and global optimal control. Shutdown and the small uncertainty pilot are executed,
but `p_success` and the sampled ranges are scenario assumptions, not empirical
estimates. No unique optimal policy or real-world probability is claimed.
The thresholds `H_ext`, `H_min`, `Delta`, `q`, `q_total` are policy conventions and
require sensitivity analysis before any final paper conclusion.

## 6. Point of No Return: preventive vs recovery deadlines

Two different deadlines are evaluated on the fixed risk-revised stress background
(`H0=1e9`, `H_ext=1e8`, `H_min=2e8`):

\[
\tau_{prevent}^{*}=\sup\{\tau:\min_{0\le t\le T}H^\tau(t)>H_{ext}\},
\]

\[
\tau_{recover}^{*}=\sup\{\tau:H^\tau(T)>H_{ext}\}.
\]

The first is the latest sampled start that avoids any first passage. The second
allows an earlier crossing but requires final recovery above `H_ext`. Neither is
an irreversible-extinction theorem; both are sampled policy-class deadlines.

A 1-year scan over `tau=0..75` was run for `R u=0.8` and `C/A_max=0.1`, followed
by a 0.25-year local refinement at the observed boundaries. Actual sampled results:

|Policy|prevent last success|prevent first failure|recover last success|recover first failure|sampled window|
|---|---:|---:|---:|---:|---:|
|R u=0.8|42.75|43.00|57.25|57.50|14.50 years|
|C/A_max=0.1|42.50|42.75|65.75|66.00|23.25 years|

The success sets are contiguous over the full 1-year grid and over the refined
local ranges. This is an empirical property of the tested grid and policy class,
not a general monotonicity theorem. The boundary resolution is 0.25 years; report
the intervals rather than a unique exact point.

The window is real in the model in the following sense: after the last sampled
preventive start, the no-crossing goal is no longer achieved by the tested policy,
but a later start can still return the final population above `H_ext`. For example,
R `tau=50` starts after the no-intervention crossing at year 43, then recovers to
about `2.33e9` by year 100, flagged `recovered_after_extinction=True`. This is not
a claim that social or institutional recovery occurred, nor that a later shock
cannot cause another collapse.

Figures: `part_v_ponr_R_u0.8.png/pdf`, `part_v_ponr_C_c0.1.png/pdf`.
Tables: `part_v_ponr_scan.csv`, `part_v_ponr_summary.csv`,
`part_v_ponr_refinement.csv`, `part_v_ponr_manifest.json`.

## 7. Fallible shutdown

The shutdown extension uses installed stock `A` and operating availability
`O=vA`, with `v=1-kZ 1[t>=tau]`. The implementation uses a deterministic
success branch `v=1-k` for `t>=tau`; failure is the no-intervention branch.
Installed `A` and facility land do not jump at activation; the successful branch
reduces operating demands, R&D and autonomous production, while `A` continues to
depreciate/decommission. The policy is not a monetary-cost calculation and does
not estimate `p_success`.

With full shutdown `k=1`, actual branch results on the risk-revised stress
background:

|tau|success branch|failure branch|P_ext for p_s=0.5|P_recovered for p_s=0.5|
|---:|---|---|---:|---:|
|0|marginal, no crossing|extinction at 43|0.5|0|
|25|marginal, no crossing|extinction at 43|0.5|0|
|50|crosses at 43, recovers|extinction at 43|1.0|0.5|
|75|crosses, no recovery|extinction at 43|1.0|0|

For `p_s=0.9` the mixture extinction probability at early starts is `0.1`; at
late starts the first passage has already occurred, so `P_ext=1` even when the
success branch recovers. `p_s` is an assumed scenario parameter, not an empirical
estimate. The exact branch mixture is reported; a mean availability
`1-k p_s` is not used as a substitute. Files: `part_v_shutdown_branches.csv`,
`part_v_shutdown_mixture.csv`, `part_v_shutdown.png/pdf`, `part_v_shutdown_manifest.json`.

## 8. Small Part V uncertainty ensemble

Eight vectors sampled from the exploratory `stress_augmented` range vary only
`eta, xi, omega, q_c, M_max, c_A, w_A0, e0`; all human, resource, threshold and
initial-condition fields are fixed at the risk-revised stress background. Seven
policies were run (none, R at tau=0/25/50 with u=0.8, C at tau=0/25/50 with
C/A_max=0.1):

|Policy|P_extinction|P_recovered|mean final H|mean final s_H|
|---|---:|---:|---:|---:|
|none|0.50|0|2.13e9|0.318|
|R tau=0|0.00|0|1.20e10|0.600|
|R tau=25|0.00|0|1.17e10|0.614|
|R tau=50|0.50|0.50|5.74e9|0.726|
|C tau=0|0.00|0|1.36e10|0.600|
|C tau=25|0.00|0|1.35e10|0.602|
|C tau=50|0.50|0.50|7.81e9|0.811|

This is a small exploratory ensemble (`n=8`), not a real-world probability or a
preregistered prior. It shows the same qualitative distinction: early policies
avoid first passage but remain marginal; late policies can cross and later recover.
Files: `part_v_uncertainty_results.csv`, `part_v_uncertainty_summary.csv`,
`part_v_uncertainty_manifest.json`.

## 9. What remains unexecuted

- Monetary cost conversion: no sourced cost data; only physical proxies are reported.
- Global optimal control: only a finite policy grid was evaluated, not a continuous
  optimal-control solution or a global Pareto proof.
- Full Part V uncertainty: the `n=8` ensemble is a pilot, not a full distribution.
- Shutdown failure probability: `p_s` values are scenarios, not estimates; no
  empirical failure law is claimed.
- True irreversible extinction: the ODE has no finite-time zero mechanism. First
  passage, recovery and permanent-loss claims are kept distinct.

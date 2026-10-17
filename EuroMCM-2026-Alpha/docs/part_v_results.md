# Part V results — legacy policy experiments (`H_ext=1e6`)

**LEGACY:** These results use `H_ext=1e6` and the old joint-stress background.
They are retained for reproducibility. Current risk-revised results are in
[`part_v_risk_results.md`](part_v_risk_results.md). Do not mix the two thresholds.

## What was executed

Two separate deterministic policy grids were run with the implemented model:

1. **Reference-background main grid (25 runs):** `base_rsi()` with the fixed human,
   supply, threshold and initial conditions from `docs/population_protocol.md`,
   alignment `a=0`, no policy + 12 resource-protection R + 12 installation-cap C.
2. **Exploratory pressure slice (25 runs):** the same policy grid on
   `scenario_stress()`. This background is not the reference background and is not a
   forecast. It is included only to test whether the policies can act when the
   no-intervention path is already marginal/extinct.

Artifacts:

- `results/tables/part_v_main_experiments.csv` — full 25 reference runs.
- `results/tables/part_v_main_summary.csv`, `part_v_main_summary_compact.csv`
  (the compact table expresses `final_H` in billions; the full table keeps persons).
- `results/tables/part_v_stress_experiments.csv` — full 25 pressure runs.
- `results/figures/part_v_R_timing.png/pdf`, `part_v_C_timing.png/pdf`.
- `results/figures/part_v_stress_R_timing.png/pdf`, `part_v_stress_C_timing.png/pdf`.
- `results/tables/part_v_manifest.json` — settings and outputs.

All runs used adaptive DOP853 with extinction/adequacy threshold events; full-horizon
policy accounting used `terminate_on_extinction=False`, so paths continue after a
threshold event while the extinction flag is retained. There were no failed runs.

## Reference-background main grid

The no-intervention path is non-marginal: final H about `2.160588e10`, final
`s_H` about `0.925632`, final-window `p_bad=0`, and no extinction. Every R and C
run in this grid also remains non-marginal; `p_bad=0` in all 25 runs.

|Policy|tau|strength|final H|final s_H|C_install (hardware units)|C_protect (MWh)|
|---|---:|---:|---:|---:|---:|---:|
|none|—|—|2.160588e10|0.925632|0|0|
|R|0|0.5|2.160588e10|0.925632|0|0|
|R|0|0.8|2.160588e10|0.925632|0|0|
|R|0|1.0|2.160603e10|0.925668|0|6.064e9|
|C|0|0.1|2.160601e10|0.925664|1.160e6|0|
|C|0|0.5|2.160595e10|0.925650|5.069e6|0|
|C|0|1.0|2.160588e10|0.925632|0|0|

The same pattern holds at tau=25, 50 and 75. In this reference background,
human satisfaction is already above the tested R strengths except at the land
bottleneck for `u=1.0`; the protection policy then displaces a large amount of AI
operating energy while changing human final adequacy only by about `4e-5`. The
cap reduces AI installation but does not change the human outcome because the
human is not resource-marginal.

**This is a valid negative policy result:** under the reference background, neither
tested policy improves the human outcome because the baseline is already
non-marginal and the binding human constraint is not relaxed by the policy.
It does not show that the policies are ineffective in all backgrounds.

## Exploratory pressure slice

`scenario_stress()` has a no-intervention effective extinction around year 68.85.
Selected actual outcomes:

|Policy|tau|strength|outcome|min H|final H|final s_H|p_bad|D_s (yr)|
|---|---:|---:|---|---:|---:|---:|---:|---:|
|none|—|—|extinction|2.53e4|2.53e4|0.00995|1.000|83.25|
|R|0|0.5|marginal|7.48e7|7.48e7|0.500|1.000|83.25|
|R|0|0.8|marginal|1.00e8|1.02e10|0.7046|0.434|4.25|
|R|0|1.0|marginal|1.00e8|1.66e10|0.6015|1.000|38.75|
|R|25|0.8|non-marginal|1.00e8|3.55e9|0.800|0.000|8.00|
|R|25|1.0|marginal|1.00e8|1.63e10|0.6129|1.000|28.75|
|R|50|0.8|non-marginal|9.25e6|6.83e7|0.800|0.000|33.00|
|R|50|1.0|non-marginal|9.25e6|5.05e8|1.000|0.000|33.00|
|R|75|0.5|extinction|2.93e5|2.93e5|0.500|1.000|83.25|
|R|75|0.8|extinction|4.84e5|1.31e6|0.800|1.000|58.00|
|C|0|0.1|marginal|1.00e8|1.35e10|0.6011|1.000|41.25|
|C|0|0.5|marginal|1.00e8|7.42e9|0.6004|1.000|48.75|
|C|50|0.1|non-marginal|9.25e6|4.94e8|1.000|0.000|33.50|
|C|50|0.5|non-marginal|9.25e6|4.94e8|1.000|0.000|33.50|
|C|75|0.1|extinction|4.84e5|3.50e6|1.000|1.000|58.50|
|C|75|0.5|extinction|4.84e5|3.50e6|1.000|1.000|58.50|

In this stress slice, early enough R or C can prevent the extinction event, but
many resulting paths remain marginal. R `u=0.8` is non-marginal at tau=25 and 50,
while R `u=1.0` is marginal at those times; this is a genuine non-monotone
coupled response, not a numerical smoothing artifact. Late policies at tau=75 do
not prevent extinction in the tested grid. `C=1.0` is the no-restriction limit and
matches the no-intervention extinction. R `u=0.5` at tau=0/25 remains marginal.

Do not select a single "optimal" tau or strength from this slice. The slice uses a
specific joint-stress background and a finite grid; the non-monotone pattern means
a simple "earlier is always better" or "stronger is always better" rule is not
supported. Report the actual tested grid, including failures and censoring.

## Cost proxies

`C_install` is the same-state blocked new installation integral
`int (B0-B_C) dt` and is in hardware units. `C_protect` is the immediate AI
operating-allocation displaced at the same state and is in MWh; it is not a total
counterfactual system effect or a monetary cost. `E_build` is actual construction
energy in MWh. No monetary conversion is claimed.

The reference R `u=1.0` case has a large `C_protect` but a very small human
adequacy gain at the land bottleneck; this is a real Pareto concern for the policy.
The pressure slice shows that a policy can prevent extinction while still leaving
substantial final-window marginalization; population survival and resource welfare
must be reported separately.

## Interpretation limits

- The reference and pressure backgrounds are exploratory scenario settings, not
  calibrated forecasts. The reference already excludes extinction by the population
  lower bound; its policy comparison is therefore mainly a resource/adequacy and
  restriction-cost comparison.
- The pressure slice is not a real-world probability sample and must not be mixed
  with the reference 25-run grid.
- `R` is an enforced protection floor, not a measurement of institutional feasibility.
- `C` is an installed/new-construction cap, not a direct intelligence or capability cap.
- The tested grid is finite; no global optimal-control or unique critical-time claim
  follows. The non-monotone R outcomes are retained.
- Full-horizon cost metrics continue the physical ODE after an extinction threshold
  event; the extinction flag remains set. If an implementation terminates at the
  event, later cost metrics are censored and must not be compared as full-horizon.

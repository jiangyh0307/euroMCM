> Post-review update (2026-10-18): see `review_followup_zh.md` for continuous-event boundary checks and threshold/horizon/deprivation-mortality sensitivity. The original four-set tables below retain historical sampled crossing-time columns; they are not event-localization precision evidence.

# Part VI — Robustness synthesis and conditional policy recommendations

**Status: completed synthesis. No new population mechanism was introduced.** Part V
is frozen. This section uses the existing risk-revised Part V simulations plus four
pre-specified parameter sets for the two critical-time sensitivity checks.

## 1. Sensitivity of the two deadlines

Four parameter sets were fixed in `configs/part_vi_robustness.yaml` **before** the
scan. All other risk-revised stress settings were held fixed. Policies:
`R` protection with `u_bar=0.8`; `C` new-installation cap with `C/A_max=0.1`.
The grid is `tau=0..75` years, coarse 2-year scan followed by 0.5-year local
refinement. Values below are **last sampled success / first sampled failure**, not
exact continuous boundaries.

|Set|Policy|Prevent last/first fail|Recover last/first fail|Sampled window|
|---|---|---:|---:|---:|
|base stress|R|42.5 / 43.0|57.0 / 57.5|14.5 yr|
|base stress|C|42.5 / 43.0|65.5 / 66.0|23.0 yr|
|fast RSI (`eta=1`)|R|40.5 / 41.0|55.5 / 56.0|15.0 yr|
|fast RSI (`eta=1`)|C|40.5 / 41.0|64.5 / 65.0|24.0 yr|
|high AI energy (`e0=20000`)|R|38.0 / 38.5|53.5 / 54.0|15.5 yr|
|high AI energy (`e0=20000`)|C|34.5 / 35.0|59.5 / 60.0|25.0 yr|
|low energy supply (`E_total=8e9`)|R|40.0 / 40.5|55.0 / 55.5|15.0 yr|
|low energy supply (`E_total=8e9`)|C|38.5 / 39.0|62.5 / 63.0|24.0 yr|

Under this grid:

- The **recovery deadline is later than the preventive deadline in all four sets**.
  A post-prevention recovery window of roughly **14.5–15.5 years for R** and
  **23–25 years for C** appears.
- Faster RSI, higher AI energy intensity and lower energy supply move both deadlines
  **earlier**. The preventive deadline is most sensitive in the C/high-energy case
  (about 34.5–35 years versus 42.5 in the base).
- The C policy has a larger recovery window but can have an earlier preventive
  deadline when AI energy intensity is high. **No tested policy dominates on both
  deadlines.**
- No-AI counterfactuals are marginal, not extinct, in all four sets. AI without
  intervention reaches effective extinction at about 43.0, 41.0, 38.5 and 40.5 years
  respectively. This is a joint pressure-background result, not a real-world
  probability.
- The success sets on the sampled/refined ranges were contiguous, but this is an
  empirical property of the tested grid and policy class. No global monotonicity,
  unique exact threshold or irreversible-extinction theorem is claimed.

Figure: `results/figures/part_vi_windows.png/pdf`.
Tables: `results/tables/part_vi_robustness_summary.csv`,
`part_vi_robustness_tau_scan.csv`, `part_vi_robustness_manifest.json`.

## 2. Physical costs and policy effects

The following are **physical proxies**, not monetary costs. They come from the
risk-revised Part V runs (`H_ext=1e8`, `H_min=2e8`, new pressure background
`H0=1e9`).

- In the reference background all 25 policy runs are non-marginal; policy effects
  on human outcomes are negligible. `R u=1` displaces about `6.06e9 MWh` of AI
  operating allocation at a land bottleneck while changing final human adequacy by
  only about `4e-5`. A cap reduces new installation but does not change the human
  outcome. **A policy with a positive physical cost is not justified in this
  already-safe reference background.**
- In the pressure background, early R/C can avoid the first crossing but generally
  remain **marginal**; population survival is not welfare recovery. Early
  `R u=0.8` has a large displaced-AI-energy proxy (`~1.5e11 MWh` at tau=0) and
  final H about `1.20e10`; `C=0.1` blocks about `3.76e6` hardware units and gives
  final H about `1.35e10`. Both remain marginal.
- Late policies can cross the threshold and still recover: `R u=0.8, tau=50`
  ends around `3.16e8` with final `s_H=0.8`; `C=0.1, tau=50` ends around `2.26e9`
  with final `s_H=1.0`; both are first-passage/recovery cases, not irreversible
  extinction. `C` blocked about `5.95e6` hardware units in that run.
- A full shutdown is a separate branch policy. Its success branch avoids operation
  but installed stock remains; early shutdown avoids extinction while remaining
  marginal, and late shutdown can cross then recover. The assumed success
  probability is not estimated. Monetary damage is not claimed.

## 3. Conditional policy recommendations

1. **If the objective is to prevent any effective-extinction crossing**, the tested
   preventive deadlines are concentrated around **35–43 years**, with faster RSI or
   higher AI energy intensity moving them earlier. A universal “act by year X”
   recommendation is not supported; monitor the pressure parameters.
2. **If the objective is recovery after a crossing**, a later window exists in the
   tested sets, roughly **14.5–25 years beyond the preventive deadline**. This is a
   population-recovery window, not a guarantee of institutional, social or welfare
   recovery.
3. **Do not use a single deadline as a Point of No Return.** Preventive and recovery
   deadlines differ. A policy can be too late to avoid collapse but still early
   enough to recover population above `H_ext`; conversely, final recovery can occur
   while final-window adequacy remains marginal.
4. **Cap versus protection is conditional.** C has the larger recovery window in
   this grid, but can have the earlier preventive deadline under high AI energy
   intensity. R more directly protects human resources but can impose large
   displaced-operating-energy costs with little welfare gain when the human
   bottleneck is land. No monetary cost ranking is established.
5. **Measurement priorities** suggested by the sensitivity are the RSI growth rate,
   AI operational energy intensity, total energy supply, and the human resource
   floor. These are conditional model sensitivities, not a formal value-of-information
   calculation.
6. **Reporting rule:** keep effective extinction, terminal extinction, recovery,
   rapid contraction/collapse and marginalization separate. Do not call a first
   passage “irreversible extinction,” and do not call population recovery “policy
   success” without the adequacy and social qualifications.

## 4. What Part VI does not establish

No global optimal control, exact continuous critical-time theorem, monetary cost,
real-world probability, full uncertainty distribution or empirical RSI calibration.
The four sets are representative scenarios selected for robustness checking, not a
random sample. Part V/VI theory modeling stops here; the remaining work is paper
integration, references and required competition attachments.

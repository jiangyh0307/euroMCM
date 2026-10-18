> Post-review structural alternative: `deprivation_mortality=0` preserves this reference law. An explicitly separate shortfall-mortality family, modified safety certificate and sensitivity results are documented in `review_followup_zh.md`. The reference lower bound with baseline mortality alone must not be applied unchanged when that coefficient is positive.

# Population protocol & Part V decision record (P0 handoff)

**Decision:** keep the P0 human equation unchanged for the reference model. Do not increase mortality to manufacture an extinction result. The present model lets resources suppress births/effective growth but does **not** make mortality rise under deprivation. Extinction and resource-defined marginalization must therefore be reported separately.

## Human population law

The implemented law (`src/alpha/rsi.py`) is

\[
\dot H=H[\beta_Hs_H-\delta_H],\qquad 0\le s_H\le1.
\]

Here \(s_H\) is the shared allocator's human basic-resource satisfaction. Thus \(f(s_H)=s_H\ge0\); at \(s_H=0\), recruitment is zero but mortality remains \(\delta_H\). Interpret \(\beta_H\) as a potential per-capita recruitment/effective-growth contribution at full satisfaction, not a raw birth rate identifiable from a crude birth statistic. Interpret \(\delta_H\) as baseline mortality, independent of resource shortfall. This is a structural assumption and omits starvation-related excess mortality.

For constant rates,

\[
H(t)=H_0\exp\!\left(\int_0^t(\beta_Hs_H-\delta_H)du\right),\quad
H_0e^{-\delta_Ht}\le H(t)\le H_0e^{(\beta_H-\delta_H)t}.
\]

With effective threshold \(0<H_{ext}<H_0\),

\[
\delta_{crit}=T^{-1}\log(H_0/H_{ext}).
\]

**Proposition (conditional finite-horizon non-extinction).** Assume \(H_0>H_{ext}>0\), constant \(\beta_H\ge0,\delta_H\ge0\), a well-defined solution and measurable \(s_H(t)\in[0,1]\). If \(\delta_H<\delta_{crit}\), then \(H(t)>H_{ext}\) for every \(t\in[0,T]\).

**Proof.** Since \(\beta_Hs_H\ge0\), integrating the per-capita equation gives \(H(t)\ge H_0e^{-\delta_Ht}\ge H_0e^{-\delta_HT}>H_{ext}\). ∎ If \(\delta_H\ge\delta_{crit}\), this certificate is unavailable; extinction does **not** follow. Equality is not sufficient because the lower bound can touch `H_ext` at \(T\), and the code counts `H <= H_ext` as extinction.

Legacy reference values `H0=8e9`, `delta_H=0.01/year`, `H_ext=1e6`, `T=100 years` give `delta_crit=0.08987/year` and lower bound `H(100)>=2.943e9`. Extinction was mathematically excluded under that legacy threshold.

**Risk-revised Part V thresholds (not a change to the ODE):** `H_ext=1e8`,
`H_min=2e8`, rapid-collapse window `Delta=10` years with `q=0.5` plus the
`H<=H_min` size floor, cumulative loss `q_total=0.9`, and recovery flags.
The reference background still has `H(100)>=2.943e9>H_ext=1e8`; rapid/cumulative
collapse is impossible there because `delta_H=0.01` limits 10-year loss to 9.5%
and 100-year loss to 63.2%. The revised pressure background must use `H0=1e9`;
the old `scenario_stress()` with `H0=1e8` is legacy and would be extinct at t=0
under `H_ext=1e8`. See `part_v_risk_results.md`.

## Why old UQ and the controlled pilot differ

Old UQ varies demographics, initial population, supply and RSI together; it does not isolate RSI. `delta_H=beta_H*r_H`.

|Range|`beta_H`|`r_H`|Implied `delta_H`|`H0`|Vectors whose own bound excludes 100-y extinction|
|---|---:|---:|---:|---:|---:|
|conservative|0.10–0.20|0.40–0.70|0.04–0.14|1e9–8e9|45/100|
|central|0.10–0.20|0.40–0.75|0.04–0.15|0.5e9–8e9|33/100|
|aggressive|0.15–0.25|0.50–0.80|0.075–0.20|0.1e9–8e9|0/100|
|stress-augmented|0.15–0.25|0.50–0.80|0.075–0.20|0.1e9–0.3e9|0/100|

Old UQ uses `H_ext=1e6`, `H_min=1e7`, `T=100`, whereas the controlled pilot uses
`H_min=1e8` and the same extinction threshold/horizon. All ranges are exploratory;
none was preregistered. The stored per-vector check has zero bound contradictions.
Not satisfying the sufficient bound does not mean a sample must go extinct.

The new paired pilot fixes `beta_H=0.02`, `delta_H=0.01`, `H0=H_ref=8e9`, thresholds, supplies and land partition; only eight RSI parameters vary. For each draw, no-AI uses `A0=0, rho=0` and the same human/supply background. The reserved facility site remains outside human service; no land is silently transferred. Across 96 vectors and five alignments there are 480 AI-present + 96 no-AI solves; no extinction occurred. In the aggressive range at `a=0`, AI lowered mean final H by 1.36%, lowered final `s_H` by 0.023, increased final-window bad-time fraction by 0.098, and changed 4/32 draws from non-marginal to marginal. `min H` is uninformative here because every trajectory's minimum is its initial `H0`. These are conditional model contrasts, not real-world causal estimates.

The paired effect includes removing the AI construction-energy reservation in the
no-AI arm. It is the effect of the modeled AI sector as a bundle, not an isolated
estimate of operating competition alone. That narrower question would require an
additional equal-budget-reservation control; it has not been run here.

## Part V reference and evaluation decision

Use `base_rsi()` plus `configs/rsi_baseline.yaml` as the reference setting, not the joint stress case: human `beta_H=0.02`, `delta_H=0.01`, `H0=8e9`; `H_ext=1e6`, `H_min=1e8`, `s_min=0.8`; `T=100`, final window `W=10`, `p_tol=0`; `E_total=3e10 MWh/year`, `L_service=2e6 km^2`, `L_site=100 km^2`; RSI `A0=1e4`, `q0=1`, `q_max=100`, `eta=0.2`, `xi=0.2`, `omega=0.2`, `q_c=10`, `e0=10000 MWh/(hardware-unit year)`, `w_A0=1`, `c_A=0.5/year`, `M_max=1e5 hardware units/year`, `c_build=5000 MWh/unit`, `rho=0.1`. These are **ASSUMPTION**, not calibrated population standards or a measured energy allocation.

Primary outcomes: extinction event; minimum H relative to `H_min`; final-window `p_bad`/time below `s_min`; and intervention cost proxies (curtailed hardware-years, foregone construction energy, disabled operating capacity). Do not invent monetary costs.

Compare a computing-power cap with a fallible shutdown over start time, using paired draws and common backgrounds. A cap stops new additions but does not delete installed hardware. Shutdown disables operation but must not release occupied land; the current `A` conflates installed and operable stock, so implement an operating-availability state/factor before coding shutdown. Report failed shutdown branches separately. Add demographic/RSI stress arms only as labelled sensitivity cases; never tune mortality to force extinction.

**Evidence note:** selected `m_N=2700` and `m_M=2500 kcal/person/day` are ASSUMPTIONS, not estimates from the adult figures; see `results/tables/parameter_table.csv`. Before claiming empirical calibration, verify the source data and aggregation method.

# Part II — Resource-constrained RSI population dynamics

## Model

States are human population `H`, installed hardware `A`, and capability per hardware unit `q`. Resource allocation uses the same operator as Part I with operational supplies `(E_op, L_service)` and demands `(e_H H, ell_H H)`, `(e_0 q^{-xi} A, ell_A A)`.

Construction and operations are separated:

```text
E_op = E_total - R_build,   B_energy = R_build / c_build
B = min(r_A(q) A s_A, M, B_energy, (A_max-A)/tau_build)
A_dot = B - delta_A A - mu_A (1-s_A) A
q_dot = eta q (A s_A)/(A_c + A s_A) (1 - q/q_max)
H_dot = H(beta_H s_H - delta_H)
```

The endpoint-consistent budget is `R_build = min(rho E_total, [E_total - a b_H^tot e_H H]_+)`; the fixed-split rule is a comparison variant. Manufacturing is `min(M_max, c_H(1-zeta)H/H_ref + c_A zeta A s_A)` with `zeta(q)=q^nu/(q^nu+q_c^nu)`.

## Analytic results

- Efficiency–expansion threshold: `d log(e_A(q)A)/dt = A_dot/A - xi q_dot/q`.
- Industrial self-sufficiency: with `H -> 0`, `s_A=1`, and all other bottlenecks loose, `c_A zeta(q) >= delta_A` is necessary. If `c_A > delta_A`, the threshold is `q_self = q_c [delta_A/(c_A-delta_A)]^{1/nu}`.
- Finite-horizon screen: `H(t) >= H(0)e^{-delta_H t}`. With baseline demography, extinction within 100 years is impossible.

## Results

- Scenario A (low RSI): non-marginal at `a=0.5`; AI is not self-sustaining in the human-free counterfactual (`A_end/A_0 = 0.007`).
- Scenario B (moderate RSI): non-marginal at `a=0.5`; AI collapses in the human-present simulation (`A_final=4.26`) but grows to the site cap when humans are removed.
- Scenario C (rapid RSI): marginal at `a=0.5`; AI reaches the site cap (`A_final=9.08e5`) and `q=100`, but human adequacy is about 0.50.
- Stress scenario (joint human+AI): extinction at `a=0` (`t=68.86 yr`), marginal at `a=0.5/1.0`. Human-free AI is self-sustaining in B, C, and stress, conditional on exogenous power.

### Earlier 2x2 bundle comparison (not an isolated-effect experiment)

`controlled_stress_factorial.csv` separates human demography from AI pressure. At `a=0`:

| Arm | Outcome | `min H` |
|---|---|---:|
| baseline human + baseline AI | non-marginal | 8.00e9 |
| baseline human + stress AI | marginal | 3.57e9 |
| fast human + baseline AI | marginal | 1.00e8 |
| fast human + stress AI | extinction at 68.86 yr | 1.00e6 |

These arms simultaneously change demographic rates, initial population, thresholds or energy supply. Their outcomes compare bundles; they do not identify an isolated effect of RSI or demography. For a truly fixed-background RSI comparison use the 480-run pilot in `docs/results.md`: all human/resource/initial/threshold parameters are fixed and only eight RSI parameters vary. Its artifact prefix is `p0_controlled_`.

## Figures and tables

- `results/figures/fig3_rsi_scenarios.png/pdf`
- `results/figures/fig4_rsi_resources.png/pdf`
- `results/tables/rsi_scenario_summary.csv`
- `results/tables/rsi_human_free_counterfactual.csv`
- `results/tables/rsi_efficiency_expansion_diagnostic.csv`
- `results/tables/controlled_stress_factorial.csv`
- `results/figures/figS_controlled_stress.png/pdf`

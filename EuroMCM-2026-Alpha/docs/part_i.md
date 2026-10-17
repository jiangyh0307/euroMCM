# Part I — Historical validation

## Question

Can the unified resource-allocation mechanism produce a Neanderthal–modern-human replacement time of the order reported for Europe (2,600–5,400 years)?

## Model

The same weighted proportional-fair allocator used in Parts II–IV allocates food energy and effective land service between `N` and `M`:

```text
maximize  W_N log(s_N) + W_M log(s_M)
subject to 365 m_N N s_N + 365 m_M M s_M <= S_E
           ell_N N s_N + ell_M M s_M <= S_L
           0 <= s_N, s_M <= 1
```

Population dynamics are `N_dot = N(beta_N s_N - delta_N)` and `M_dot = M(beta_M s_M - delta_M)`. There is no extra logistic carrying capacity. `T_rep` is the first time `N <= kappa N_ref`; no crossing is right-censored.

## Results

- Baseline scenario: `T_rep = 2867.46 yr`, inside the European band. This is a compatibility demonstration, not calibration.
- Full 650-cell grid: 14 European-compatible cells (2.15%), 30 regional-compatible cells (4.62%), 325 censored, 0 errors. Median crossed time 525.64 years.
- The compatible region is narrow in `(w_M/w_N, beta_M/beta_N)`. H0 (`w_M=w_N`) and H1 (`w_M != w_N`) both have compatible cells; the exercise does not distinguish them.
- Sensitivity: changing `kappa`, `M0/N0`, `m_N-m_M`, or the birth-rate ratio changes `T_rep` materially. The problem-reported energy difference range spans roughly 1,700–5,600 years in the baseline scenario.

## Figures and tables

- `results/figures/fig1_historical_trajectories.png/pdf`
- `results/figures/fig2_historical_compatibility.png/pdf`
- `results/figures/figS_historical_sensitivity.png/pdf`
- `results/tables/historical_compatibility_scan.csv`
- `results/tables/historical_compatibility_summary.json`
- `results/tables/historical_sensitivity.csv`

## Status

Computed. The historical model is not causally validated; see `docs/limitations.md`.

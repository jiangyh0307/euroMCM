# Part III — Alignment, coexistence and viability

The numerical figures below are earlier exploratory artifacts, selectively checked
but not fully tolerance-certified. Current integration/acceptance rules are in
`docs/p0_acceptance.md`. The analytic certificate remains conditional on its stated
assumptions; old fixed-step minima are sampled approximations.

## Alignment

For operational human demand `D_Hj` and current supplies `S_j`, define `b_H = min(1, min_j S_j/D_Hj)` over positive human demands. The allocation adds the constraint `s_H >= a b_H`. At `a=1`, the endpoint-consistent construction budget protects the maximum human basic satisfaction attainable from current total energy and the designated land-service pool.

## Outcomes

For horizon `T`, final window `W`, thresholds `H_ext < H_min`, `s_min`, and tolerance `p_tol`:

- Extinction: `min_{t<=T} H(t) <= H_ext`.
- Marginal survival: no extinction, but the final-window bad fraction `p_bad` exceeds `p_tol`.
- Non-marginal survival: no extinction and `p_bad <= p_tol`.

The three categories are mutually exclusive and exhaustive for successful runs.

## Viability certificate

If `H_dot=H(beta_H s_H-delta_H)`, `beta_H>0`, `s_H >= a b_H`, and `b_H >= b_under > 0` uniformly on the safety boundary and other state constraints are forward invariant, then `a >= a_safe = delta_H/(beta_H b_under)` implies `H(t) >= H_min` for all `t` while the assumptions hold. This is a sufficient population-floor condition, not a non-marginal welfare guarantee.

## Results (stress scenario)

- `a_safe = 0.600`; numerical population-floor threshold on the 0.1 grid is `a_num_pop = 0.400` at `eta=0.5`.
- The certificate is conservative: the numerical grid satisfies the floor earlier than the sufficient threshold.
- Phase diagram: extinction at low `a` and higher `eta`; marginal survival elsewhere. No non-marginal outcome was observed in the stress scenario.
- Fixed-policy safe slices: at `a=0,0.2`, all tested `(A_0,q_0)` fail the population floor; at `a=0.4`, lower-left states are safe and high `A_0/q_0` states remain unsafe.
- Classification depends on `T`; results are not monotone in `a`, so no unique numerical threshold is claimed.

## Figures and tables

- `results/figures/fig5_alignment_phase.png/pdf`
- `results/figures/figS_safe_initial_states.png/pdf`
- `results/figures/figS_alignment_horizon.png/pdf`
- `results/tables/alignment_phase_diagram.csv`
- `results/tables/alignment_scan.csv`
- `results/tables/alignment_summary.txt`
- `results/tables/alignment_safe_initial_states.csv`

# Part V writing outline and execution status

The English mathematical/theoretical draft is `../docs/part_v_mathematics.md`
(equations V1–V20 and Propositions V1–V4 with proofs). The implementation and
legacy results are in `../docs/part_v_results.md`; current risk-revised results
are in `../docs/part_v_risk_results.md`. The Chinese handoff is
`../docs/part_v_handoff_zh.md`.

## Proposed paper section

1. Intervention definitions and fixed comparison background.
2. Resource protection R versus new-installation cap C.
3. Delayed-action population certificate and exact accumulated-satisfaction identity.
4. Separate physical restriction-cost ledgers and paired evaluation metrics.
5. Fallible shutdown: installed versus operating capacity and success/failure
   branch mixtures (executed in a small grid with assumed `p_s`).
6. **Executed Results:** legacy 25-run reference/stress grid (`H_ext=1e6`) and
   risk-revised 25+25 grid (`H_ext=1e8`, `H_min=2e8`, rapid/cumulative collapse,
   recovery flags). In the revised stress background (`H0=1e9`), no intervention
   reaches effective extinction at 43 years; early R/C avoid it but remain marginal;
   four late-policy cases cross below `H_ext` and recover, so they are not called
   irreversible extinction. The reference grid remains non-marginal and policies
   show no human-outcome benefit there. Point-of-no-return scan: R u=0.8 has
   sampled preventive/recovery deadlines about 42.75/57.25 years (window about
   14.5); C/A_max=0.1 has about 42.5/65.75 years (window about 23.25). These are
   finite-grid, policy-class statements, not global monotonicity theorems. A small
   fallible-shutdown branch grid and an 8-vector uncertainty pilot are executed.
7. Limitations: enforcement assumptions, fixed electricity/land background, no calibrated
   monetary cost, no general timing monotonicity, and restricted finite policy classes.

Do not present the finite grid as a global optimal-control solution, or the
population-floor certificate as a welfare guarantee. Do not merge the reference and
stress backgrounds into one probability distribution. Do not claim a unique optimal
activation time; the stress slice is non-monotone in R strength.

Figures: `../results/figures/part_v_R_timing.pdf`, `part_v_C_timing.pdf`,
`part_v_stress_R_timing.pdf`, `part_v_stress_C_timing.pdf`.

LaTeX compilation is still **NOT EXECUTED** (no engine installed). The existing
Parts I–IV draft is separate; Part V results should be integrated later with the
actual tables in `results/tables/part_v_*`.

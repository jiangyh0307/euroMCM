# Current limitations and verification boundary

1. **Historical compatibility is not causal validation.** Constant supplies,
   homogeneous space and assumed demographic means omit migration, assimilation,
   age structure and stochastic loss. The selected all-age energy means are assumptions,
   not derived estimates. The small compatible grid fraction is design-dependent.
2. **All future inputs are conditional.** Capability laws, energy-efficiency exponents,
   bargaining weights, industrial capacity and hardware-unit scale are not measured RSI
   parameters. Exogenous power does not establish autonomous grid operation.
3. **Facility land remains simplified.** The site/service partition is fixed. Retirement
   means completed physical decommissioning; merely idle equipment does not release land.
4. **Alignment is operational.** A protected resource floor is not a measure of goals,
   enforcement reliability or intent. Its population-floor proof requires resource lower
   bounds, regularity and feasibility of all states. It does not certify resource welfare.
5. **Exploratory is not preregistered.** All ranges were built during exploration. The
   later narrow stress range was informed by observed outcomes. None is confirmatory;
   frequencies and Wilson intervals are conditional model-scenario quantities.
6. **Old UQ confounds backgrounds.** It changes demographics, H0, supplies and RSI together.
   Its outcomes do not isolate RSI effects. The new pilot fixes these backgrounds but
   has only 32 vectors per range and is not a realistic prior or forecast.
7. **Verification is selective.** The old projected coarse RK4 saved trajectories fail
   some current precision checks. Adaptive refinement passes 26 targeted cases, and
   36 stratified checks find no class changes, but this does not certify the remaining
   library or bound its error rate. Full adaptive re-integration is incomplete.
8. **Threshold classification has numerical resolution.** Extinction and adequacy events
   are detected with finite solver step/tolerances. Equality uses a 1e-10 comparison
   tolerance. Multiple crossings inside one accepted step or tangencies can require
   additional refinement. Sampled population minima are not certified continuous minima.
9. **No general monotonicity or control kernel.** Safe sets are fixed-policy finite-grid
   observations; no unique critical alignment or continuous robust viability kernel has
   been proved. Failed simulations cannot be removed to claim universal safety.
10. **Sensitivity is conditional association.** Few extinction events and nearly constant
    outputs weaken rank screening. No unique measurement priority or numerical EVPI is
    established. The old rankings are retained as exploratory artifacts.

Original references have not been independently verified. The current LaTeX draft is
not compiled because the environment has no engine. Part V, the final paper, Summary
Sheet, ENOCH letter and AI-use report remain P1/P2 tasks. See `p0_acceptance.md` for the
explicit P0 handoff decision.

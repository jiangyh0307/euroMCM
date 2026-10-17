# Part IV — UQ, controlled comparison and selective verification

All sampling ranges are exploratory. Conservative, central and aggressive are
earlier broad ranges; stress_augmented is a later, outcome-informed narrow range.
None is preregistered or empirically justified as a real probability law.

## Results and provenance

The earlier 100-vector-per-range library changes human demographic rates, H0,
energy and land supplies as well as technology. Its frequencies describe joint
scenarios, not the isolated effects of RSI. The stored broad aggressive range has
2/100 extinction outcomes at a=0; the later narrow range has 42/100. Both are
conditional exploratory frequencies, not real-world probabilities.

The new RSI-only pilot freezes human rates, initial conditions, resources,
thresholds and horizon, then varies eight technology parameters. N=32 per range,
five alignments: 480 AI-present simulations plus 96 paired no-AI counterfactuals.
All no-AI draws are non-marginal. In the aggressive range at a=0, AI lowers mean
final H by 1.36%, final s_H by 0.023, and raises final-window bad-time fraction by
0.098; 4/32 outcomes change from non-marginal to marginal. At a=1 the difference is
negligible. Minimum H is H0 in every pilot draw and is not an informative paired
effect metric. All effective parameters are exported for audit.

## Verification

- Each of 400 stored parameter vectors was checked against **its own** H0 and
  delta_H. The lower-bound theorem excludes year-100 extinction for 45/100
  conservative and 33/100 central vectors; it excludes none in either high-pressure
  range. No recorded event contradicts its own bound.
- 26 targeted cases: all adaptive refinement comparisons pass and classifications
  agree. The old coarse RK4 trajectories do not all pass trajectory-error limits.
- An additional 12 stratified random vectors at three alignments give 36 checks:
  no failures or class changes. Shared alignments are not independent draws.
- Full-library adaptive rechecking is incomplete and not required for this P0
  selective-verification handoff. No global numerical error certificate is claimed.

## Sensitivity and robust alignment

The earlier Spearman rankings are exploratory associations, sensitive to the range
and output definition. Sparse extinction events make an extinction ranking unstable.
The new controlled pilot does not establish a unique measurement priority. Resource
service availability, energy supply, e0 and xi remain candidates, conditional on
the design; EVPI is not calculated.

The earlier structural library crosses proportional fairness/priority allocation
with bounded/non-saturating capability growth. Its alignment-set intersections
are finite-grid empirical statements. They are not continuous-domain guarantees
or a control viability kernel. Failed cases must not be discarded to certify safety.

Detailed tables, protocol and reproduction commands: `docs/results.md`,
`docs/p0_acceptance.md` and `README.md`.

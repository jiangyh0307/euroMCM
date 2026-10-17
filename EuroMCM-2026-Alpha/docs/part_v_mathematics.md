# Part V — Human interventions, timing and conditional policy comparison

**Mathematical specification and English theoretical draft. Implementation and
the 25-run legacy reference/pressure grids plus a risk-revised 25+25 grid:
EXECUTED.** Legacy results are in `part_v_results.md`; current risk-revised results
are in `part_v_risk_results.md`. Fallible shutdown has a small executed
success/failure branch grid (with assumed success probabilities), and the
point-of-no-return scan and 8-vector uncertainty pilot are executed. This document
does not change Parts I–IV or their population law. The primary minimal comparison is resource protection versus a cap on new
hardware installation. No empirical policy cost or shutdown failure probability is
supplied here.

## V.1 Scope and frozen background

We ask which human interventions reduce resource marginalization, under what
implementation timing, and at what physical restriction cost. We do not infer that
a policy is beneficial merely because it reduces AI hardware.

Keep the state x=(H,A,q), time in years, the same fixed land partition, and

\[
\dot H=H(\beta_Hs_H-\delta_H). \tag{V1}
\]

No famine-related death term is introduced. The population protocol fixes the
reference demographic and resource background: beta_H=0.02/year, delta_H=0.01/year,
H0=8e9, H_ext=1e6, H_min=1e8, s_min=0.8, T=100 years, final window W=10 years,
p_tol=0, E_total=3e10 MWh/year, L_service=2e6 km², L_site=100 km². These are scenario
settings (with the electricity scale a problem-derived approximation), not calibrated
standards. Preserve every other effective parameter within a paired policy comparison.
Use the saved controlled vectors if an ensemble is required; do not change their
human or supply parameters to obtain extinction cases.

The reference satisfies H(t)>=H0 exp(-delta_H t)>H_ext for t<=100. Hence extinction
frequency cannot discriminate policies in that background. Report it, but use adequacy,
shortage duration, population relative to the no-intervention path and restriction
cost proxies as principal endpoints. Stress backgrounds, if used, must be separate.

## V.2 Decisions, alignment and activation

Let a in [0,1] remain the exogenous alignment setting from the problem. A human
intervention is a policy pi; it must not be described as predicting or changing AI goals.
Let tau be the **effective activation time**, not the announcement time. An implementation
lag d>=0 can be represented by tau=t_decision+d. Supplies and policy settings are
piecewise continuous; state trajectories are continuous at activation unless a stock
reset is explicitly defined. None of the primary policies resets H,A or q.

The minimal schedules are constant after activation:

\[
u(t)=\bar u\,\mathbf1_{t\ge\tau},\quad
g(t)=\max\{a,u(t)\},\qquad 0\le\bar u\le1. \tag{V2}
\]

u is an enforced institutional protection setting. Perfect enforcement is a scenario
assumption; the floor cannot itself establish political implementability. With u<=a
the protection policy has no additional effect. No-intervention means u=0 and no
new-installation cap, while retaining the same a and all other model components.

## V.3 Policy R: human basic-resource protection

At state H>0 compute human-only satisfaction from total energy and service land:

\[
b_H^{tot}=\min\left\{1,\frac{E_{total}}{e_HH},
\frac{L_{service}}{\ell_HH}\right\}, \tag{V3}
\]

omitting a ratio with zero human demand. At H=0 use b_H^tot=1. To preserve the
alignment endpoint during construction, replace the baseline effective protection
coefficient by g consistently in both budgeting and allocation:

\[
R_g=\min\{\rho E_{total},[E_{total}-g b_H^{tot}e_HH]_+\},\quad
E_{op,g}=E_{total}-R_g. \tag{V4}
\]

Define b_H^op by (V3) with E_op,g replacing E_total. The **unchanged** proportional-fair
allocator receives populations (H,A), per-unit demands
(e_H,ell_H),(e0 q^(-xi),ell_A), weights (w_H,w_A0 q^omega), supplies
(E_op,g,L_service), and the lower bound

\[
s_H\ge g b_H^{op}. \tag{V5}
\]

Thus Policy R strengthens a resource floor, not the demographic equation. It is a
resource-protection **package**, including protection against construction withdrawal.
If instead only operating allocation is changed, that is a different policy variant
and must be labeled separately. Unused R_g stays unused, as in the baseline. We do
not silently optimize or reallocate unused energy.

**Endpoint check.** At g=1, E_op,g>=b_H^tot e_HH and E_op,g<=E_total. Together with
the unchanged land-service constraint this implies b_H^op=b_H^tot; the allocator
therefore sets s_H=b_H^tot. The guarantee is relative to the existing land partition,
not a promise to reclaim already occupied facility land.

For a given state, the floor is feasible: human consumption at s_H=g b_H^op is
no larger than each supply, and s_A=0 is feasible. If this forces AI satisfaction
to zero, use the baseline boundary extension, not log(0).

## V.4 Policy C: cap on additional installed hardware

Keep the baseline operational allocator and budget (g=a unless R is also explicitly
applied). Define the installation flow available before a regulatory cap:

\[
\begin{aligned}
B_0(x,g)&=\min\{r_A(q)A s_A,\ M(H,A,q,s_A),\ R_g/c_{build},\ B_{site}\},\\
M&=\min\{M_{max},c_H[1-\zeta(q)]H/H_{ref}+c_A\zeta(q)A s_A\},\\
B_{site}&=(A_{max}-A)_+/\tau_{build},\qquad A_{max}=L_{site}/\ell_{site}.
\end{aligned} \tag{V6}
\]

For a regulatory target C>=0 in **hardware units**, use

\[
B_C(t)=
\begin{cases}
B_0(x,a),&t<\tau,\\
\min\{B_0(x,a),(C-A)_+/\tau_{cap}\},&t\ge\tau,
\end{cases}\quad \tau_{cap}>0. \tag{V7}
\]

All terms are hardware units/year. For the minimal comparison fix tau_cap=tau_build;
it is an installation-rate adjustment time, not an empirically estimated policy delay.
One may specify C=c A_max with c in [0,1] for reproducible dimensionless scanning.
For the no-policy reference, disable (V7) rather than approximating infinity numerically.
If C=A_max and tau_cap=tau_build, (V7) duplicates the existing site bound and adds
no restriction; this is a useful analytic implementation check.

\[
\dot A=B_C-[\delta_A+\mu_A(1-s_A)]A,
\qquad \dot q=\eta q\frac{A s_A}{A_c+A s_A}(1-q/q_{max}). \tag{V8}
\]

This policy is an **installed-hardware/new-construction cap**, not a bound on
capability q, effective intelligence qA, or all realized computing services. Capability
can improve while A is capped. No hidden decommissioning or power shutdown occurs.

### Proposition V1 — cap feasibility and grandfathering

Assume C and A_max are constant after activation, C<=A_max, nonnegative retirement
rates and a well-posed system. If A(tau)<=C, then A(t)<=C for t>=tau.

**Proof.** At A=C, B_C=0, so dot A=-[delta_A+mu_A(1-s_A)]C<=0. At A=0,
B_desired=0, hence dot A=0. The boundary tangency condition gives invariance of
[0,C]. The same argument retains the physical site bound A<=A_max. ∎

If A(tau)>C, the policy does **not** instantly satisfy a stock cap. It freezes new
construction while above C and lets completed retirement reduce A. For C>0 and
delta_A>0, while above C,

\[
A(t)\le A(\tau)e^{-\delta_A(t-\tau)}.
\]

Consequently the first entry into A<=C occurs no later than
tau+log(A(tau)/C)/delta_A, provided the horizon is long enough. This is an upper
bound on compliance time, not an instantaneous reset. If delta_A=0 no such finite
bound follows; if C=0 exponential retirement need not reach zero in finite time.
Report A>C as a **grandfathered regulatory exceedance**, distinct from the physical
site infeasibility A>A_max. A declining physical A_max is outside this simple policy.

## V.5 Timing: what can be proved

### Proposition V2 — delayed protection certificate

Assume beta_H>0, delta_H>=0, H0>=H_min>H_ext. The allocation is feasible, the
system is well posed with the regularity required for forward invariance, and other
physical state constraints remain invariant. After tau, suppose operational supply
floors at H=H_min imply b_H^op>=b_under>0. If

\[
H(t)\ge H_{min}\ (0\le t\le\tau),\qquad
\max(a,\bar u)b_{under}\ge\delta_H/\beta_H, \tag{V9}
\]

then the complete trajectory remains above H_min on [0,T].

**Proof.** The first condition covers the unprotected period. At the activation
time H is continuous and H(tau)>=H_min. For any later boundary state H=H_min,
dot H>=H_min[beta_H max(a,u_bar)b_under-delta_H]>=0. Apply the Part III
forward-invariance argument on each continuous-policy interval, carrying the
continuous state through switching times. ∎

Since R_g<=rho E_total, E_op,g>=(1-rho)E_total. With prescribed lower supplies,

\[
b_{under}=\min\left\{1,
\frac{(1-\rho_{max})E_{min}}{e_H H_{min}},
\frac{L_{service,min}}{\ell_H H_{min}}\right\} \tag{V10}
\]

is conservative (omit zero-demand ratios; uncertain human demands require upper
bounds). If it gives a required g>1, the certificate is unavailable, not a proof
of extinction. Do not assume a positive electricity floor if the model endogenously
loses human-run power production; the current result conditions on prescribed supply.

A conservative pre-activation test is

\[
H_0e^{-\delta_H\tau}\ge H_{min}. \tag{V11}
\]

For delta_H>0 this gives tau<=log(H0/H_min)/delta_H; for delta_H=0 the baseline
population cannot decline. This is a sufficient timing envelope, not a numerically
optimal launch time or a necessary deadline. It can be very loose in the reference
background and certifies population only, not resource welfare.

### Proposition V3 — exact population comparison and accumulated satisfaction

For two policy trajectories with the same H0,beta_H,delta_H,

\[
\log\frac{H^{\pi}(t)}{H^0(t)}
=\beta_H\int_0^t[s_H^{\pi}(u)-s_H^0(u)]du. \tag{V12}
\]

**Proof.** Integrate the difference of the per-capita equations (V1); the common
mortality terms cancel. ∎

This identity explains why final H is informative even when min H equals H0.
Positive accumulated satisfaction difference at T implies a larger final population,
not automatically a larger minimum population or better final-window welfare.
An intervention at tau has no population jump; its effect accumulates only afterwards.

The exact threshold condition along a trajectory is

\[
H(t)\le H_{ext}\ \Longleftrightarrow\
\delta_Ht-\beta_H\int_0^t s_H(u)du\ge\log(H_0/H_{ext}). \tag{V13}
\]

Thus the general no-extinction screen delta_H T<log(H0/H_ext) is unaffected by
either policy. It cannot be used to claim policy effectiveness when it already
excludes extinction in the untreated baseline.

### Earlier is not automatically better

At a frozen state, Policy C cannot increase B relative to B_0, and Policy R
restricts the feasible allocation to protect humans. These local statements do
not order the full coupled solutions: A, q, H, automation and budgets subsequently
differ. No comparison theorem establishes that earlier activation always improves
H, final adequacy or restriction cost. Scan the full finite candidate grid; do not
use binary search for a unique policy threshold or smooth away non-monotone outcomes.

### Stronger but conservative welfare certificate

Let H_up=H0 exp(max(beta_H-delta_H,0)T). If b_H^op>=b_all>0 for all admissible
states with H<=H_up, post-activation g b_all>=s_min, and (V9) holds, then both
H>=H_min and s_H>=s_min hold after activation. If tau<=T-W and no extinction occurred
before tau, this suffices for non-marginal survival in the final window. Obtain b_all
from (V10) with H_up replacing H_min. This bound may be too conservative to implement;
failure of the bound does not imply failure of a policy.

## V.6 Endpoints and effect metrics

Retain the Part III classification exactly. Let

\[
\begin{aligned}
I_{ext}^{\pi}&=\mathbf1\{\exists t\in[0,T]:H^{\pi}(t)\le H_{ext}\},\\
p_{bad}^{\pi}&=\frac1W\int_{T-W}^{T}
\mathbf1\{H^{\pi}<H_{min}\ \text{or}\ s_H^{\pi}<s_{min}\}\,dt,\\
D_s^{\pi}&=\int_0^T\mathbf1\{s_H^{\pi}<s_{min}\}\,dt,\\
J_s^{\pi}&=\frac1{T s_{min}}\int_0^T(s_{min}-s_H^{\pi})_+dt,\\
J_H^{\pi}&=\frac1{T H_{min}}\int_0^T(H_{min}-H^{\pi})_+dt.
\end{aligned} \tag{V14}
\]

D_s has years; J_s,J_H are dimensionless. The deficits complement the exhaustive
three-category endpoint: they retain severity even when most runs share a category.
These are normative scoring conventions, not measured social welfare utilities.
Also record min H, H(T), min s_H and q(t),A(t),zeta(t).

For paired policy versus no-intervention runs, report

\[
\Delta_H=\frac{H^{\pi}(T)-H^0(T)}{H^0(T)},\quad
\Delta p_{bad}=p_{bad}^{\pi}-p_{bad}^0,\quad
\Delta D_s=D_s^{\pi}-D_s^0. \tag{V15}
\]

Lower p_bad,D_s,J_s,J_H are preferable; larger Delta_H is a population effect,
not a complete welfare ranking. Baseline pressure can be zero: an inactive policy
or no observed benefit is a valid result and must not trigger outcome-driven retuning.

**Horizon rule.** Full-horizon metrics require a full-horizon path. The effective
extinction threshold is an observation/classification event, not literal removal
of humans. Continue the physical ODE after first crossing for policy-cost comparison,
while permanently retaining the extinction flag. If the implementation instead
terminates at first crossing, all later metrics are censored and must not be compared
as if they were full-T integrals. Never replace a post-threshold path with H=0 silently.

### V.6A Risk-revised Part V adjudication

The Part V policy experiments use an expanded, mutually exclusive hierarchy in
addition to the Part III adequacy categories. All thresholds are conventions,
not empirical estimates:

\[
H_{ext}=10^8,\quad H_{min}=2\times10^8,\quad \Delta=10\ \text{yr},\quad
q=0.5,\quad q_{total}=0.9.
\]

1. **Effective extinction:** \(\min_t H(t)\le H_{ext}\). This is a
   first-passage event, not a claim of biological zero. Record
   \emph{terminal extinction} if \(H(T)\le H_{ext}\), and
   \emph{recovered after extinction} if a crossing occurred but \(H(T)>H_{ext}\).
2. **Rapid collapse:** no extinction, and for some \(t\le T-\Delta\),
   \(H(t+\Delta)\le(1-q)H(t)\) and \(H(t+\Delta)\le H_{min}\). The size
   floor prevents a large proportional fall at a still-large population from being
   labeled a small-population collapse. Record the raw rapid-contraction diagnostic
   separately.
3. **Cumulative collapse:** no prior catastrophe and
   \(H(T)\le(1-q_{total})H_0\).
4. **Marginal/non-marginal survival:** only if no catastrophe; use the final-window
   adequacy rule of Part III.

Precedence is extinction > rapid collapse > cumulative collapse > marginal >
non-marginal. These conditions are scenario policy standards; sensitivity to
\(H_{ext},H_{min},\Delta,q,q_{total}\) is required before any empirical claim.
The revised pressure background must have \(H_0=10^9\); the legacy
\(H_0=10^8,H_{ext}=10^6\) run is not interchangeable. The reference background
\(H_0=8\times10^9,\delta_H=0.01\) still excludes extinction at \(H_{ext}=10^8\):
\(H_0e^{-0.01\times100}=2.943\times10^9>H_{ext}\), and its maximum 10-year loss
is 9.5%, so rapid/cumulative collapse is impossible there. This is a property of
the unchanged ODE, not a policy result.

## V.7 Cost proxies: separate restriction, resource use and welfare

Do not add different units or call proxy restriction a monetary social cost.
Recommended physical ledgers are:

\[
\begin{aligned}
C_{install}^{C}&=\int_\tau^T[B_0(x^C(t),a)-B_C(t)]dt
&&\text{hardware units blocked at the same state},\\
E_{build}^{\pi}&=\int_0^T c_{build}B^{\pi}(t)dt
&&\text{MWh actually used for construction},\\
C_{protect}^{R}&=\int_\tau^T
 [X_{AE}^{op}(x^R(t);a)-X_{AE}^{op}(x^R(t);g)]_+dt
&&\text{MWh of immediate AI operating allocation displaced},\\
C_{duration}^{\pi}&=T-\tau
&&\text{years of active intervention}.
\end{aligned} \tag{V16}
\]

Each allocation in C_protect is recomputed at the **same** state x^R with its own
consistent budget rule; it is a frozen-state opportunity proxy. It is not the total
counterfactual system effect and not a welfare price. C_install uses min of all other
bounds before the cap: r_A A s_A minus B_C alone would incorrectly charge limitations
already imposed by manufacturing, energy or physical sites.

Report separately trajectory differences such as integral_0^T(A^0-A^pi)dt
(hardware-years, possibly signed). They include endogenous feedback and are not
identical to same-state blocked installation. A resource-protection setting duration
integral(g-a)dt has protection-years, not energy or money. Institutional enforcement
costs remain unmeasured. Monetary weights require external evidence or explicit
normative assumptions; absent these, use a Pareto table rather than a claimed net benefit.

## V.8 Minimal optimization statement

Policy candidates are
Pi_R={(tau,u_bar)} and Pi_C={(tau,C)} on finite declared grids, plus no intervention.
The study is a **restricted policy-class search**, not a global optimal-control solution.
For a specified scenario theta, compare the vector

\[
\big(I_{ext},J_H,p_{bad},J_s,C_{install},C_{protect},E_{build},C_{duration}\big), \tag{V17}
\]

with non-applicable cost components marked N/A rather than falsely zero-cost.
A Pareto frontier is meaningful within a policy's commensurate cost ledger. Across
different policies, present distinct cost columns unless a common cost conversion
is justified. If scalar optimization is required, declare the dimensionless loss
and coefficients before comparing outcomes; changing coefficients is decision sensitivity.

For uncertainty, use the same theta^(n) in every policy arm, and preserve shared
backgrounds. Differences are paired conditional scenario effects. The robust safe
policy set is an intersection over the **tested** theta/structure library; no continuous
robust claim follows. An intervention cannot be declared universally safe by excluding
its failed simulations. No Monte Carlo frequency is an objective real-world risk.

## V.9 Fallible shutdown: optional third policy, mathematically specified

This extension preserves A as installed stock and introduces an externally prescribed
operating-availability fraction v(t) in [0,1]. A known schedule is sufficient for
one intervention; endogenous restart would require a new dynamic state/model.

Let Z be the Bernoulli success indicator at effective activation tau, with assumed
success probability p_s. For disabling fraction k in [0,1],

\[
v_Z(t)=1-kZ\mathbf1_{t\ge\tau},\qquad O(t)=v_Z(t)A(t). \tag{V18}
\]

At tau, O may jump but H,A,q remain continuous. Installed footprint ell_site A
does not change. q is retained knowledge, not erased on shutdown. Use the same
allocator with populations (H,O), AI per-operating-unit demands e0 q^(-xi),ell_A,
and weight w_A0 q^omega. The policy assumes cold shutdown: idle operating energy
and allocable supporting service demands are negligible, but installed facility
land remains reserved. Standby energy is an explicitly omitted extension.

Replace each **productive/operating** A s_A by O s_A in R&D, desired expansion and
autonomous production. Use total A for site capacity and baseline decommissioning:

\[
\begin{aligned}
M_v&=\min\{M_{max},c_H(1-\zeta)H/H_{ref}+c_A\zeta O s_A\},\\
B_v&=\min\{r_A(q)O s_A,M_v,R_g/c_{build},(A_{max}-A)_+/\tau_{build}\},\\
\dot A&=B_v-\delta_A A-\mu_A(1-s_A)O,\\
\dot q&=\eta q\frac{O s_A}{A_c+O s_A}(1-q/q_{max}).
\end{aligned} \tag{V19}
\]

At v=1 these equations reduce exactly to the baseline. At successful full shutdown
(v=0), O=0, B_v=0, dot q=0 and dot A=-delta_A A. The latter represents ongoing
physical decommissioning, not instant release of sites. This assumes no external
re-seeding of AI from zero operating capacity and a persistent shutdown order; if
these assumptions are relaxed the result changes. Construction reservations R_g
remain as in the baseline even if unused. Releasing that reservation is a separate
policy variant and must be disclosed, not silently mixed into a shutdown effect.

### Proposition V4 — fallible intervention outcomes are a branch mixture

For fixed theta, tau,k,p_s and deterministic dynamics conditional on Z, let Y_S,Y_F
be the full-horizon result on successful and failed shutdown branches. Then

\[
\mathbb E[Y\mid\theta]=p_sY_S+(1-p_s)Y_F,
\quad P(C=c\mid\theta)=p_s\mathbf1_{C_S=c}+(1-p_s)\mathbf1_{C_F=c}. \tag{V20}
\]

**Proof.** Condition on the two mutually exclusive values of Z. ∎

If failure leaves the system unaffected, its trajectory equals no intervention up
to an explicitly modeled attempt cost. Do not simulate a mean availability
v=1-k p_s and call it the expected outcome: nonlinear feedback and threshold
classification do not commute with expectation. Success probabilities are assumed
settings, not empirically estimated here. If p_s depends on the state at tau, evaluate
it on that scenario's common pre-intervention trajectory; do not invent a capability
failure law to force an outcome. Record disabled hardware-years integral(1-v)A dt
as a physical restriction proxy, not as monetary damage.

## V.10 Implementation status and remaining deliverables

Equations (V1)–(V8) are implemented in `src/alpha/rsi.py` through the optional
`Intervention` interface and `simulate_rsi(..., intervention=..., terminate_on_extinction=False)`.
The legacy 25-run reference grid and a separate 25-run exploratory pressure slice
have been executed (`docs/part_v_results.md`). The risk-revised 25+25 grid uses
\(H_{ext}=10^8,H_{min}=2\times10^8\), a new \(H_0=10^9\) pressure background,
and the hierarchy in V.6A; see `docs/part_v_risk_results.md`. No failed runs were
recorded. The revised pressure no-intervention path crosses \(H_{ext}\) at 43.0
years; early R/C policies avoid the crossing but remain marginal, and four
late-policy paths cross then recover and are not called irreversible extinction.

Executed outputs:

1. Timing–intensity maps for R and C in the reference background and a separate
   stress slice, including inactive and ineffective settings.
2. Full per-run tables for population, adequacy, deficit duration, and restriction proxies.
3. Separate reference and stress figures; before/after policy switching is recorded
   in the trajectory fields.
4. Shutdown is executed as a small branch grid under assumed `p_s`; no empirical
   failure probability or monetary cost is supplied.
5. A point-of-no-return scan (1-year grid plus 0.25-year local refinement) and an
   8-vector RSI uncertainty pilot are executed. Full uncertainty distributions and
   global optimal control are **NOT EXECUTED**.
6. Results wording is limited to actual computations; no global optimum or general
   monotone timing rule is claimed. Sampled preventive/recovery deadlines are in
   `part_v_risk_results.md`.

The reference background is already non-marginal, so its policy runs mostly show
zero human outcome benefit or cost-only displacement. The stress slice is exploratory
and must remain separate. Do not use either as a real-world policy forecast.

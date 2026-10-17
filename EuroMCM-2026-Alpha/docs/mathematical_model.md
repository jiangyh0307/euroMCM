# A unified resource-competition model: mathematical specification v1

**Status: mathematical specification; implementation, unit tests and numerical experiments executed. See `docs/results.md` for computed results and `README.md` for reproduction commands.**
This document is also the English technical draft for Parts I–IV. Numbered results are conditional mathematical results, not empirical discoveries. Source authority: `2026_Problem_Alpha.pdf`, Sections 3–6. References named below are transcribed from the problem; their original publications have not yet been independently checked.

## 1. Scope, evidence and modeling philosophy

We ask under what physical, dynamical and allocation conditions humanity can avoid extinction and marginalization when sharing resources with recursively self-improving systems. Historical and future dynamics use exactly the same resource-allocation operator. Historical compatibility tests a mechanism's ability to produce an observed order of magnitude; it does not establish a causal explanation for Neanderthal disappearance. Future calculations will be conditional scenarios, not forecasts.

The problem supplies ranges rather than population time series:

|Constraint|Value|Attribution in problem|Interpretation|
|---|---|---|---|
|European overlap|2,600–5,400 yr|Higham et al. (2014)|European compatibility target|
|France/northern Spain overlap|1,400–2,900 yr|Djakovic et al. (2022)|Separate regional target|
|South-west France density ratio|modern:Neanderthal approximately 10:1|Mellars and French (2011)|Disputed regional constraint, not European initial condition|
|Adult female Neanderthal energy|3,000–5,000 kcal/day|Snodgrass and Leonard (2009)|Adult estimate, not whole-population mean|
|Adult male Neanderthal energy|4,000–7,000 kcal/day|Same|Same|
|Extra Neanderthal energy|100–350 kcal/day|Froehle and Churchill (2009)|Same-climate comparison; population extrapolation requires assumptions|
|Data-centre electricity in 2024|415 TWh; 1.5% of world total|IEA, Energy and AI (2025)|All data centres, not RSI-only electricity|
|Data-centre electricity growth since 2017|approximately 12%/yr|Same|Past aggregate trend, not an RSI growth parameter|
|Data-centre electricity in 2030|945 TWh|Same|Projection, not an observation|

These entries are **SOURCE (problem-reported)**. No future RSI parameter is directly measured by these entries. A derived scale, such as 415/0.015 TWh/yr for world electricity, is an **ESTIMATE**, approximate and dependent on rounded inputs. It is not the supply available to our modeled system.

Three important choices are explicit:

1. Resource satisfaction is a fixed-proportions (Leontief-type) bundle. More of one resource cannot compensate for less of another.
2. Installed hardware and capability per hardware unit are distinct states.
3. Operational resource protection must be distinguished from protection against construction withdrawals. Section 5 specifies an endpoint-consistent budget policy; a fixed construction share is a labeled comparison variant.

## 2. Unified allocation operator

### 2.1 Definition and units

For active populations i=1,2, let P_i>0, per-unit demands d_ij>=0, total demands D_ij=d_ij P_i, supplies S_j>=0, and weights W_i=w_i P_i>0. Choose satisfaction s_i in [0,1]. Actual allocations are

\[
X_{ij}=D_{ij}s_i,\qquad \sum_iX_{ij}\le S_j. \tag{1}
\]

Each inequality has its own resource unit. Energy flows (kcal/yr or MWh/yr), land services (km² of usable capacity), and hardware production (hardware units/yr) are never added to one another. Manufacturing is a production bound, not an operational resource in the baseline allocator.

Weights must be measured in a common arbitrary utility-weight unit. For humans versus hardware, w_H has weight/person and w_A has weight/hardware-unit. Their numerical comparison is meaningless until population and hardware units are fixed. Changing a population unit requires transforming both its per-unit demand and per-unit weight. Multiplying all weights by a common positive factor leaves allocations unchanged.

Let b_H=min(1,min_{j:D_Hj>0} S_j/D_Hj), with b_H=1 when all human demands vanish. Define l_H=a b_H, l_A=0. In historical applications a=0. The main operator solves

\[
\max_{l_i\le s_i\le1}\ \sum_iW_i\log s_i
\quad\text{subject to (1).} \tag{2}
\]

When a strictly positive feasible satisfaction vector exists, strict concavity gives a unique maximizer. The feasible set is compact; the objective tends to minus infinity as a positive-weight coordinate approaches zero, so existence follows by restriction to a compact positive superlevel set. Strictly positive supply for every demanded resource, positive weights, and a<1 suffice here. At a=1 a positive solution may still exist if protected human consumption leaves positive residual capacity for AI on every AI-demanded resource.

Remove P_i=0 groups from optimization; return zero actual allocations for them and a documented satisfaction convention s_i=1. A zero-demand active group has optimal s_i=1. No arbitrary population cutoff is part of the mathematics. Tiny positive groups must not be silently deleted by the solver. If a group requires a zero-supply resource, its satisfaction is forced to zero.

**Boundary extension.** When feasibility forces s_i=0, ordinary logarithmic utility is not a finite optimization problem. Define the allocation by the limit of maximizers of sum W_i log(s_i+epsilon) as epsilon decreases to zero. For the two-group forced-zero cases here, fix the forced-zero coordinates first and maximize over the remaining coordinates; this gives the same unique limit. In particular at a=1, s_H=b_H, and AI receives its maximal feasible satisfaction from residual supplies. This boundary-aware extension avoids using log(0) in a solver. Positive-feasible cases use the exact unregularized operator.

### 2.2 KKT conditions

Let lambda_j>=0 multiply resource constraints, u_i>=0 multiply upper bounds and v_i>=0 multiply lower bounds. The Lagrangian, for a positive optimum, is

\[
\mathcal L=\sum_iW_i\log s_i+\sum_j\lambda_j(S_j-\sum_iD_{ij}s_i)
 +\sum_i u_i(1-s_i)+\sum_i v_i(s_i-l_i). \tag{3}
\]

Primal feasibility, dual nonnegativity, stationarity and complementarity are

\[
\frac{W_i}{s_i}-\sum_j\lambda_jD_{ij}-u_i+v_i=0, \tag{4}
\]
\[
\lambda_j(S_j-\sum_iD_{ij}s_i)=0,\quad
u_i(1-s_i)=0,\quad v_i(s_i-l_i)=0. \tag{5}
\]

Under a constraint qualification these are necessary, and for this concave problem sufficient. At degenerate boundaries use the reduced boundary problem instead of asserting Slater's condition. For l_i<s_i<1,

\[
s_i=\frac{W_i}{\sum_j\lambda_jD_{ij}}. \tag{6}
\]

Lambda_j is marginal optimal utility per unit additional resource j **when the protection floor is held fixed**. Its unit is utility-weight/resource-unit. If l_H=a b_H(S) changes with supplies, the envelope derivative at a differentiable point is instead

\[
\frac{\partial V}{\partial S_j}=\lambda_j-v_H\frac{\partial l_H}{\partial S_j}. \tag{7}
\]

Thus a raw resource multiplier is not automatically the total comparative-static price of supply under an endogenous protection floor. Shadow prices may be nonunique for redundant constraints although satisfaction is unique. Report reliability and degeneracy rather than fabricated prices.

With an energy bottleneck only, the denominator in (6) is lambda_E D_iE; a land bottleneck gives lambda_L D_iL. With several binding resources it is their price-weighted sum. Large demand for a scarce resource reduces satisfaction at given weight. Two binding nonparallel constraints determine the two satisfactions; they support a positive interior optimum only if nonnegative multipliers solve (4). Binding need not mean strictly positive multiplier.

### 2.3 Proposition 1: single-resource allocation

Suppose a=0, P_i,w_i,d_i,S>0, the resource is exhausted and 0<s_i<1. Then

\[
s_i=\frac{S W_i}{D_i(W_1+W_2)}
=\frac{S w_i}{d_i(w_1P_1+w_2P_2)}. \tag{8}
\]

**Proof.** Stationarity gives D_i s_i=W_i/lambda. Summing over groups gives S=(W_1+W_2)/lambda. Substitute and cancel P_i. Conversely, if both values in (8) lie strictly between zero and one, these values and lambda=(W_1+W_2)/S satisfy all KKT conditions. Strict concavity establishes uniqueness. ∎

If S>=D_1+D_2, both satisfactions equal one. In an intermediate regime use capped water filling s_i=min(1,W_i/(lambda D_i)), with lambda chosen to exhaust S. With a fixed feasible lower bound, replace this by clip(W_i/(lambda D_i),l_i,1). Endpoint forced-zero cases require the boundary rule above. Formula (8) must not be used if a cap/floor binds or if multiple resource constraints are active.

### 2.4 Exact two-group solver specification, before coding

The feasible set in (s_1,s_2) is a polygon. For positive-feasible cases enumerate feasible vertices with positive coordinates and stationary points on every nontrivial feasible boundary segment. For segment s(t)=u+t v, t in [0,1], an interior stationary point satisfies

\[
\frac{W_1v_1}{u_1+t v_1}+\frac{W_2v_2}{u_2+t v_2}=0. \tag{9}
\]

The derivative is strictly decreasing along a nonconstant segment with positive weights. If v_1v_2!=0, its candidate root is

\[
t_*=-\frac{W_1v_1u_2+W_2v_2u_1}{(W_1+W_2)v_1v_2}. \tag{10}
\]

Retain only roots inside the segment and positive domain; monotone or coordinate-constant edges attain their maximum at an endpoint. The increasing objective places the optimum on the upper feasible boundary, unless (1,1) is feasible. Comparing these finite candidates gives the exact optimizer in exact arithmetic. Handle lower-dimensional polygons separately.

Extreme scale separation (for example, one population at 1e-20 of the other) can make a vertex look feasible within floating-point tolerance even though its objective gain is not negligible. The implementation therefore first solves each single-resource relaxation by robust water filling. If that relaxation's maximizer is feasible for every resource, it is globally optimal for the full problem, because it maximizes the objective over a superset of the feasible set. If no relaxation is feasible, the polygon/KKT candidates are used. Regression tests cover populations down to 1e-40. This is an implementation safeguard, not a change to the mathematical problem.

Return s, X, utilization sum_i X_ij/S_j (undefined, not artificially 100%, when S_j=0), slack, active constraints, success, and reliable KKT multipliers if recoverable. Normalize each constraint by its own positive scale; never add unscaled residuals of different units. A floating-point feasibility repair must preserve the human floor, so uniform downscaling of both satisfactions is not generally valid.

## 3. Part I: historical competition and partial identification

### 3.1 Dynamics

N and M are persons in the same fixed region, time is years. For historical energy and effective habitat access,

\[
D_{NE}=365m_NN,\quad D_{ME}=365m_MM,\quad
D_{NL}=\ell_NN,\quad D_{ML}=\ell_MM. \tag{11}
\]

Here m_i is kcal/person/day and ell_i is km²/person of effective access. Adult energy estimates can be used as an explicitly labeled adult-equivalent demographic approximation; they must not silently be labeled measured all-age averages. A future calibration can use m_i=sum_g pi_ig m_ig with age/sex fractions pi_ig. Without these fractions, whole-population m_i and its difference remain assumption-dependent.

With constant supplies or prescribed positive supply paths, use (2) at a=0 and

\[
\dot N=N(\beta_Ns_N-\delta_N),\qquad
\dot M=M(\beta_Ms_M-\delta_M). \tag{12}
\]

Rates beta_i,delta_i are yr^-1. For finite bounded rates,
P_i(t)=P_i(0)exp(integral_0^t(beta_i s_i-delta_i)du), proving positivity for positive initial conditions and invariance of zero populations. No separate logistic term is added. Rates are effective demographic parameters rather than measured fertility schedules.

Let r_i=delta_i/beta_i. Baseline viable resident populations require 0<r_i<1. If beta_i<delta_i a population declines even with full resources; historical replacement in that regime is not evidence for resource competition.

### 3.2 Proposition 2: relative advantage is not extinction

Under the interior single-energy-bottleneck conditions of Proposition 1,

\[
\frac{d}{dt}\log\frac{M}{N}
=\frac{S_E}{w_NN+w_MM}
\left(\frac{\beta_Mw_M}{d_M}-\frac{\beta_Nw_N}{d_N}\right)
+\delta_N-\delta_M,\quad d_i=365m_i. \tag{13}
\]

**Proof.** Subtract dot N/N from dot M/M in (12), then insert (8). ∎

For equal beta and equal delta, M/N increases exactly when w_M/d_M>w_N/d_N. This is an advantage in acquisition weight per unit basic energy requirement. It neither proves finite-time extinction nor even dot N<0. The latter requires s_N<r_N.

Define N_crit=kappa N_ref with a fixed, stated N_ref, 0<kappa<1, and initially N(0)>N_crit. Then

\[
T_{rep}=\inf\{t\ge0:N(t)\le N_{crit}\}. \tag{14}
\]

If no crossing is observed before T_hist, record a right-censored outcome T_rep>T_hist, never a fabricated time T_hist. A deterministic positive solution does not reach zero in finite time under (12). Moreover dot N>=-delta_N N implies

\[
T_{rep}\ge \delta_N^{-1}\log[N(0)/N_{crit}] \tag{15}
\]

when delta_N>0. This is a useful impossibility screen before simulations.

### 3.3 Boundary equilibria and invasion

For a single resource and a viable sole resident i, its positive equilibrium is

\[
P_i^*=S/(d_i r_i). \tag{16}
\]

It is stable within the resident axis: near it, dot P_i=beta_i S/d_i-delta_i P_i, with derivative -delta_i. A rare invader k has limiting satisfaction and per-capita invasion rate

\[
s_{k|i}=\min\left(1,\frac{w_k d_i r_i}{w_i d_k}\right),\qquad
g_{k|i}=\beta_k s_{k|i}-\delta_k. \tag{17}
\]

For 0<r_k<1, g_{k|i}>0 exactly when

\[
C_k>C_i,\qquad C_i=\frac{w_i}{d_i r_i}=\frac{\beta_iw_i}{\delta_i d_i}. \tag{18}
\]

Thus with distinct C values one boundary equilibrium is transversely invasible and the other is transversely attracting. These are local invasion statements; global exclusion is not inferred merely from a ratio plot. If C_N=C_M=C, there is a continuum of equilibria

\[
w_NN+w_MM=SC,\quad N,M>0, \tag{19}
\]

with s_i=r_i. Linearization has a zero eigenvalue along this continuum and a negative transverse eigenvalue. This is neutral coexistence, not an isolated asymptotically stable coexistence point.

For general multi-resource coexistence, set s_i=r_i in the allocator and require

\[
\sum_i d_{ij}r_iP_i\le S_j,\qquad
\frac{w_i}{r_i}=\sum_j\lambda_j d_{ij},\qquad
\lambda_j\left(S_j-\sum_i d_{ij}r_iP_i\right)=0. \tag{20}
\]

These are feasibility and KKT conditions for an interior positive equilibrium. For two independent binding resources, solve the two resource equations for positive P_i and the two stationarity equations for nonnegative lambda. With strict multiplier positivity and 0<r_i<1, the binding pattern persists locally. Both resources binding forces D^T s=S, so P_i s_i=c_i, where d^T c=S. Consequently dot P_i=beta_i c_i-delta_i P_i and the local Jacobian is diag(-delta_N,-delta_M). This proves local asymptotic stability in that nondegenerate binding region. At active-set changes use one-sided analysis or direct perturbation simulations, not an unjustified smooth Jacobian.

### 3.4 Compatibility sets and non-identifiability

Define the admissible parameter domain before searching. It includes demographic plausibility, positive supplies/demands, common region, and the stated energy-extrapolation convention. The European set is

\[
\Theta_{hist}^{EU}=\{\theta:2600\le T_{rep}(\theta)\le5400,
100\le m_N-m_M\le350,\ \theta\text{ admissible}\}. \tag{21}
\]

The energy-difference restriction here is conditional on applying the adult comparison to effective per-person demands. A separate regional set uses 1400–2900 years. Do not intersect these times as if they described the same population trajectory. The disputed 10:1 density ratio should enter separate regional analyses as (i) an explicitly assumed initial ratio, (ii) an uncertain observation-time ratio, and (iii) omitted. A tolerance around 10 is an assumption, not a source-provided error bar.

Compare H0:w_N=w_M and H1:w_N!=w_M under identical demographic/resource ranges. Evidence that H0 has compatible points would show energy differences can suffice within those assumptions, not that acquisition advantages are absent. Failure to find points is search-domain dependent. No compatibility result has yet been computed.

Several exact invariances establish non-identifiability:

* Common multiplication of all w_i leaves allocations unchanged.
* Multiplying every population, supply and absolute threshold by c>0 leaves satisfaction and normalized trajectories unchanged; it does not leave an independently fixed absolute extinction threshold unchanged.
* Multiplying demands and supply of one resource by a common factor leaves the allocation unchanged.
* Multiplying all demographic rates by c rescales the autonomous historical clock by 1/c. For beta_i=c beta_i^0 and delta_i=c delta_i^0, P_c(t)=P_1(ct) and T_rep,c=T_rep,1/c.

Thus matching one duration cannot identify all rates, resource scales, relative weights and thresholds. Report compatible counts/fractions under a declared design measure, projections and parameter correlations; a fraction is not an intrinsic volume independent of parameterization or a posterior probability. Threshold sensitivity must accompany any coexistence-time claim. Near a stable exclusion equilibrium with loser invasion rate g<0, an asymptotic tail gives T_rep approximately t_0+log[N(t_0)/N_crit]/|g|; it is not an exact full-trajectory formula.

## 4. Part II: physical RSI dynamics

### 4.1 States, resource units and stock accounting

H is persons, A is installed hardware-equivalent units, q>0 is a dimensionless capability index, and t is years. A hardware unit requires a reproducible definition before calibration. Reference scales H_ref,A_ref,q_ref may normalize displays, but cannot change dynamics unless demands and weights are transformed consistently.

Operational demands and weights are

\[
D_{HE}=e_HH,\ D_{HL}=\ell_HH,\quad
D_{AE}=e_0q^{-\xi}A,\ D_{AL}=\ell_AA,
\quad W_H=w_HH,\ W_A=w_{A0}q^\omega A. \tag{22}
\]

e_H has MWh/(person yr), e_0 has MWh/(hardware-unit yr), ell_H and ell_A have km² per respective unit, xi,omega>=0 are dimensionless. e_H represents electricity/essential-service energy, not metabolic calories. ell_A is supporting land-service demand; facility footprints are separately reserved. We fix ell_A as the baseline, avoiding an unsupported capability-dependent land-efficiency law.

Let L_total=L_site+L_service+L_other be a fixed disjoint partition, all in km². A_max=L_site/ell_site, with ell_site in km²/hardware-unit. Facility land is never allocated again through L_service. Idle installed equipment remains in A and occupies its site. For the requested three-state model, delta_A and mu_A(1-s_A) describe **completed retirement with physical decommissioning**, not mere operational shutdown. Physical decommissioning, not losing power, releases occupied facility capacity. This rapid-removal aggregate approximation must be disclosed; a subsequent model can add an idle/unremoved-hardware stock. Calling mu_A a pure shutdown rate while removing its hardware from the footprint is inconsistent.

### 4.2 Construction and operations

Let E_total be the available annual energy flow in MWh/yr, c_build the MWh per newly installed hardware unit, and rho in [0,1] a maximum construction-budget fraction. Define a budget R_build and

\[
E_{op}=E_{total}-R_{build},\quad B_E=R_{build}/c_{build}. \tag{23}
\]

The original fixed-split variant sets R_build=rho E_total. Section 5 explains why this variant alone cannot ensure the original problem's full a=1 endpoint, and specifies the main endpoint-consistent alternative. Unused budgets are not automatically reallocated in the baseline. Thus actual operation plus actual building energy never exceeds E_total.

With s from the unified operator for supplies (E_op,L_service), define

\[
\zeta(q)=\frac{q^\nu}{q^\nu+q_c^\nu},\quad
r_A(q)=r_0q^\gamma, \tag{24}
\]
\[
M=\min\left\{M_{max},c_H[1-\zeta(q)]\frac{H}{H_{ref}}+c_A\zeta(q)A s_A\right\}, \tag{25}
\]
\[
B=\min\left\{r_A(q)A s_A,\ M,\ \frac{R_{build}}{c_{build}},\
\frac{(A_{max}-A)_+}{\tau_{build}}\right\}. \tag{26}
\]

r_0,c_A have yr^-1, gamma>=0 is dimensionless, c_H,M_max have hardware-units/yr, and tau_build has years. All four production bounds are hardware-units/yr. gamma=0 is the baseline; gamma>0 is an additional scenario, not a necessary consequence of intelligence.

The diminishing human-production term in (25) makes a substantive assumption: automation substitutes for the old human-supported channel. If automated production is initially weak, total capacity can temporarily fall as zeta rises. That behavior is not a mathematical error, but should be checked against a non-subtractive alternative M=min(M_max,c_H H/H_ref+c_A zeta A s_A).

Human dependence here acts through aggregate hardware production. Taking E_total as exogenous additionally assumes power availability is maintained independently; the model does not then establish autonomous power-plant operation. A scenario extension may use E_total=E_floor+E_scale[(1-zeta_E)f_H(H)+zeta_E f_A(A s_A)], but this creates implicit allocation feedback and must not be inserted without a new well-posedness analysis. The P0 core retains prescribed supplies and explicitly conditions self-sufficiency on electricity availability.

### 4.3 Coupled equations and invariant domain

\[
\begin{aligned}
\dot H&=H(\beta_Hs_H-\delta_H),\\
\dot A&=B-\delta_AA-\mu_A(1-s_A)A,\\
\dot q&=\eta q\frac{A s_A}{A_c+A s_A}(1-q/q_{max}).
\end{aligned} \tag{27}
\]

beta_H,delta_H,delta_A,mu_A,eta are yr^-1; A_c has hardware units; q_max is dimensionless. A_c>0, q_max>0, 0<q(0)<=q_max and 0<=A(0)<=A_max. The alternative non-saturating law removes (1-q/q_max) without changing allocation or other equations.

For constant A_max and nonnegative parameters the domain H>=0, 0<=A<=A_max, 0<q<=q_max is forward invariant, subject to a well-posed allocation-coupled ODE. H positivity follows from its multiplicative equation. At A=0, desired construction is zero and dot A=0. At A=A_max, B_site=0 and dot A<=0. The q derivative vanishes at q=q_max and is nonnegative below it; q=0 is invariant and positive solutions cannot cross it. The non-saturating alternative satisfies q(t)<=q(0) exp(eta t), hence has no finite-time blow-up under this law. Also H(t)<=H(0)exp[(beta_H-delta_H)t]. These bounds prevent finite-time state escape for fixed finite parameters and supplies.

The assumed allocator is continuous and piecewise smooth in nondegenerate positive-state regions; switches require a locally Lipschitz extension or a stated solution concept. At the a=1 forced-zero face use the explicit boundary formula. Do not invoke a global smoothness theorem across extinct populations or zero supplies without checking it. For safety proofs below assume existence, uniqueness and the indicated local regularity. A numerical integrator must enforce/verify domain validity rather than conceal invalid states by clipping output.

For a time-varying A_max, invariance requires dot A<=dot A_max on A=A_max. A site bound on new construction alone does not ensure this if capacity falls. Baseline L_site is constant; falling-site scenarios require explicit retirement or an infeasibility report.

### 4.4 A finite-horizon extinction impossibility screen

The human equation satisfies the one-sided bound

\[
\dot H=H(\beta_Hs_H-\delta_H)\ge-\delta_HH,
\qquad H(t)\ge H(0)e^{-\delta_Ht}. \tag{27a}
\]

Consequently, if

\[
H(0)e^{-\delta_HT}>H_{ext}, \tag{27b}
\]

then no extinction outcome can occur by horizon T under **any** admissible alignment or AI trajectory in this model. This is a necessary-condition screen, not a welfare guarantee. For the fixed baseline H(0)=8x10^9, delta_H=0.01 yr^-1, T=100 yr and H_ext=10^6, the lower bound is 2.943x10^9 persons. Extinction is excluded; both marginal and non-marginal survival remain possible. This does not explain all old UQ outcomes, whose demographic rates vary. The individual audit excludes extinction for 45/100 conservative and 33/100 central vectors and no vectors in the two higher-pressure ranges; no recorded event contradicts its own bound. Lack of this certificate does not imply extinction.

**Proof.** Drop the nonnegative term beta_H s_H from the H equation and integrate the resulting linear inequality. ∎

### 4.5 Proposition 3: efficiency–expansion threshold

For A,q>0, unconstrained AI operational energy demand is E_A^d=e_0q^(-xi)A. Therefore

\[
\frac{d}{dt}\log E_A^d=\frac{\dot A}{A}-\xi\frac{\dot q}{q}. \tag{28}
\]

**Proof.** Differentiate log e_0+log A-xi log q. ∎

Demand increases exactly when dot A/A>xi dot q/q. Actual energy allocation is s_A E_A^d, whose log derivative, when s_A>0 and differentiable, additionally includes dot s_A/s_A. Efficiency in this scenario does not imply decreasing aggregate consumption; demand and actual consumption must be plotted separately.

### 4.6 Proposition 4: industrial self-sufficiency threshold

Freeze q, let H tend to zero and suppose s_A=1. Then

\[
\dot A=\min\{r_A(q)A,M_{max},c_A\zeta(q)A,B_E,B_{site}\}-\delta_A A. \tag{29}
\]

For A>0, nonnegative hardware growth holds **if and only if every term in the minimum is at least delta_A A** in this frozen fully supplied state. In particular the necessary industrial condition is c_A zeta(q)>=delta_A. If c_A>delta_A>0 its equality occurs at

\[
q_{self}=q_c\left(\frac{\delta_A}{c_A-\delta_A}\right)^{1/\nu}. \tag{30}
\]

**Proof.** c_A q^nu/(q^nu+q_c^nu)>=delta_A is equivalent to (c_A-delta_A)q^nu>=delta_A q_c^nu. Solving the equality gives (30); the function is strictly increasing for q>0. The minimum criterion follows directly from (29). ∎

If 0<c_A<=delta_A, finite q with zeta<1 cannot sustain positive A at full resource adequacy. The delta_A=0 edge case is degenerate and does not require the positive threshold (30). If q_self>q_max, the bounded-capability baseline cannot attain the threshold. Equality at q_max may be approached only asymptotically. Even q>q_self does not suffice if desired expansion, M_max, construction energy or site availability is tighter.

With s_A<1, a necessary condition strengthens to c_A zeta(q)s_A>=delta_A+mu_A(1-s_A). For general simulations distinguish (i) crossing q_self, (ii) satisfying all frozen-state replacement bounds, and (iii) surviving an H=0 counterfactual with allocation recomputed. Only (iii) tests sustained independence inside the full model, and still assumes the stated power supply. None of these is automatically a bifurcation theorem.

## 5. Part III: alignment and conditional viability

### 5.1 Operational protection and the construction-budget issue

For supplies in the operational allocator, define b_H=min(1,E_op/(e_HH),L_service/(ell_HH)) for H>0. Its protection floor is exactly s_H>=a b_H. At a=0 it is ordinary competition. At a=1 it maximizes human satisfaction over the operational feasible set, leaving only residual services to AI.

**Necessary qualification:** with a fixed positive rho, AI construction can reduce E_op below human needs even when E_total would meet those needs. For example E_total=e_HH with nonbinding land gives s_H<=1-rho at a=1. Thus fixed construction reservation plus an operational floor is not by itself the original problem's full endpoint “takes nothing humans need.”

For the main endpoint-consistent version retain the fixed rho split whenever it is harmless, but set

\[
b_H^{tot}=\min\{1,E_{total}/(e_HH),L_{service}/(\ell_HH)\},\qquad
R_{build}=\min\{\rho E_{total},[E_{total}-a b_H^{tot}e_HH]_+\}. \tag{31}
\]

At H=0 set b_H^tot=1 and the reserved human energy to zero. Equation (31) is a maximum-budget rule, not actual energy expenditure. It changes no allocation objective. At a=0 it gives the original rho split. At a=1, E_op>=b_H^tot e_HH and E_op<=E_total, hence b_H=b_H^tot. The floor then gives s_H=b_H^tot: construction and AI operations cannot reduce the maximum human basic-service satisfaction attainable from total current energy and the designated human-accessible land-service pool. Spare energy can still fund construction. For intermediate a the protection remains a b_H calculated from E_op, not a b_H^tot; do not conflate these quantities.

This proof is relative to the fixed land partition. It does not restore historical land already committed to facilities. Declare L_site precommitted before the modeled horizon and L_service protected from further facility conversion. A broader interpretation requiring return of occupied sites at a=1 requires an explicit land-reallocation/decommissioning model. This limitation cannot be repaired merely by increasing an operational floor.

### 5.2 Exact, exhaustive finite-horizon outcomes

Choose T>0, final window length 0<W<=T, 0<H_ext<H_min<=H(0), and 0<s_min<=1. All are decision/scenario assumptions, not observed facts. Define E={min_[0,T] H<=H_ext}. To interpret “long-term” in the final window define

\[
p_{bad}=\frac1W\int_{T-W}^{T}
\mathbf1\{H(t)<H_{min}\ \text{or}\ s_H(t)<s_{min}\}\,dt. \tag{32}
\]

For a declared tolerance p_tol in [0,1), define: extinction if E; marginal survival if not E and p_bad>p_tol; non-marginal survival if not E and p_bad<=p_tol. These three outcomes are mutually exclusive and exhaustive. A strict baseline p_tol=0 permits no positive-duration shortfall. Equality H=H_min or s_H=s_min passes. Use a baseline W=10 yr with T=100 yr and sensitivity T=50,150 yr, altered W,p_tol,H_ext,H_min,s_min. These values specify a classification convention, not an empirical calibration.

Population safety min_[0,T] H>=H_min differs from final-window non-marginal survival: the latter may permit earlier population shortfalls. The numerical alignment threshold must identify which criterion it uses.

### 5.3 Proposition 5: conditional forward-invariance guarantee

Let K={H>=H_min} intersect the feasible hardware/capability domain. Suppose:

1. beta_H>0, delta_H>=0 and H_min>0; H(0)>=H_min.
2. The full coupled system has a unique solution on [0,T], is continuous in time (piecewise continuity with a valid Carathéodory formulation also suffices), and is locally Lipschitz in state near the safety boundary.
3. Other state constraints are forward invariant; current service supplies at H=H_min have a uniform lower bound such that b_H>=b_under>0 over all admissible t,A,q and uncertainty values being considered.
4. The allocator enforces s_H>=a b_H exactly, including its endpoint extension.
5. a b_under>=delta_H/beta_H.

Then H(t)>=H_min for every t in [0,T]. In particular a sufficient alignment level is

\[
a_{safe}=\frac{\delta_H}{\beta_H b_{under}}\le1. \tag{33}
\]

**Proof.** Define B(H)=H-H_min. At every point of the feasible boundary H=H_min,
dot B=H_min(beta_H s_H-delta_H)>=H_min(beta_H a b_under-delta_H)>=0.
Thus the vector field is in the tangent half-space to K at its human-population boundary. At every other feasible-domain boundary it is inward/tangent by assumption 3 and the physical invariance conditions. The tangent-cone forward-invariance theorem for locally Lipschitz ODEs implies invariance of their intersection K. Equivalently, a local Lipschitz bound extends the boundary inequality to a comparison inequality dot B>=-L|B| near B=0, preventing crossing from B>=0 to B<0. Compactness of each finite-time trajectory allows continuation of this argument to T. ∎

The theorem is a sufficient population-floor guarantee, not a necessary survival criterion or an unconditional real-world guarantee. If a_safe>1, this particular certificate is unavailable; extinction does not follow. If beta_H<delta_H, no resource allocation can indefinitely prevent population decline under this demographic law, although finite-time survival can still hold.

With constant demands and supply floors S_j>=S_j,min for **operational** resources,

\[
b_{under}=\min\left\{1,\min_j\frac{S_{j,min}}{d_{Hj}H_{min}}\right\}. \tag{34}
\]

For uncertain demands use upper bounds d_Hj,max. Under (31), E_op>=(1-rho)E_total, so E_total>=E_min, rho<=rho_max<1 give the conservative bound E_op>=(1-rho_max)E_min. This certificate needs no forecast of A or q, but it does need a credible resource lower bound. A power supply that collapses with human industrial loss cannot be assigned a positive floor without justification.

For parameter uncertainty a common sufficient bound is sup_theta delta_H(theta)/[beta_H(theta)b_under(theta)]. It certifies population safety only when all stated hypotheses hold uniformly. This is distinct from the robust non-marginal set below.

### 5.4 Welfare sufficiency is a separate condition

A boundary population certificate does not imply s_H>=s_min at larger H. For a stronger sufficient finite-horizon non-marginal guarantee, let H_up=H(0) exp(max(beta_H-delta_H,0)T). If supplies and demands imply b_H>=b_all>0 for every H<=H_up and feasible state, then a b_all>=s_min together with Proposition 5 ensures both the population floor and resource adequacy throughout [0,T]. This bound may be very conservative, and should not replace the weaker population theorem in reporting.

### 5.5 Safe initial states and numerical alignment sets

For a fixed setting a define

\[
V_a(T)=\{x_0:\min_{0\le t\le T} H(t;x_0,a)\ge H_{min}\}. \tag{35}
\]

A grid of initial (A_0,q_0) at fixed H_0 approximates a slice of this fixed-policy safe set. It is not a computed control viability kernel. For fixed parameters define A_pop={a:min H>=H_min} and A_nm={a:non-marginal survival}. A_num=inf A_pop is meaningful with an empty-set convention (+infinity), but does not imply all larger a are safe. Report the full sampled set, its resolution and any disconnected components.

At fixed state/supply the two-group optimum satisfies s_H(a)=max(s_H(0),a b_H), until its human-only cap. This follows by maximizing the strictly concave utility reduced to the Pareto frontier: truncating the feasible interval below its unconstrained maximizer leaves it unchanged, otherwise the constrained maximum is at the new lower endpoint. This instantaneous monotonicity does not prove monotonicity of entire coupled trajectories, whose industrial production, resource budgets and demands change with alignment.

The phase diagram should distinguish the three outcome classes and separately hatch the population-safety certificate region. Do not label the hatching a guarantee of non-marginal welfare.

## 6. Part IV: uncertainty, structural robustness and information priorities

### 6.1 Evidence categories and scenario distributions

Every input record must contain name, definition, unit, baseline, admissible range, provenance category, reference if any, rationale and uncertainty role. SOURCE means problem-reported or independently verified data; ESTIMATE means a transparent derivation from evidence; ASSUMPTION means an exploratory convention. No numerical demographic or RSI calibration is established in this mathematical draft.

Parameter uncertainty concerns values within a model; structural uncertainty concerns functions and mechanisms; scenario probabilities concern a chosen measure on those choices. Pi_conservative, Pi_central and Pi_aggressive are earlier broad exploratory ranges; Pi_stress_augmented is a later range selected after inspecting outcomes. **None of these experiments is preregistered or confirmatory.** Supports and dependence assumptions must be disclosed. Uniform/log-uniform choices are scenario conventions, not real-world frequencies. Human demographics, resources and technology parameters may be dependent; independent sampling is itself an assumption. The new controlled pilot fixes demographics, supplies, thresholds and initial states and varies only eight RSI parameters; it is also exploratory.

Use reproducible draws theta^(n) and preferably common random numbers across a and structural alternatives. Each draw must satisfy q_0<=q_max, A_0<=A_max, H_ext<H_min, positive denominators and unit constraints. Failed/infeasible simulations form a reported diagnostics category and must not be silently relabeled as survival or dropped from a probability denominator.

### 6.2 Conditional probabilities and sampling intervals

For successful complete experiments under declared Pi and structure F,

\[
\widehat P_k(a\mid\Pi,F)=N^{-1}\sum_{n=1}^N
\mathbf1\{C(\theta^{(n)},a,F)=k\},\quad
k\in\{ext,marg,nm\}. \tag{36}
\]

The partition in (32) implies the sum is exactly one apart from floating-point reporting. Record minimum H, final-window adequacy, q_self crossing and censoring, full replacement feasibility, and human-free counterfactual status separately. A q threshold crossing is not equivalent to actual autonomy.

For iid scenario draws, a pointwise Wilson interval for each probability uses z=1.96 and

\[
\frac{\hat p+z^2/(2N)\ \pm\ z\sqrt{\hat p(1-\hat p)/N+z^2/(4N^2)}}{1+z^2/N}. \tag{37}
\]

These are marginal sampling-error intervals, not simultaneous bands and not intervals for real-world extinction risk. Standard iid binomial intervals are not automatically valid for dependent Latin-hypercube or quasi-Monte Carlo designs. Historical search may use LHS; probability estimation should use iid samples if (37) is reported.

### 6.3 Sensitivity and censoring

Low-cost global screening can use Spearman rank correlations between sampled inputs and Y_1=min H, Y_2=the explicitly coded outcome indicator, Y_3=a_safe, and Y_4=time to industrial threshold. Report ties, sample size and bootstrap uncertainty; resample entire parameter vectors, not individual columns. With correlated inputs these are associations, not isolated causal effects or variance decompositions. A constant output has undefined correlation and must not be assigned zero importance without qualification.

Never replace a censored event time by T and call it an observed time. For Y_4 report crossing probability separately and restrict time correlations to crossings with a selection-bias caveat, or use a dedicated censored-time analysis. A_num screening requires a grid scan over a per draw and storage of disconnected safe sets, rather than unjustified binary search.

Choose the candidate quantity worth measuring only after comparing absolute rank effects and uncertainty across the three scenario measures and the structural alternatives. No winner is known at this stage. A useful decision-oriented extension is EVPI=min_u E L(u,theta)-E[min_u L(u,theta)]>=0, under a stated feasible action set, integrable loss and common information assumptions. It is a later policy analysis, not a numerical result here.

### 6.4 Structural alternatives and robust sets

Use a crossed 2x2 experiment: proportional fairness versus a specified priority rule; bounded versus non-saturating capability growth. Both allocation rules obey the same resource constraints and human floor. One transparent AI-first rule is:

1. Set s_H=l_H and allocate maximal feasible s_A=min(1,min_{j:D_Aj>0}(S_j-D_Hj l_H)/D_Aj).
2. Hold that s_A fixed and allocate maximal feasible s_H=min(1,min_{j:D_Hj>0}(S_j-D_Aj s_A)/D_Hj).
3. Apply the same absent-group and zero-resource conventions.

This deliberately changes allocation ethics while preserving conservation and endpoints. It is a structural stress test, not a second main historical mechanism. The main Parts I–III always use proportional fairness. Optional additional tests include substitutive versus additive industrial capacity, fixed versus protected construction budgeting, and slow versus rapid automation.

Define

\[
\mathcal A_{safe}(\theta,F)=\{a:\text{non-marginal survival under }(\theta,F)\},\quad
\mathcal A_{robust}=\bigcap_{\theta\in\Theta,F\in\mathcal F}\mathcal A_{safe}(\theta,F). \tag{38}
\]

Without a monotonicity theorem keep the set form. Intersection over a finite experiment library is only **empirical robustness over tested cases**, not the full intersection over a continuous uncertainty domain. A finite-grid intersection can have false safe points if trajectories or parameters are undersampled. The analytic population certificate survives both allocation structures because its proof uses the protection floor alone, provided the same supply floors and dynamical assumptions hold; it still does not prove robust non-marginal welfare.

## 7. Numerical contract for the implementation phase

The implementation is in `src/alpha/`; the numerical experiments and tests have been executed, with results in `docs/results.md`. The following contract is retained as the verification checklist for any extension. Calibration remains absent: all numerical future parameters are scenario assumptions.

### 7.1 Required mathematical tests

1. Compare exact single-resource solutions against (8) only in its uncapped regime, and separately test caps.
2. Verify abundant supplies give (1,1); remove zero populations without NaNs.
3. Verify a=0 equivalence; a=1 human-only maximum, including forced s_A=0; and (31)'s construction endpoint.
4. Test genuinely two-binding resources. A dimensionless analytic fixture is per-unit demand matrix [[2,1],[1,2]], populations (1,1), weights (1,1), supplies (1,1): s=(1/3,1/3), lambda=(1,1), and both resources bind. This is a solver fixture, not a scenario parameterization.
5. Test redundant constraints, zero supply, zero-demand groups, very small positive populations, and unit rescaling invariance.
6. Check normalized primal feasibility, stationarity and complementarity against a trusted generic convex optimizer on a separate randomized fixture set; nonunique duals need not match.
7. If regularization is used, compare epsilon=10^-4,10^-6,10^-8,10^-10 on boundary and tiny-population cases; when exact boundary handling is used report epsilon sensitivity as not applicable to the primary solver and validate its limiting interpretation separately.
8. Verify historical resident equilibrium, invasion signs, threshold events and censored outcomes; do not rely solely on plots.
9. Check A>=0, q>0, q<=q_max in bounded models, ell_site A<=L_site, B<=M and c_build B<=R_build throughout trajectories. Verify idle capacity is not removed from the footprint except through the declared decommissioning flows.
10. Construct a case satisfying every assumption of Proposition 5 and verify H>=H_min; test a_safe>1 is reported as uncertified rather than extinct.
11. Check complete outcome partition, deterministic repeatability, and probability sums.
12. Compare solver tolerances, time sampling/event localization and two initial-state scales. Use root events for extinction; sampled minima alone can miss crossings. Refine final-window indicator integration near threshold crossings.

The historical implementation retains fixed-step RK4 with solve_ivp as a comparison. RSI now defaults to adaptive DOP853. Fixed-step RK4 is retained only as a comparison: a targeted audit found its old one-year saved trajectories insufficiently accurate. Ceiling projection and the silent cap on installed hardware have been removed; material invariant-domain violations fail visibly. Zero installed hardware is handled as an invariant absent-group state, without taking log(0). Threshold-event intervals determine the adaptive final-window bad fraction. A 1e-10 satisfaction/relative-population comparison tolerance treats mathematical equality as passing; this is a numerical convention, not a changed welfare standard. See `p0_numerical_audit.csv` for failed old-step comparisons and `docs/p0_acceptance.md` for the selective scope of verification.

### 7.2 Experiments and planned figures

* Figure 1: historical N,M trajectories, extinction threshold and crossing or censorship; separate observed overlap bands from simulated curves.
* Figure 2: map of w_M/w_N versus beta_M/beta_N, color T_rep, distinct censored/incompatible cells, European compatibility contour; additional H0/H1 accepted-set and threshold/initial-ratio sensitivity tables. Remaining parameters fixed for a slice must be disclosed.
* Figure 3: separate axes for H,A,q,zeta in low/moderate/rapid RSI scenarios; parameter values are scenario assumptions.
* Figure 4: AI demanded versus allocated operational energy, human adequacy and each active construction bottleneck; no mixed-unit axes.
* Figure 5: a versus eta outcome phase diagram with a separately labeled population-safety certificate overlay; accompany with initial A,q safe-set slices and a_num grid resolution.
* Figure 6: all three outcome probabilities versus a for each of three scenario measures, with conditional sampling intervals and N.
* Supplementary: rank sensitivity, the crossed structural experiment, threshold/window/horizon comparisons, epsilon/numerical-convergence diagnostics and empirical robust alignment sets.

No range or sample size may be chosen retrospectively merely to force historical compatibility or an extinction-colored phase region. Publish incompatible and censored experiments. A coarse successful pilot should precede the full sampling design.

## 8. Preliminary discussion and limitations

The framework's mathematical contribution is the integration of a common constrained allocation mechanism, explicit hardware and construction limits, industrial substitution, and a resource-floor viability certificate. It is not the invention of KKT theory, competitive exclusion, or forward invariance.

Historical ranges constrain a highly non-identifiable parameter family. Spatial migration, stochastic demographic loss, age composition, disease and assimilation are omitted. Contemporary data-centre statistics cannot calibrate hypothetical RSI systems without a mapping from hardware units to services and a separation of RSI from other computing. Population dynamics omit age structure, health adaptation, migration and policy. Industrial capacity is aggregated; power continuity is prescribed; fixed land partitions omit competing land conversion; resource-induced hardware loss assumes completed decommissioning. The mapping from capability to energy efficiency or bargaining weight is speculative. A safety certificate is conditional on resource floors and feasible physical states, and a population floor alone is not a welfare guarantee.

The original problem also requires at least two human interventions and timing comparisons, a one-page ENOCH letter naming a present-day application and a valuable unknown, summary sheet, references and any required AI-use report. These are outstanding P1/P2 requirements, not satisfied by Parts I–IV. A natural present-day application is competition between data-centre expansion and essential community electricity/land services; it requires separate empirical calibration.

**Results status:** all propositions above are analytic. The numerical compatibility sets, exclusion times, phase diagrams, scenario probabilities, sensitivity rankings and robustness sets have now been computed; see `docs/results.md` and `results/`. They remain conditional on the stated scenario assumptions.

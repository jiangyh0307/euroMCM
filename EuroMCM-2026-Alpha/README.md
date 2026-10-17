# EuroMCM 2026 α — Our Turn

## Overview

**Parts I–VI theory modeling is complete; the remaining work is paper integration and
competition attachments.** The project asks:

> Under what resource-allocation, physical and dynamical conditions can humanity
> avoid extinction and marginalization alongside hypothetical recursive
> self-improving AI?

Historical competition and future RSI scenarios use the **same weighted
proportional-fair resource allocator**. Installed hardware and capability are
separate states; construction energy, operations, manufacturing and facility land
are accounted separately. Alignment is an operational human-resource floor, not a
measure of AI intent.

Authoritative problem: `../2026_Problem_Alpha.pdf` (verified in the current local
workspace; adjust if the GitHub layout places it elsewhere).

## Key Findings

1. **Collapse does not necessarily eliminate recoverability.** In the risk-revised
   100-year pressure background, the tested policies have two different deadlines:

   |Policy|Last sampled preventive start|Last sampled recovery start|Sampled window|
   |---|---:|---:|---:|
   |Resource protection R, `u=0.8`|42.75 yr|57.25 yr|14.5 yr|
   |New-installation cap C, `C/A_max=0.1`|42.50 yr|65.75 yr|23.25 yr|

   “Preventive” means never crossing `H_ext=10^8`; “recovery” allows an earlier
   crossing but requires `H(T)>H_ext` at year 100. These are **last sampled
   successes**, not exact continuous boundaries or general monotonicity theorems.
   Part VI's coarser base scan gives 57.0/65.5 (windows 14.5/23.0); the small
   difference is grid resolution, not a model change.
2. **The window survives four pre-specified parameter checks.** Across base stress,
   faster RSI, higher AI energy intensity and lower energy supply, preventive
   deadlines were roughly **35–43 years**, recovery deadlines were later, and
   sampled windows were about **14.5–15.5 years for R** and **23–25 years for C**.
   Faster RSI / higher AI energy / lower supply move both deadlines earlier.
3. **A first passage is not irreversible extinction.** A trajectory may cross below
   `H_ext` and recover; this is recorded as `recovered_after_extinction=True` and
   must not be called irreversible extinction. Population recovery also does not
   mean social, institutional or welfare recovery.
4. **The reference background is already non-marginal.** Its 25 policy runs stay
   non-marginal and show no human-outcome benefit from R or C. A policy with a real
   physical cost is not justified there. In the pressure background, early R/C avoid
   the first crossing but generally remain marginal; late policies can cross and
   recover.
5. **Historical compatibility is a demonstration, not validation.** The stored
   baseline gives about 2,867 years; 14/650 grid points are European-duration
   compatible. H0 and H1 both have compatible points; the exercise does not identify
   the historical mechanism.

All numerical results are conditional scenario computations. No result is a
real-world extinction probability, empirical RSI calibration or causal historical
claim.

## Model Architecture (Parts I–VI)

|Part|Content|Main current file|
|---|---|---|
|I|Historical two-population competition, censoring, compatibility and non-identifiability|`src/alpha/historical.py`|
|II|RSI population/hardware/capability dynamics, construction/manufacturing/site constraints|`src/alpha/rsi.py`|
|III|Alignment floor, three-level outcomes, conditional population-floor certificate|`src/alpha/alignment.py`, `viability.py`|
|IV|Exploratory UQ, sensitivity, structural robustness|`src/alpha/uncertainty.py`|
|V|Resource protection R, installation cap C, shutdown branches, critical times|`src/alpha/rsi.py`, `risk.py`|
|VI|Four-set robustness of the two critical times; conditional policy synthesis|`docs/part_vi_results.md`|

The shared allocator is `src/alpha/allocation.py`. The population ODE is unchanged
through Parts V–VI:
`H_dot = H(beta_H s_H - delta_H)`. Risk adjudication is separate from the ODE.

## Current Risk Definitions

- `H_ext = 10^8`: effective-extinction first-passage floor.
- `H_min = 2×10^8`: minimum acceptable population and rapid-collapse size floor.
- Rapid collapse: 10-year loss ≥50% **and** `H(t+10)≤H_min`.
- Cumulative collapse: `H(T)≤0.1 H0`.
- Marginal/non-marginal: final-window adequacy, only if no catastrophe.
- Precedence: extinction > rapid collapse > cumulative collapse > marginal > non-marginal.

**Important coincidence:** in the risk-revised pressure background `H0=10^9`, the
90% cumulative threshold equals `0.1 H0 = 10^8 = H_ext`. Cumulative collapse and
effective extinction are therefore the same event in that set. They remain distinct
definitions and can separate in other backgrounds.

**Terminology:** `tau_recover*` is the latest sampled start that achieves
`H(T)>H_ext` **within the specified 100-year horizon and tested policy class**.
It is not a claim that recovery is impossible after that year under every policy.
Likewise, `tau_prevent*` is a tested policy deadline, not a general theorem.

Legacy results with `H_ext=10^6` are retained only for reproducibility and are not
mixed with the current risk-revised results.

## Reproducibility

Tested with Python 3.9.6; Python 3.11+ recommended.

```bash
python3 -m pip install -r requirements.txt
export PYTHONPATH=src
```

**Quick validation (not the full experiment suite):**

```bash
python3 -m pytest -q tests
```

Current result: **77 passed** (58 P0 + 11 Part V policy/shutdown + 8 risk).

**Full selected pipeline** (historical/RSI/alignment/UQ are not all rerun; the
script runs the P0 acceptance checks plus Parts V–VI):

```bash
./run_all.sh
```

`run_all.sh` includes `run_part_v.py`, `run_part_v_risk.py`, PONR scans,
shutdown branches, the 8-vector uncertainty pilot and `run_part_vi_robustness.py`.
It is not a quick command and can take several minutes. The legacy Part V stress
slice is separate:

```bash
python3 experiments/run_part_v_stress.py
```

Original historical/RSI/alignment/UQ figure commands remain available but can
overwrite exploratory outputs and take longer:

```bash
python3 experiments/run_historical.py
python3 experiments/run_rsi.py
python3 experiments/run_alignment.py
python3 experiments/run_uq.py --n 100 --seed 2026 --dt 1.0
```

RSI defaults to adaptive DOP853 with extinction/adequacy threshold events.
`integrator="rk4"` is retained only for comparisons. The current classification
equality tolerance is `1e-10`.

## Results and Data

|Topic|Current result|Location|
|---|---|---|
|Historical baseline|`T_rep≈2867 yr`; 14/650 European-compatible|`results/figures/fig1...`, `fig2...`; `docs/results.md`|
|RSI scenarios|low/moderate non-marginal; rapid/stress marginal or extinct|`results/figures/fig3...`, `fig4...`; `docs/results.md`|
|Risk-revised Part V|reference all non-marginal; pressure extinction at 43 yr; recovery cases|`docs/part_v_risk_results.md`; `part_v_risk_*`|
|Critical times|R 42.75/57.25; C 42.50/65.75 in base pressure|`part_v_ponr_summary.csv`; `part_v_ponr_*`|
|Shutdown|success/failure branch grid, assumed `p_s`|`part_v_shutdown_*`|
|Small UQ pilot|8 RSI vectors, 7 policies|`part_v_uncertainty_*`|
|Part VI robustness|four sets; windows R 14.5–15.5, C 23–25|`docs/part_vi_results.md`; `part_vi_windows.png/pdf`|
|Physical cost proxies|blocked installation, displaced AI energy, construction MWh|`part_v_risk_*`, `part_v_shutdown_*`|

There is **no monetary-cost result** and **no global optimal-control solution**.
The cost columns are physical proxies only.

## Assumptions and Limitations

- Historical compatibility is not causal validation; parameter provenance is in
  `src/alpha/parameters.py` and `results/tables/parameter_table.csv`.
- Selected historical population energy means (2700/2500 kcal/person/day) are
  ASSUMPTION, not measured all-age means.
- All RSI technology, energy, land, manufacturing and capability laws are scenario
  assumptions. Hardware units are not empirically calibrated.
- Power supply is exogenous; the human-free counterfactual does not prove autonomous
  power-plant operation.
- Facility land is a fixed precommitted partition. Shutdown reduces operating
  availability but does not release installed stock or site land.
- Risk thresholds and critical times are policy conventions. Sensitivity to
  `H_ext,H_min,Delta,q,q_total` is still required before final paper claims.
- Numerical verification is selective: 26 targeted cases, 36 stratified checks and
  an interrupted full-library recheck. Some old coarse RK4 trajectories fail current
  precision checks; old results are retained as exploratory.
- No real-world probability, irreversible-extinction theorem, unique optimal policy
  or value-of-information result is claimed.

## Team Handoff

**Frozen model and definitions (read first):**
`docs/mathematical_model.md`, `docs/population_protocol.md`,
`docs/part_v_mathematics.md`.

**Current results (use these in the paper):**
`docs/part_v_risk_results.md`, `docs/part_vi_results.md`, `docs/results.md`,
`docs/p0_acceptance.md`.

**Legacy/archived (do not mix with current claims):**
`docs/part_v_results.md` (`H_ext=1e6`), `docs/archive/`, `paper/archive/`.

**Next priorities:**
1. Check the core mathematical conclusions and explain the mechanisms behind
   the longer C recovery window and the potential welfare cost of strong R.
2. Integrate Parts I–VI into the final paper, with consistent risk definitions.
3. Verify references, compile the LaTeX draft, and prepare the Summary Sheet,
   ENOCH Letter and AI-use report.

Optional extensions (not required for the current theory): full Part V uncertainty
distribution, monetary-cost calibration, global optimal control, spatial migration,
idle-hardware states and a continuous viability kernel.

## Project Organization

|Location|Purpose|
|---|---|
|`src/alpha/allocation.py`|Shared allocator and boundary cases|
|`src/alpha/historical.py`|Historical competition and censoring|
|`src/alpha/rsi.py`|RSI/hardware/human dynamics and policies|
|`src/alpha/risk.py`|Risk-revised outcome hierarchy and paired damage|
|`src/alpha/alignment.py`, `viability.py`|Safety maps and conditional certificate|
|`src/alpha/uncertainty.py`, `scenarios.py`|Exploratory sampling and scenario backgrounds|
|`configs/`|P0 acceptance, risk Part V and Part VI robustness settings|
|`experiments/`|Runnable experiments and verification|
|`results/figures/`, `results/tables/`|Current figures and tables|
|`tests/`|Mathematical, physical, policy and risk regressions|
|`docs/`, `paper/`|Current derivations, results, handoff and archives|

LaTeX compilation is **NOT EXECUTED** (no engine installed). Compile from `paper/`
when an engine is available. The full-library adaptive verification remains
incomplete by the agreed selective-verification scope; this is a documented limit,
not a passed check.

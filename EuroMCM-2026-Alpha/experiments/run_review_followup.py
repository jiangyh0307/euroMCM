"""Post-review sensitivity checks; assumptions, not empirical calibration."""
from pathlib import Path
from dataclasses import replace, asdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import json, os, time
os.environ.setdefault('MPLCONFIGDIR', '/tmp/euromcm-mpl')
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import numpy as np
import pandas as pd
from alpha.scenarios import scenario_collapse_stress, base_rsi
from alpha.rsi import simulate_rsi, Intervention
from alpha.risk import assess_risk, RiskThresholds
ROOT=Path(__file__).resolve().parents[1]
TABLES=ROOT/'results/tables'
FIGS=ROOT/'results/figures'
SETS={
 'base':{}, 'threshold_low':{'H_ext':5e7}, 'threshold_high':{'H_ext':1.5e8},
 'horizon_50':{'T':50.}, 'horizon_150':{'T':150.},
 'mortality_002':{'deprivation_mortality':.02},
 'mortality_006':{'deprivation_mortality':.06},
 'mortality_012':{'deprivation_mortality':.12}}

def compute(task):
 name,kind,tau,overrides=task
 p=replace(scenario_collapse_stress(),**overrides)
 if kind=='no_ai': p=replace(p,A0=0.,rho=0.)
 pi=Intervention(kind={'R':'protect','C':'cap'}.get(kind,'none'),tau=tau,u_bar=.8,cap_fraction=.1)
 sim=simulate_rsi(p,intervention=pi,terminate_on_extinction=False,max_step=.5)
 th=RiskThresholds(H_ext=p.H_ext,H_min=p.H_min)
 r=assess_risk(sim.t,sim.H,sim.s_H,p.H0,th,p_bad=sim.p_bad_final_window,extinction_event_time=sim.extinction_time)
 return dict(set=name,policy=kind,tau=tau,T=p.T,H_ext=p.H_ext,kappa=p.deprivation_mortality,
  prevent_success=not r.extinction,recover_success=not r.terminal_extinction,
  extinction_time=r.extinction_time,final_H=sim.H[-1],min_sample_H=sim.min_H,
  final_s_H=sim.s_H[-1],p_bad=r.final_window_bad_fraction,outcome=r.outcome,
  H_min=p.H_min,delta_years=th.delta_years,q_rapid=th.q_rapid,q_total=th.q_total)

def execute(tasks):
 rows=[]
 with ProcessPoolExecutor(max_workers=4) as pool:
  jobs={pool.submit(compute,t):t for t in tasks}
  for i,f in enumerate(as_completed(jobs),1):
   rows.append(f.result())
   if i%25==0 or i==len(tasks):print(f'{i}/{len(tasks)} completed',flush=True)
 return rows

def main():
 tasks=[]
 for name,ov in SETS.items():
  T=ov.get('T',100.)
  for kind in ['none','no_ai']:tasks.append((name,kind,0.,ov))
  for kind in ['R','C']:
   for tau in np.arange(0,min(T,125.)+.01,5.):tasks.append((name,kind,float(tau),ov))
 rows=execute(tasks)
 pd.DataFrame(rows).to_csv(TABLES/'review_sensitivity_coarse.csv',index=False)
 # Refine every observed success/failure transition; no binary search or monotonicity assumption.
 refine=set()
 df=pd.DataFrame(rows)
 for (name,kind),sub in df[df.policy.isin(['R','C'])].groupby(['set','policy']):
  sub=sub.sort_values('tau')
  for col in ['prevent_success','recover_success']:
   vals=list(sub[['tau',col]].itertuples(index=False,name=None))
   for (a,x),(b,y) in zip(vals[:-1],vals[1:]):
    if x!=y:
     for tau in np.arange(a+.5,b,.5):refine.add((name,kind,float(tau)))
 rows+=execute([(n,k,t,SETS[n]) for n,k,t in sorted(refine)])
 df=pd.DataFrame(rows).sort_values(['set','policy','tau'])
 df.to_csv(TABLES/'review_sensitivity_runs.csv',index=False)
 summary=[]
 for (name,kind),s in df[df.policy.isin(['R','C'])].groupby(['set','policy']):
  r=dict(set=name,policy=kind)
  for col,label in [('prevent_success','prevent'),('recover_success','recover')]:
   ok=s[s[col]];bad=s[~s[col]]
   last=float(ok.tau.max()) if len(ok) else None
   later=bad[bad.tau>last] if last is not None else bad
   r[label+'_last_success']=last
   r[label+'_next_failure']=float(later.tau.min()) if len(later) else None
   r[label+'_right_censored']=bool(last is not None and last==s.tau.max())
   r[label+'_contiguous_sample_success']=bool(len(ok)==0 or len(bad)==0 or ok.tau.max()<bad.tau.min())
  r['window']=None if any(r[x] is None for x in ['prevent_last_success','recover_last_success']) else r['recover_last_success']-r['prevent_last_success']
  summary.append(r)
 pd.DataFrame(summary).to_csv(TABLES/'review_sensitivity_summary.csv',index=False)
 # Mechanism trajectories: matched pressure cases and reference controls.
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,axs=plt.subplots(2,2,figsize=(11,8))
 mechanisms=[]
 for label,p,pi in [
  ('none',scenario_collapse_stress(),Intervention()),
  ('R early',scenario_collapse_stress(),Intervention(kind='protect',u_bar=.8)),
  ('C early',scenario_collapse_stress(),Intervention(kind='cap',cap_fraction=.1)),
  ('R late',scenario_collapse_stress(),Intervention(kind='protect',u_bar=.8,tau=50)),
  ('C late',scenario_collapse_stress(),Intervention(kind='cap',cap_fraction=.1,tau=50))]:
  sim=simulate_rsi(p,intervention=pi,terminate_on_extinction=False)
  for ax,y in zip(axs.flat,[sim.H,sim.s_H,sim.A,sim.q]):ax.plot(sim.t,y,label=label)
  rows_m=pd.DataFrame(dict(policy=label,t=sim.t,H=sim.H,s_H=sim.s_H,A=sim.A,q=sim.q,
    human_energy=sim.E_human_allocated,AI_energy=sim.E_AI_allocated,
    B=sim.B,B_before=sim.B_before_policy,E_op=sim.E_op,R_build=sim.R_build,
    energy_human_cap=sim.E_op/(p.e_H*sim.H),land_human_cap=p.L_service/(p.ell_H*sim.H)))
  mechanisms.append(rows_m)
 for ax,title in zip(axs.flat,['Human population','Human adequacy','Installed hardware','Capability per unit']):
  ax.set_title(title);ax.set_xlabel('Years');ax.grid(alpha=.2)
 axs[0,0].set_yscale('log');axs[0,0].axhline(1e8,color='k',ls=':');axs[0,1].axhline(.8,color='k',ls=':')
 axs[0,0].legend(fontsize=8);fig.tight_layout();fig.savefig(FIGS/'review_policy_mechanisms.png',dpi=160)
 pd.concat(mechanisms).to_csv(TABLES/'review_policy_mechanisms.csv',index=False)
 manifest={'sets':SETS,'policies':{'R':{'u':.8},'C':{'cap_fraction':.1}},'coarse_tau_step':5.,'transition_refinement_step':.5,
 'mortality_law':'delta_eff = delta_H + kappa * max(0, 1-s_H/0.8)',
 'limitations':'Post-review exploratory design; uncalibrated kappa; finite grid can miss disconnected success islands; horizon/right censoring explicit. Baseline population law retained at kappa=0.',
 'n_runs':len(df),'full_state_baseline':asdict(scenario_collapse_stress())}
 (TABLES/'review_sensitivity_manifest.json').write_text(json.dumps(manifest,indent=2))
 print(pd.DataFrame(summary).to_string(index=False),flush=True)
if __name__=='__main__':main()

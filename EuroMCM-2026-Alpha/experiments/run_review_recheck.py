from pathlib import Path
from dataclasses import replace
import numpy as np
import pandas as pd
from alpha.rsi import simulate_rsi,Intervention
from alpha.scenarios import scenario_collapse_stress
from alpha.risk import assess_risk,RiskThresholds
root=Path(__file__).resolve().parents[1]
rows=[]
for kind,taus in [('protect',[42.75,43.,57.25,57.5]),('cap',[42.5,42.75,65.75,66.])]:
 for tau in taus:
  for precision in ['default','tight']:
   p=replace(scenario_collapse_stress(),dt=.1 if precision=='tight' else .5)
   sim=simulate_rsi(p,intervention=Intervention(kind=kind,tau=tau,u_bar=.8,cap_fraction=.1),terminate_on_extinction=False,rtol=1e-10 if precision=='tight' else 1e-8,atol=1e-12 if precision=='tight' else 1e-10,max_step=.1 if precision=='tight' else .25)
   rows.append(dict(policy=kind,tau=tau,precision=precision,extinction_time=sim.extinction_time,prevent=not np.isfinite(sim.extinction_time),recover=bool(sim.H[-1]>p.H_ext),final_H=sim.H[-1],min_sample_H=sim.min_H))
df=pd.DataFrame(rows);df.to_csv(root/'results/tables/review_boundary_recheck.csv',index=False)
print(df.to_string(index=False),flush=True)
# Normative risk sensitivity on unchanged trajectories; adequacy p_bad is dense-event evaluated.
rows=[]
for kind,tau,u in [('none',0,0),('protect',0,.8),('protect',50,.8),('cap',0,0),('cap',50,0)]:
 for label,changes in [('base',{}),('Hmin_low',{'H_min':1.5e8}),('Hmin_high',{'H_min':4e8}),('adequacy_low',{'s_min':.6}),('adequacy_high',{'s_min':.9})]:
  p=replace(scenario_collapse_stress(),**changes)
  sim=simulate_rsi(p,intervention=Intervention(kind=kind,tau=tau,u_bar=u,cap_fraction=.1),terminate_on_extinction=False)
  for delta,q,qt in [(10,.5,.9),(5,.5,.9),(20,.5,.9),(10,.3,.9),(10,.7,.9),(10,.5,.8),(10,.5,.95)]:
   th=RiskThresholds(H_ext=p.H_ext,H_min=p.H_min,s_min=p.s_min,delta_years=delta,q_rapid=q,q_total=qt)
   r=assess_risk(sim.t,sim.H,sim.s_H,p.H0,th,p_bad=sim.p_bad_final_window,extinction_event_time=sim.extinction_time)
   rows.append(dict(policy=kind,tau=tau,setting=label,H_min=p.H_min,s_min=p.s_min,Delta=delta,q_rapid=q,q_total=qt,outcome=r.outcome,p_bad=r.final_window_bad_fraction,rapid=r.rapid_collapse,cumulative=r.cumulative_collapse))
pd.DataFrame(rows).to_csv(root/'results/tables/review_risk_conventions.csv',index=False)
print('risk-convention rows:',len(rows),flush=True)

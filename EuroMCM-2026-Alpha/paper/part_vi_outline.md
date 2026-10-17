# Part VI writing outline — robustness and conditional policy advice

Source: `../docs/part_vi_results.md`; tables `../results/tables/part_vi_robustness_*`.

1. Purpose: no new model; test whether Part V critical-time findings survive a small
   set of pre-specified parameter changes, then synthesize physical costs and policy
   implications.
2. Four pre-specified sets: base stress, fast RSI (`eta=1`), high AI energy
   (`e0=20000`), low energy supply (`E_total=8e9`). R `u=0.8`, C `C/A_max=0.1`;
   2-year coarse grid with 0.5-year local refinement.
3. Results: preventive deadline roughly 35–43 years; recovery deadline later;
   R window about 14.5–15.5 years, C about 23–25 years. Faster/high-energy/lower-supply
   backgrounds move deadlines earlier. Success sets contiguous on tested ranges only;
   no global monotonicity theorem.
4. Cost synthesis: physical proxies only; R can displace large AI operating energy
   with small welfare gain at a land bottleneck; C blocks installation. No monetary
   ranking. No-AI is marginal in all four pressure sets; AI no-intervention is extinct.
5. Conditional policy advice: distinguish prevent vs recover; no unique Point of No
   Return; C has larger recovery window but not uniformly earlier prevention; monitor
   RSI growth, AI energy intensity, energy supply and human resource floor.
6. Limitations: four representative scenarios, finite grid/policy class, assumed
   shutdown p_s, no global optimal control, no real-world probabilities, no monetary costs.
7. This closes theory modeling. Remaining: integrate Parts I–VI into the final paper,
   Summary Sheet, ENOCH letter, references and AI-use report.

# 已归档的 v2 交接记录：当前结论见 docs/p0_acceptance.md

本文保留历史记录，其中“预设定”等措辞、测试数和验证范围已被当前验收文档替代。

# 交接说明（v1，已实现并运行）

## 1. 当前状态

Parts I–IV 第一版已经完成：统一资源分配器、历史相容性分析、RSI 三维动力系统、Alignment/Viability、Monte Carlo 与结构鲁棒性均已实现并实际运行。仓库包含 11 张图（主图 6 张、补充图 5 张）、参数来源表、单元测试和英文数学/论文草稿。

**没有**声称历史因果验证，也**没有**把情景概率说成现实灭绝概率。所有 RSI 参数都是 ASSUMPTION/ESTIMATE，不是实测。

## 2. 先读什么

1. `README.md`：项目结构、安装、复现命令、结果摘要、限制。
2. `docs/mathematical_model.md`：统一模型、KKT、五个命题与证明、数值验证合同。
3. `docs/results.md`：实际运行得到的数字、图表索引。
4. `docs/assumptions.md` / `docs/limitations.md`：参数来源与不能说的话。
5. `src/alpha/parameters.py` / `scenarios.py`：可执行参数与情景定义。

## 3. 运行

```bash
python3 -m pip install -r requirements.txt
./run_all.sh
```

或单独运行：

```bash
export PYTHONPATH=src
python3 -m pytest -q tests
python3 experiments/run_historical.py
python3 experiments/run_rsi.py
python3 experiments/run_alignment.py
python3 experiments/run_uq.py --n 100 --seed 2026 --dt 1.0
```

当前测试结果：41 passed。UQ 的 N=100 运行需要数分钟；快速试点用 `--n 30`。

## 4. 必须保留的数学/工程约定

1. 历史与未来共用同一个 Weighted Proportional Fairness 算子。
2. 接口接收 **per-unit** demands 和 weights，内部乘人口；不要重复乘。
3. `a=1` 使用 endpoint-consistent construction budget：

   ```text
   b_H_tot = min(1, E_total/(e_H H), L_service/(ell_H H))
   R_build = min(rho E_total, [E_total - a b_H_tot e_H H]_+)
   E_op = E_total - R_build
   ```

   分配器仍用 `s_H >= a b_H`，其中 `b_H` 基于 `E_op`。固定比例版本只能作为结构比较。
4. 三状态模型的硬件损失项解释为 **完成物理拆除的退役流量**；仅停机不释放占地。P1 应增加 idle-but-unremoved 状态。
5. 运营能源与建设能源不得重复使用同一份 MWh；实际建设能源 `c_build B <= R_build`，实际运营 `s_H e_H H + s_A e_A A <= E_op`。
6. 无阈值穿越记右删失；不要把积分终点当灭绝时间。
7. 安全证书 `a_safe` 只是人口下界的充分条件，不是福利保证，也不是现实绝对安全。
8. 数值安全集合未证明单调；不要用二分法声称唯一临界 Alignment。
9. 非光滑 min/active-set 切换使用固定步 RK4；换积分器后必须做 dt 收敛检查。
10. 任何新参数必须标注 SOURCE/ESTIMATE/ASSUMPTION、单位、范围、理由。

## 5. 结果边界

- 历史基线 `T_rep=2867.46 yr`，在 2600–5400 内；650 格扫描中 14 格（2.15%）欧洲相容，30 格（4.62%）区域相容，325 格删失。H0 与 H1 都相容，不能区分。
- Stress 情景 `a_safe=0.6`，数值人口下界阈值 `a_num_pop=0.4`；证书保守。Stress 相图没有 non-marginal，只有 extinction/marginal。
- UQ N=100（预设的三组措施）：conservative 全 marginal；central 98% marginal、2% non-marginal；broad aggressive 在 `a=0` 灭绝 2% [0.6%,7.0%]，`a>=0.5` 为 0，non-marginal 3–4%。
- 事后构造的 `stress_augmented` 探索措施：`a=0` 灭绝 0.42 [0.33,0.52]，`a=1` non-marginal 0.19 [0.13,0.28]。该措施不是预注册比较，不能当作预测。
- 结构鲁棒性：预设 aggressive 库在 `a>=0.2` 达到 80/80 人口下界安全（robust set `{0.2,0.4,0.6,0.8,1.0}`）；stress-augmented 探索库在 `a>=0.6` 达到 80/80（robust set `{0.6,0.8,1.0}`）。两库 robust non-marginal 集合均为空。
- 受控 2×2：baseline human + stress AI 为 marginal（min H=3.57e9）；fast human + baseline AI 为 marginal（min H=1.00e8）；只有 fast human + stress AI 达到灭绝。
- 有限时域 screening：基线 `H(t)>=H(0)e^{-0.01t}`，100 年下界约 2.95e9 > H_ext=1e6，因此基线 demography 下 100 年内不可能灭绝。
- 可靠性修订：修复了极小人口分配器错误；自适应积分器此前卡顿部分由该错误造成，修复后与固定步 RK4 一致。预设措施与事后 stress-augmented 措施已分开。

## 6. 后续任务

P1：

- 核验原题引用文献；改进历史参数校准与空间迁徙。
- 用更好的硬件、电力、土地数据替换 RSI 情景参数；增加 idle capacity、供应链、电网连续性。
- 实现 Part V：至少两种干预（computing cap、fallible shutdown）及实施时机、失败概率、成本、生存结果比较。
- Viability kernel、稳健控制、bifurcation、EVPI。

P2：

- 完整比赛论文、one-page summary、ENOCH letter、参考文献核验、AI 使用报告、最终排版。

## 7. 不要做的事

- 不要把历史拟合称为因果验证。
- 不要把情景概率称为现实人类灭绝概率。
- 不要把 `a_safe` 称为现实安全保证。
- 不要把工业自给阈值直接称为分岔点。
- 不要为了得到好看的相图而回溯性挑选参数范围；`aggressive` 是预设定 broad measure，`stress_augmented` 是事后探索措施，两者不能混用，也都不是预测。

# EuroMCM：数学贡献、Introduction 主线与论文结构

2026-10-18；依据当前实现、84 项测试及最新核查结果制定。本文件是论文整合蓝图；尚未替换正式 LaTeX 正文。

## 一、论文定位

推荐题目：**Survival, Marginalization, and Recovery: A Resource-Constrained Model of Human–RSI Coexistence**。

全文中心问题：在共同的物理资源约束下，哪些条件能保障人口安全，人口安全与资源福利为何分离，以及人类干预分别何时还能预防穿越和实现期末恢复？

数学主线：**受约束分配 → 耦合动力系统 → 可证明的充分/必要条件 → 有限政策类的时机比较 → 结构与参数敏感性**。

Introduction 中应强调“构建、推导、证明、界定、比较”，并紧接着写清每项结果回答什么问题。成熟方法是工具，针对本题构造的连接与得到的机制性结论是贡献。未完成系统文献查新，不使用 first、novel theory、previously unexplored 等优先权措辞。

## 二、最值得突出的数学优势

### A. 分配层是明确的凸优化问题，动态反馈不是任意指定

统一采用

\[
\max_s\sum_i w_iP_i\log s_i,\qquad
\sum_i d_{ij}P_i s_i\le S_j,\quad \ell_i\le s_i\le1.
\]

在正的、非退化有效可行域上，目标严格凹、约束线性，因此有效正权重坐标上的最优满足率唯一；强制零、缺席群体等边界另行定义。单资源、无上限激活、无保护下界激活时，有闭式解

\[
s_i=\frac{S w_i}{d_i\sum_k w_kP_k}.
\]

这给历史人口与未来 RSI 一个共同的“供给—分配—满足率—增长”机制；各资源分别守恒，能量与土地不直接相加。KKT 条件和活跃约束还能识别瓶颈，并为闭式特例、数值解和实现检查提供相互核对。

优势：结构可解释、分配可检验，能从参数差异推导竞争优势；不是仅将两条指数曲线放在一起。

边界：严格凹性、KKT 和比例公平属于已有理论；我们贡献其具体耦合、端点一致的建设/运营预算和对本题结果的推导。历史检验及共同机制本身也是原题要求，不能只用“我们做了”作为创新。

### B. 有物理可行域与比较界，先分析可不可能，再模拟发生什么

以 H 为人口、A 为安装硬件、q 为单位硬件能力。各建设流量约束均以硬件单位/年计量；建设能耗与运营能耗分开，安装存量与运营可用量分开。

在参数非负、物理上限固定且分配耦合 ODE 适定的条件下，

\[
\mathcal D=\{H\ge0,\ 0\le A\le A_{\max},\ 0<q\le q_{\max}\}
\]

前向不变：H 的乘性方程保持正性；A=0 时建设/变化为零，A=A_max 时建设流为零且导数非正；q=q_max 时导数为零。此结论是饱和主模型的性质，不覆盖移除 q 饱和项后的同一 q 上界。

主人口方程给出

\[
H_0e^{-\delta_Ht}\le H(t)\le H_0e^{(\beta_H-\delta_H)t}.
\]

因此若 \(H_0e^{-\delta_HT}>H_{ext}\)，无论 AI 参数如何，在该背景内都不能出现有效灭绝；不能把这类背景的“无灭绝”当成政策成功。阈值穿越仍可发生，但确定性正解不在有限时间到达生物学零。

额外死亡率 κ>0 时，下界需换成 \(H_0e^{-(\delta_H+\kappa)t}\)，上界不变。全文须区分主模型与替代模型。

优势：能排除不可能结果，避免用模拟数量掩盖模型结构；物理可行性来自方程边界，而不是事后截断。

### C. 从资源保护推导人口安全的充分条件，并将人口与福利分开

若分配器强制 \(s_H\ge a b_H\)，且在安全边界 H=H_min 有统一资源下界 \(b_H\ge\underline b>0\)，则在适定性、局部正则性、其余物理约束不变等条件下，

\[
a\ge a_{safe}:=\frac{\delta_H}{\beta_H\underline b}\le1
\quad\Longrightarrow\quad H(t)\ge H_{min}.
\]

证明只需检查边界：\(\dot H\ge H_{min}(\beta_Ha\underline b-\delta_H)\ge0\)，再用前向不变性。若 a_safe>1，只能说该证书不可用；它不是灭绝证明，也不是最小必要 alignment。

该证书不需要精确预报每条 A、q 路径，但需要可信的统一资源下界；外生供电假设不能省略。a=1 的保护相对于固定的人类可用土地分区，不能写成归还所有历史占地。

人口安全不蕴含 \(s_H\ge s_{min}\)。主模型正人口稳态必须满足 \(s_H=\delta_H/\beta_H\)。压力背景该值为 0.6，低于福利阈值 0.8，直接解释了“人口保住并增长，仍然边缘化”。这是必要的稳态平衡条件，不单凭此式宣称所有轨迹都收敛。

额外死亡模型的零增长满足率为

\[
s_* =\begin{cases}
\delta_H/\beta_H,&\delta_H/\beta_H\ge s_d,\\
(\delta_H+\kappa)/(\beta_H+\kappa/s_d),&\delta_H/\beta_H<s_d,
\end{cases}\qquad s_d=0.8.
\]

相应的充分保护条件为 a≥s_*/b_under。它已同步到安全证书实现。

优势：将“保护需要多强”变成可证明的条件，将“活下来”和“过得够好”变成不同数学命题。

### D. 政策效果有精确恒等式，能够解释路径差异

同一 H0、β、δ、κ=0 下，两条政策路径满足

\[
\log\frac{H^\pi(t)}{H^0(t)}
=\beta_H\int_0^t[s_H^\pi(u)-s_H^0(u)]\,du.
\]

该恒等式无需线性化，也不要求 A、q 的轨迹相同。它解释了人口收益取决于累计满足率差，而不是某一个终点的满足率；更高期末人口不自动意味着更少早期损失或更高最终福利。

κ>0 时不能照搬旧式：还需减去两条路径的累计额外死亡率差，或定义净增长函数 g(s)=βs−δ−κ(1−s/s_d)_+ 后对 g 的差积分。

能力—能源关系也有精确恒等式：

\[
\frac{d}{dt}\log(e_0q^{-\xi}A)
=\frac{\dot A}{A}-\xi\frac{\dot q}{q}.
\]

它比较硬件扩张与效率改善的相对速度；需求增长的判据是右侧为正。实际消耗还乘满足率 s_A，不得混称。

优势：结果有机制解释，不只报告曲线和相关系数。恒等式本身是直接微积分结果，不包装为新的微积分理论。

### E. 用两个严格定义的成功集合研究干预时机

对固定政策族、固定强度、相同背景与给定 T，定义

\[
\mathcal T_{prevent}=\{\tau:\min_{0\le t\le T}H^\tau(t)>H_{ext}\},\qquad
\mathcal T_{recover}=\{\tau:H^\tau(T)>H_{ext}\}.
\]

显然 \(\mathcal T_{prevent}\subseteq\mathcal T_{recover}\)，因此两集合非空时，\(\sup\mathcal T_{prevent}\le\sup\mathcal T_{recover}\)。集合包含本身不是深刻创新；本研究的贡献是对两种物理实现不同的政策，计算严格分离的采样窗口、解释其机制，并检验参数/结构变化。

原背景细网格：R 的最后成功预防/恢复启动约 42.75/57.25 年，C 约 42.50/65.75 年。这些是有限网格上界限的估计，不是连续精确临界值，也不意味着实际成功集随 τ 单调。数值结果没有证明唯一或不可逆的 Point of No Return。

补充：本次写作梳理可直接推出一个**政策无关的必要恢复界**，适用于仅改变资源分配/硬件、而不改变人口基本增长参数的政策。设政策 τ 前与无干预路径 H^0 一致，则

\[
H^\pi(T)\le H^0(\tau)e^{(\beta_H-\delta_H)(T-\tau)}=:U(\tau).
\]

证明：τ 时人口连续且等于 H^0(τ)，之后 s_H≤1，因此积分 \(\dot H/H\le\beta_H-\delta_H\)。κ≥0 的短缺额外死亡模型也满足该上界。

若 U(τ)≤H_ext，则即使 τ 后人类资源立即完全满足，也无法在 T 前恢复到阈值以上。该条件是不可能性判据；U(τ)>H_ext 仅表示尚未排除恢复，并非存在可行政策的充分证明。

主模型中

\[
\frac{d}{d\tau}\log U(\tau)=\beta_H(s_H^0(\tau)-1)\le0.
\]

因此这个理想恢复包络随延迟非增；这不证明具体 R/C 轨迹或成功集合单调。κ>0 时右侧再减非负的基线额外死亡项，结论仍成立。

这条简单推论可以与 C 的存量退役可行性及延迟保护证书一起放在干预章，形成“解析上界—可行政策—数值窗口”的逻辑。它是现有方程的直接推论，不声称文献首创。按保存的无干预轨迹插值，原背景的理想恢复上界约在 τ=65.91 年触及阈值；该数字仅为写作诊断，未经独立根定位精度核查，不作为新主结果或最优性结论。

## 三、Introduction 的三项贡献表述

不要把上述五类数学性质列成五项全新的理论。建议收敛为三项贡献：

1. **统一的约束分配—动力系统框架。** 将严格凹的资源分配问题与人口、安装硬件和单位硬件能力耦合，保持单位、预算和物理可行域一致；历史实例检验同一分配机制的量级兼容性。
2. **可解释的安全条件与人口—福利分离。** 推导人口比较界、资源保护的充分安全条件和精确政策比较恒等式，说明哪些无灭绝结果由结构决定，以及人口恢复为何不保证资源充足。
3. **有解析边界支持的政策时机比较。** 区分预防与期末恢复成功集合，给出理想恢复上界，并对 R/C 的有限政策类计算两类启动期限；用阈值、期限和短缺死亡机制检查窗口依赖哪些假设。

建议英文 contribution 段落（工作稿，可用于正式 Introduction；应结合最终正文核对）：

> This paper makes three contributions. First, we couple a common constrained resource-allocation problem to population, installed-hardware and capability dynamics, with separate construction and operating budgets and an invariant physical state domain. Second, we derive population comparison bounds, a sufficient resource-protection condition and exact policy-comparison identities. These results distinguish population safety from resource adequacy and explain why demographic recovery can coexist with marginalization. Third, we formulate intervention timing through separate prevention and terminal-recovery success sets. An ideal recovery envelope supplies a necessary feasibility bound, while policy scans quantify the distinct timing windows of resource protection and installation caps. Sensitivity checks over thresholds, observation horizons and deprivation-induced mortality identify which conclusions persist and which depend on modeling choices.

段落中的 invariant、sufficient、necessary 都要在正文紧邻列出适用条件。Introduction 不能把条件安全证书写成现实保证，不能把必要恢复界写成可实现的最优控制解。

## 四、Introduction 的段落顺序

1. **问题与决策目标。** 在 RSI 条件存在且资源有限的前提下，什么决定人口存续、边缘化与干预时机？不讨论 RSI 一定会出现。
2. **相关方法与本题需要连接的环节。** 比例公平已有成熟理论；AI 增长研究也已有投入瓶颈讨论；人机资源竞争已有模拟研究。本文需要将分配、物理扩张、人口安全与干预时机连接起来，而不是声称此前无人研究竞争。
3. **研究问题。** 哪些物理/分配条件足以维持人口？为何活下来仍可能边缘化？避免第一次穿越与实现期末恢复是否具有不同的干预期限？
4. **方法与数学性质。** 用一句机制链说明优化层到动力层，再概述比较界、安全证书与政策时机集合；历史结果称 compatibility，不作为未来 RSI 的校准证据。
5. **三项贡献与主要发现。** 使用上节贡献段落；结果预告强调人口/福利分离及不同政策的两类期限，不把某个年份写成普遍常数。
6. **正文路线。** 用两三句交代模型、解析性质、政策、敏感性与结论。

Introduction 目标约 600–750 英文词、1.5 页；不要列出全部状态方程、77/84 项测试或实验脚本历史。

## 五、完整论文结构及页数预算

按原题，Summary、目录、正文、信件和参考文献合计不超过 25 页；AI 使用报告不计入该上限。目标先做到约 23 页，留 2 页排版/必要证明余量。附录若放入提交 PDF，也占限额。

|部分|建议英文标题|必须回答的问题/核心数学内容|目标页数|
|---|---|---|---:|
|摘要页|Summary Sheet|三项贡献、主要条件、政策窗口、可信度边界|1|
|目录|Contents|便于原题各要求定位|1|
|1|Introduction|问题、相关方法、三项贡献、正文路线|1.5|
|2|Assumptions, Evidence and Notation|证据/推导/假设分类；量纲；主背景与压力背景；阈值约定|1|
|3|A Common Constrained Allocation Mechanism|分配优化、KKT、单资源闭式解；保护端点与预算一致性|2|
|4|Historical Compatibility and Identifiability|竞争指标、入侵条件、局部稳定性择要；兼容集与尺度不识别|2|
|5|Resource-Constrained RSI Dynamics|H/A/q 方程；建设/能源/制造/土地瓶颈；正性、不变域；效率—扩张条件；条件工业自维持阈值|3|
|6|Human Safety and Resource Adequacy|人口比较界、安全证书、人口与福利分离；alignment 扫描与条件情景频率|2|
|7|Interventions and Two Timing Objectives|R/C 定义；硬件 cap 的存量连续性和不变性；比较恒等式、延迟保护条件、必要恢复界；两类启动集合与结果；可失败关机作为短扩展|3|
|8|Sensitivity, Structural Checks and Numerical Verification|技术/能源四情景；新八设定扫描；额外死亡、期限和阈值；连续事件与精度核查；条件频率不等于现实概率|2.5|
|9|Discussion and Model Evaluation|优势、限制、条件政策含义；外生供电、固定土地、非校准人口与 RSI 参数|1|
|10|Conclusions|逐一回答核心问题，不引入新结果|0.5|
|信件|Letter to ENOCH|结论、可信度、值得测量的未知量、当下应用|1|
|参考文献|References|按实际引用精简，原始来源核验|1.5|
|限额外|Report on Use of AI Tools|遵循赛事 AI 政策，准确说明用途|另计|

正文不按 P0/P1/P2 工作阶段写，也不把 Parts I–VI 分别堆成六份独立报告；保留一张原题要求与章节对应表，确保读者能找到每项回答。

建议主文保留 3–4 个带简短证明的核心结果：分配闭式解/物理不变域可择一简化，人口安全证书，政策比较恒等式与必要恢复上界。历史入侵和工业阈值以短推论表达。长 KKT 分支推导、冗长证明和数值细节压缩到限额内附录；主文必须自足。

建议 6–7 组主图：模型机制图；历史兼容图；H/A/q 与物理瓶颈图；alignment 安全/福利图；两种期限与政策机制图；敏感性窗口图。参数表、定理假设表和政策对照表比大量蒙特卡洛曲线更优先。

## 六、论证与证据等级

|结论|可用措辞|不可用措辞|
|---|---|---|
|正域严格凹与 KKT、比较界、安全条件、恒等式|derive/prove，在明确假设下|普遍现实安全保证|
|历史参数与共存时间兼容|compatible / order-of-magnitude check|历史因果验证、证明同一未来必然发生|
|R/C 临界启动网格与恢复窗口|observed over tested grids / conditional numerical result|全局最优时机、实际成功集必然单调|
|四组技术背景与新八组设定|persists across tested cases|全不确定域鲁棒、现实灭绝概率|
|必要恢复包络|upper bound / impossibility screen|一定存在可行恢复政策、C 全球最优|
|84 项测试与局部精度复算|implementation/numerical validation evidence|数学证明或创新本身|

## 七、相关文献定位（初步、非穷尽查新）

- Kelly (1997), *Charging and rate control for elastic traffic*：比例公平与网络约束优化是方法基础。[作者页面](https://www.statslab.cam.ac.uk/~fpk1/elastic.html)
- Aghion, Jones & Jones (2017/2019), *Artificial Intelligence and Economic Growth*：已有研究用模型讨论 AI 自动化、增长与必要投入瓶颈；本文焦点是物理资源约束下的人口安全与福利。[NBER](https://www.nber.org/papers/w23928)
- Chen et al. (2025), *Survival Games: Human-LLM Strategic Showdowns under Severe Resource Scarcity*：已有研究在人机共存的稀缺资源模拟中评价 LLM 行为；本文研究假想 RSI 的聚合物理动力系统，不对现有 LLM 进行行为测试。[原始预印本](https://arxiv.org/abs/2505.17937)

以上来源用于界定方法与问题位置，不足以支持“首个模型”的优先权断言。正式成稿仍需核实历史原文、数据来源及前向不变性引用。

# 项目总入口：从这里开始

本次模型核查、敏感性实验、数学贡献提纲和论文初稿已统一放入这个 GitHub 本地项目目录。以后以此处的版本继续工作。

## 论文与 Overleaf

- **主要编辑文件：[paper/main.tex](paper/main.tex)**。这是完整英文论文的唯一主稿。
- **上传 Overleaf：[paper/EuroMCM_Overleaf.zip](paper/EuroMCM_Overleaf.zip)**。包含主稿与全部引用图件，可直接上传。
- [paper/README_zh.md](paper/README_zh.md)：编译、队号填写和提交前检查说明。
- [paper/introduction_and_structure_zh.md](paper/introduction_and_structure_zh.md)：数学贡献、Introduction 主线和论文章节安排。
- [paper/RESULT_SOURCES.md](paper/RESULT_SOURCES.md)：论文数值与实验结果的对应关系。
- `paper/figures/`：论文实际引用的图件。
- `paper/templates/`：你提供的官方参考模板，Word 和 LaTeX 均已保存。
- `paper/overleaf/`：导出副本，供直接上传文件夹。修改时编辑 `paper/main.tex`，然后运行 `python3 paper/build_overleaf.py`，即可刷新此文件夹与 ZIP；不需要分别修改多份主稿。

当前稿尚未编译或视觉检查。真实队号与全队 AI 使用记录需要在最终提交前填写/合并；最终页数在 Overleaf 确认。

## 模型、实验与结果

- `src/alpha/`：当前模型实现。
- `configs/`：参数及实验设置。
- `experiments/`：可复现实验；本次新增 `run_review_followup.py` 与 `run_review_recheck.py`。
- `tests/`：测试；当前模型版本的上次运行结果为 84 项通过。
- `results/tables/`：结果表与设置清单，包括本次所有 `review_*` 输出。
- `results/figures/`：完整实验图件，包括政策机制图与新敏感性窗口图。
- [docs/review_followup_zh.md](docs/review_followup_zh.md)：连续事件修正、621 次敏感性扫描、风险约定检查和机制解释。
- `docs/mathematical_model.md`、`docs/part_v_mathematics.md`：详细数学推导；当前结果结合核查报告阅读。

## 历史材料

`paper/draft_parts_i_iv.tex`、`paper/part_v_outline.md` 和 `paper/part_vi_outline.md` 保留为阶段性材料；当前论文入口是 `paper/main.tex`。`paper/archive/` 保留更早版本，不应当作当前稿使用。旧模拟表仍保留原始阈值与精度口径，论文已区分其证据等级。

`docs/local_integration_manifest.json` 记录此前散落输出与当前项目文件的对应关系及内容校验。

此次操作完成本地整理与导出，没有执行 Git 提交或远端推送。

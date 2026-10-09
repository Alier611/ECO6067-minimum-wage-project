# ECO6067: Minimum wage replication project

Current stage: completed local analysis and nine-page English report, with AI disclosure and a submission guide.
GitHub publication and course-specific requirements remain to be finalized. No understanding quizzes are required.

Paper: David Card and Alan B. Krueger (1994), *Minimum Wages and Employment:
A Case Study of the Fast-Food Industry in New Jersey and Pennsylvania*,
American Economic Review 84(4), 772-793.

## 中文操作说明

1. 解压本项目包。保留其中的 `.git` 文件夹，它包含真实的阶段提交记录。
2. 将你已有的课程附件 `public.csv` 复制到 `data/raw/public.csv`。
   包内不重复提供原始数据；请使用你原来的附件。
3. 在本文件所在目录运行下面的命令。AI 可以协助运行，无需自行编写代码。

```bash
python -m pip install -r requirements.txt
python run_project.py --stage audit
python run_project.py --stage prepare
python run_project.py --stage replicate
python run_project.py --stage extend
python build_report.py
python check_reproducibility.py
```

Windows 如需使用 `py`，将命令中的 `python` 换成 `py`。
建议 Python 3.12 或 3.13。分析和报告所用依赖的已验证版本见
`requirements.txt` 及生成的 `results/provenance.json`。
重跑最终分析仅需 `python run_project.py --stage extend`，随后运行报告生成和检查命令。
报告字体及其许可证已随包提供，不依赖某台电脑的字体路径。

## 结果位置

- `report/ECO6067_empirical_report.pdf`: 九页英文实证报告，含全部核心表格、拓展、局限和AI披露。
- `report/ECO6067_empirical_report.md`: 可编辑的正文来源；表格来自实际计算输出。
- `report/AI_USE_DISCLOSURE.md`: 单独的AI使用披露。
- `SUBMISSION_GUIDE_ZH.md`: 无代码基础适用的最终提交说明。
- `results/data_audit.json`: 数据结构、缺失情况、状态编码及检查。
- `results/missing_values.csv`: 各字段缺失数量。
- `results/sample_flow.csv`: 各分析样本数量与筛选说明。
- `results/sample_summary.csv`: 分州 FTE 均值与可用观察数。
- `results/ownership_coverage.csv`: 独立拓展所需的四组样本数量。
- `results/checks.json`: 关键数据检查，不是学生理解测验。
- `data/processed/analysis.csv`: 原字段、派生变量及样本标记。
- `results/阶段说明.md`: 无需读代码即可查看的中文进度说明。
- `results/核心复现说明.md`: 完整Table 3 / Table 4、计算方法、原文对比和全部差异。
- `results/replication_results.html`: 可用浏览器打开的静态结果表。
- `results/table3_full.csv`, `results/table4_full.csv`: 未四舍五入的计算结果。
- `results/paper_comparison.csv`: 每个数字的原文值、复现值和匹配状态。
- `results/replication_checks.json`: 独立求解、协方差及地区基准检验。
- `results/独立拓展说明.md`: 中文与必要英文的拓展问题、方法、结果和局限。
- `results/extension_effects.csv`: 所有权组DID、直接组间差异、两种标准误与区间。
- `results/extension_sample_cells.csv`: 每个拓展模型的四组样本覆盖。
- `results/extension_checks.json`: 四组手算、方差核对、参照编码及单店影响检查。

## 来源与待确认事项

正式计算使用学生上传的课程数据。本阶段另已独立下载作者数据，并确认410行46列
全部数值与缺失位置与课程CSV完全一致；证据见results/author_source_verification.json。
作者数据来源：https://davidcard.berkeley.edu/data_sets.html
可选重新核对命令：python verify_author_data.py（需要访问作者网站）。
原始附件说明对应课程的 `01_DID.zip`。详见 `docs/data_sources.md`。
Table 3 / Table 4 是当前准备目标，课程指定核心表图、报告字数、语言及截止日期
仍需从课程补充要求核对。

原始和处理后餐厅级数据默认不加入 Git；在独立核实公开再分发条件前，不推送
这些文件。仓库提供输入位置及获取说明。论文 PDF 也不重复纳入项目。

## 工作流与版本记录

本阶段提供统一运行入口，replicate从原始数据重新构建并复现全部核心表格。
extend从原始数据依次执行数据准备、核心复现和所有权独立拓展。
check_reproducibility.py从空输出目录重跑全流程并核对文件。
Git 提交由 AI 助手以 `Codex AI Assistant` 身份创建，反映实际完成的阶段，
不使用学生身份、不倒填日期，也不伪造过去的工作。
本地 Git 仓库尚未连接或发布至 GitHub。

核心表格已计算，但并非所有数字完全匹配。Table 3第3行采用明确记录的替代标准误
估计，其原实现未恢复。Table 4第五列的公开作者核查程序省略所有权变量，
得到11.91（7.39）；按论文表格标注加入该变量得到11.98（7.42）。
两种规格并列报告，不通过隐瞒规格差异来凑数。作者程序变体的残差标准差和联合
p值仍不匹配原文，不能声称第五列整列完全一致。

## 可重复性与局限

清洗过程保留原始输入，不填补一般缺失值，不根据预期结论修改数据。
关闭状态按论文规则处理，详见 `docs/analysis_rules.md`。
第二期工资对永久关闭店的例外已在作者公开check.sas的样本筛选语句中确认，
也与357样本量一致。check.sas是公开核查程序，未宣称是当年期刊最终生产程序。
仅有一个政策前时期，不能进行通常的政策前平行趋势检验。
只有两个州，政策层面统计推断的局限应在最终报告中说明。

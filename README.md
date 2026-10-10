# ECO6067: Minimum wage replication project

Student: **WANG Ruiyue**, student ID **3036761820**.

The analysis, nine-page English report, AI disclosure and reproducibility workflow are complete.
The student published the repository and confirmed that the course imposes no additional
word-count, formatting or assigned-table requirements. The selected replication covers Tables 3 and 4.

Repository: https://github.com/Alier611/ECO6067-minimum-wage-project

The permitted processed data are included in `data/processed/analysis.csv`.
The original course CSV is not redistributed; its access and input location are described below.

Paper: David Card and Alan B. Krueger (1994), *Minimum Wages and Employment:
A Case Study of the Fast-Food Industry in New Jersey and Pennsylvania*,
American Economic Review 84(4), 772-793.

## 中文操作说明

1. 克隆本仓库，或通过GitHub的Code菜单下载项目。克隆会同时保留Git提交历史。
2. 从ECO6067课程的 `01_DID.zip` 取得原始 `public.csv`，复制到 `data/raw/public.csv`。
   原始课程数据不在公开仓库中；教学团队可使用课程已提供的相同附件。
   已提交的最终处理后数据位于 `data/processed/analysis.csv`。
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

## 来源、数据访问与课程确认

正式计算使用学生上传的课程数据。本阶段另已独立下载作者数据，并确认410行46列
全部数值与缺失位置与课程CSV完全一致；证据见results/author_source_verification.json。
作者数据来源：https://davidcard.berkeley.edu/data_sets.html
可选重新核对命令：python verify_author_data.py（需要访问作者网站）。
原始附件说明对应课程的 `01_DID.zip`。详见 `docs/data_sources.md`。
学生已核对课程没有额外字数、格式或指定表图要求，本项目复现原文Table 3 / Table 4。
截止时间仍以课程平台通知为准；本项目不自行设定截止日期。

依据学生对课程许可范围的确认，处理后的 `data/processed/analysis.csv` 已加入公开仓库。
原始课程CSV不公开上传；不要通过上传完整附件或其他文件绕过原始数据的访问限制。
仓库提供课程输入获取说明及作者数据来源。原始论文PDF不重复纳入项目，生成的项目报告PDF已提交。

For the teaching team: obtain `public.csv` from the course `01_DID.zip` and place it at
`data/raw/public.csv` before rebuilding from raw input. The submitted processed file contains
410 restaurant rows, original columns, derived FTE/GAP variables and sample flags. Full raw-input
reproduction and the SHA-256 repeat check require the original course CSV bytes. The public author
archive was separately acquired and all values and missing positions were verified against that CSV;
`verify_author_data.py` rechecks equality after the course input is present.

## 工作流与版本记录

本阶段提供统一运行入口，replicate从原始数据重新构建并复现全部核心表格。
extend从原始数据依次执行数据准备、核心复现和所有权独立拓展。
check_reproducibility.py从空输出目录重跑全流程并核对文件。
最初8次Git提交由AI助手创建，记录规划、审计、准备、复现、拓展计划、拓展估计、报告和身份更新。
学生随后手动发布仓库，并提交处理后数据。阶段记录保留实际身份和时间，不倒填或改写历史。
仓库已经公开发布，教学团队可以使用上面的URL访问、克隆或下载。

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

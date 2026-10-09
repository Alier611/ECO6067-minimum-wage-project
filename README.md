# ECO6067: Minimum wage replication project

Current stage: data audit and analysis-variable construction. This is a working
project, not the final submission. No understanding quizzes are required.

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
```

Windows 如需使用 `py`，将命令中的 `python` 换成 `py`。
推荐 Python 3.11 或更新版本。本阶段使用 pandas 和 numpy；已验证的版本见
`requirements.txt` 及生成的 `results/provenance.json`。

## 结果位置

- `results/data_audit.json`: 数据结构、缺失情况、状态编码及检查。
- `results/missing_values.csv`: 各字段缺失数量。
- `results/sample_flow.csv`: 各分析样本数量与筛选说明。
- `results/sample_summary.csv`: 分州 FTE 均值与可用观察数。
- `results/ownership_coverage.csv`: 独立拓展所需的四组样本数量。
- `results/checks.json`: 关键数据检查，不是学生理解测验。
- `data/processed/analysis.csv`: 原字段、派生变量及样本标记。
- `results/阶段说明.md`: 无需读代码即可查看的中文进度说明。

## 来源与待确认事项

目前使用学生上传的课程数据。尚未独立下载作者数据；不声称已完成该步骤。
原始附件说明对应课程的 `01_DID.zip`。详见 `docs/data_sources.md`。
Table 3 / Table 4 是当前准备目标，课程指定核心表图、报告字数、语言及截止日期
仍需从课程补充要求核对。

原始和处理后餐厅级数据默认不加入 Git；在独立核实公开再分发条件前，不推送
这些文件。仓库提供输入位置及获取说明。论文 PDF 也不重复纳入项目。

## 工作流与版本记录

本阶段提供统一运行入口。后续将在此入口增加核心复现与独立拓展。
Git 提交由 AI 助手以 `Codex AI Assistant` 身份创建，反映实际完成的阶段，
不使用学生身份、不倒填日期，也不伪造过去的工作。
本地 Git 仓库尚未连接或发布至 GitHub。

## 可重复性与局限

清洗过程保留原始输入，不填补一般缺失值，不根据预期结论修改数据。
关闭状态按论文规则处理，详见 `docs/analysis_rules.md`。
第二期工资对永久关闭店的例外依据论文关闭店处理原则及357样本量的一致性核查；
本项目尚未获得作者的原始分析程序。
仅有一个政策前时期，不能进行通常的政策前平行趋势检验。
只有两个州，政策层面统计推断的局限应在最终报告中说明。

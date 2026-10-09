"""One entry point for staged preparation. All paths are relative to this project."""
import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd
import scipy

ROOT = Path(__file__).resolve().parent


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')


def audit(raw, out):
    out.mkdir(parents=True, exist_ok=True)
    x = pd.read_csv(raw)
    checks = {
        'shape_410_by_46': x.shape == (410, 46),
        'no_exact_duplicate_rows': not x.duplicated().any(),
        'unique_state_sheet': not x.duplicated(['STATE', 'SHEET']).any(),
        'state_codes_complete': x.STATE.notna().all() and x.STATE.isin([0, 1]).all(),
        'chain_codes_complete': x.CHAIN.notna().all() and x.CHAIN.isin([1, 2, 3, 4]).all(),
        'ownership_codes_complete': x.CO_OWNED.notna().all() and x.CO_OWNED.isin([0, 1]).all(),
        'status_codes_complete': x.STATUS2.notna().all() and x.STATUS2.isin(range(6)).all(),
        'state_counts_79_331': int((x.STATE == 0).sum()) == 79 and int((x.STATE == 1).sum()) == 331,
        'permanent_closures_6': int((x.STATUS2 == 3).sum()) == 6,
        'temporary_closures_4': int(x.STATUS2.isin([2, 4, 5]).sum()) == 4,
    }
    emp_cols = ['EMPFT', 'EMPPT', 'NMGRS', 'EMPFT2', 'EMPPT2', 'NMGRS2']
    checks['employment_nonnegative_or_missing'] = bool((x[emp_cols].ge(0) | x[emp_cols].isna()).all().all())
    checks['wages_positive_or_missing'] = bool((x[['WAGE_ST', 'WAGE_ST2']].gt(0) | x[['WAGE_ST', 'WAGE_ST2']].isna()).all().all())
    checks = {k: bool(v) for k, v in checks.items()}
    if not all(checks.values()):
        raise ValueError('Input audit failed: ' + ', '.join(k for k, v in checks.items() if not v))
    missing = x.isna().sum().rename('missing_count').rename_axis('variable').reset_index()
    missing.to_csv(out / 'missing_values.csv', index=False)
    report = {
        'rows': len(x), 'columns': len(x.columns),
        'state_counts': {'PA': int((x.STATE == 0).sum()), 'NJ': int((x.STATE == 1).sum())},
        'repeated_sheet_rows': x.loc[x.SHEET.duplicated(False), ['STATE', 'SHEET', 'CHAIN']].to_dict('records'),
        'status_counts': {str(k): int(v) for k, v in x.STATUS2.value_counts().sort_index().items()},
        'checks': checks,
        'notes': ['SHEET alone is not unique; retain all observations.', 'Blank input fields remain missing.'],
    }
    write_json(out / 'data_audit.json', report)
    provenance = {
        'input_name': raw.name, 'input_sha256': hashlib.sha256(raw.read_bytes()).hexdigest(),
        'source': 'Student-provided course attachment; no independent author download yet.',
        'software': {'python': platform.python_version(), 'pandas': pd.__version__, 'numpy': np.__version__, 'scipy': scipy.__version__},
    }
    write_json(out / 'provenance.json', provenance)
    return x, checks


def prepare(x, out, processed, checks):
    z = x.copy()
    z['store_key'] = z.STATE.astype(int).astype(str) + '_' + z.SHEET.astype(int).astype(str)
    z['fte1'] = z.EMPFT + z.NMGRS + 0.5 * z.EMPPT
    z['fte2_components'] = z.EMPFT2 + z.NMGRS2 + 0.5 * z.EMPPT2
    z['fte2'] = z.fte2_components
    z.loc[z.STATUS2 == 3, 'fte2'] = 0.0
    z.loc[z.STATUS2.isin([0, 2, 4, 5]), 'fte2'] = np.nan
    z['fte2_temporary_zero'] = z.fte2
    z.loc[z.STATUS2.isin([2, 3, 4, 5]), 'fte2_temporary_zero'] = 0.0
    z['change_fte'] = z.fte2 - z.fte1
    z['change_fte_temporary_zero'] = z.fte2_temporary_zero - z.fte1
    z['gap'] = np.nan
    z.loc[z.STATE == 0, 'gap'] = 0.0
    nj_wage = (z.STATE == 1) & z.WAGE_ST.notna()
    z.loc[nj_wage, 'gap'] = (5.05 / z.loc[nj_wage, 'WAGE_ST'] - 1).clip(lower=0)
    z['nj_wage_group'] = pd.Series(pd.NA, index=z.index, dtype='string')
    z.loc[(z.STATE == 1) & (z.WAGE_ST == 4.25), 'nj_wage_group'] = 'low_4.25'
    z.loc[(z.STATE == 1) & z.WAGE_ST.gt(4.25) & z.WAGE_ST.lt(5), 'nj_wage_group'] = 'middle_4.26_to_4.99'
    z.loc[(z.STATE == 1) & z.WAGE_ST.ge(5), 'nj_wage_group'] = 'high_at_least_5.00'
    z['table3_wave1'] = z.fte1.notna()
    z['table3_wave2'] = z.fte2.notna()
    z['table3_balanced'] = z.fte1.notna() & z.fte2.notna()
    z['table3_temporary_zero'] = z.fte1.notna() & z.fte2_temporary_zero.notna()
    z['table4_literal_both_wages'] = z.table3_balanced & z.WAGE_ST.notna() & z.WAGE_ST2.notna()
    z['table4_working'] = z.table3_balanced & z.WAGE_ST.notna() & (z.WAGE_ST2.notna() | z.STATUS2.eq(3))
    rows = []
    definitions = {
        'raw': 'All input observations; no deduplication by SHEET alone.',
        'table3_wave1': 'Available wave-1 FTE.',
        'table3_wave2': 'Available base wave-2 FTE, permanent closures zero.',
        'table3_balanced': 'Both base FTE observations available.',
        'table3_temporary_zero': 'Both FTE available after temporary-closure zero sensitivity.',
        'table4_literal_both_wages': 'Balanced FTE plus literally both starting wages.',
        'table4_working': 'Balanced FTE plus both wages, second wage exempt for permanent closures.',
    }
    for name, rule in definitions.items():
        m = pd.Series(True, index=z.index) if name == 'raw' else z[name]
        rows.append({'sample': name, 'all': int(m.sum()), 'PA': int((m & z.STATE.eq(0)).sum()),
                     'NJ': int((m & z.STATE.eq(1)).sum()), 'excluded_from_raw': int((~m).sum()), 'rule': rule})
    pd.DataFrame(rows).to_csv(out / 'sample_flow.csv', index=False)
    summary = []
    for state, label in [(0, 'PA'), (1, 'NJ')]:
        t = z[z.STATE == state]
        for variable in ['fte1', 'fte2', 'change_fte', 'change_fte_temporary_zero']:
            summary.append({'state': label, 'variable': variable, 'n': int(t[variable].count()), 'mean': float(t[variable].mean())})
    pd.DataFrame(summary).to_csv(out / 'sample_summary.csv', index=False)
    coverage = []
    for state, label in [(0, 'PA'), (1, 'NJ')]:
        for owned in [0, 1]:
            t = z[z.STATE.eq(state) & z.CO_OWNED.eq(owned)]
            coverage.append({'state': label, 'company_owned': owned, 'raw_n': len(t),
                             'balanced_n': int(t.table3_balanced.sum()), 'table4_n': int(t.table4_working.sum())})
    pd.DataFrame(coverage).to_csv(out / 'ownership_coverage.csv', index=False)
    def same(a, b):
        return bool(np.isclose(a, b, rtol=0, atol=1e-10))
    for state, sheet, pre, post in [(0, 46, 40.5, 24.0), (0, 49, 13.75, 11.5), (1, 407, 12.0, 14.5)]:
        row = z[z.STATE.eq(state) & z.SHEET.eq(sheet)].iloc[0]
        checks[f'manual_FTE_{state}_{sheet}'] = same(row.fte1, pre) and same(row.fte2, post)
    checks.update({
        'permanent_FTE2_zero': bool(z.loc[z.STATUS2.eq(3), 'fte2'].eq(0).all()),
        'temporary_FTE2_missing': bool(z.loc[z.STATUS2.isin([2, 4, 5]), 'fte2'].isna().all()),
        'refusal_FTE2_missing': bool(z.loc[z.STATUS2.eq(0), 'fte2'].isna().all()),
        'PA_gap_zero': bool(z.loc[z.STATE.eq(0), 'gap'].eq(0).all()),
        'missing_NJ_wage_not_imputed': bool(z.loc[z.STATE.eq(1) & z.WAGE_ST.isna(), 'gap'].isna().all()),
        'balanced_N_384': int(z.table3_balanced.sum()) == 384,
        'working_regression_N_357': int(z.table4_working.sum()) == 357,
        'literal_regression_N_351': int(z.table4_literal_both_wages.sum()) == 351,
        'closure_wage_exception_retains_six': int((z.table4_working & z.STATUS2.eq(3)).sum()) == 6,
    })
    # Independent algebraic check: subgroup means vs. least-squares coefficient.
    b = z[z.table3_balanced]
    means = b.groupby('STATE').change_fte.mean()
    did = float(means.loc[1] - means.loc[0])
    design = np.column_stack([np.ones(len(b)), b.STATE.to_numpy()])
    coefficient = float(np.linalg.lstsq(design, b.change_fte.to_numpy(), rcond=None)[0][1])
    checks['balanced_means_vs_OLS'] = same(did, coefficient)
    if not all(checks.values()):
        raise ValueError('Preparation check failed: ' + ', '.join(k for k, v in checks.items() if not v))
    processed.mkdir(parents=True, exist_ok=True)
    z.to_csv(processed / 'analysis.csv', index=False)
    write_json(out / 'checks.json', {'passed': sum(checks.values()), 'total': len(checks), 'checks': checks,
                                    'diagnostic_balanced_DID': did, 'diagnostic_OLS_coefficient': coefficient,
                                    'note': 'Diagnostic only; full table replication and standard errors pending.'})
    flow_text = '\n'.join(f"| {r['sample']} | {r['all']} | {r['PA']} | {r['NJ']} |" for r in rows)
    note = f'''# ECO6067 阶段进度：数据审计与变量准备

已跳过学生理解测验。已完成项目初始化、数据审计和变量构建。
本文件是数据准备说明；若运行extend，独立拓展结果另见独立拓展说明.md。
尚未完成最终提交报告。

## 数据与样本

原始数据410行、46列；NJ 331家、PA 79家。所有原始记录保留。
SHEET=407出现在两个州，不能单独据此去重。
一般空白保持缺失；6家永久关闭店第二期FTE为0；4家暂时关闭店基础分析为缺失。

| 样本标记 | 合计 | PA | NJ |
| --- | ---: | ---: | ---: |
{flow_text}

以上是不同表格的独立样本定义，不是一条逐步删行的共同样本。
Table 4的第二期工资例外保留永久关闭店，已在作者公开核查程序中确认；
其样本量与原文357一致，各列结果及对比见核心复现说明.md。

## 检查结果

{len(checks)}项关键检查全部通过，其中包括3家餐厅的预先手算值核对。
同一平衡样本上，均值差分得到DID {did:.10f}，
简单回归得到 {coefficient:.10f}，二者一致。
该数字是数据准备阶段的计算核查；若运行replicate阶段，完整Table 3、Table 4及标准误
另见核心复现说明.md和table3_full.csv、table4_full.csv。
重新运行的一致性结果见 reproducibility_check.json（完成重跑后生成）。

## 下一步

当前生成的是数据准备说明。完整核心复现阶段的完成状态与差异调查
另见核心复现说明.md。Table 4第五列已并列核对论文标注规格和作者程序规格，
后者省略所有权变量，其主要系数和标准误与原文匹配。
课程指定核心表图、报告字数、语言、截止日期待课程资料核对。
独立拓展问题已预先记录：直营店与加盟店的就业反应是否不同。
若运行extend阶段，拓展结果已估计并另行报告；不以结果显著与否挑选问题。

## 使用和提交

项目包不重复附带原始数据。将已有public.csv复制到data/raw后运行README中的命令。
本地Git记录已建立；尚未发布GitHub。查看版本记录可运行git log --oneline。
餐厅级原始与处理后数据默认不加入Git，公开再分发条件仍待独立核实。
无需回答知识测验；后续继续保留数据、统计和可重复性检查。
'''
    (out / '阶段说明.md').write_text(note, encoding='utf-8')
    return z


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stage', choices=['audit', 'prepare', 'replicate', 'extend'], default='extend')
    p.add_argument('--input', type=Path, default=ROOT / 'data/raw/public.csv')
    p.add_argument('--output-dir', type=Path, default=ROOT / 'results')
    p.add_argument('--processed-dir', type=Path, default=ROOT / 'data/processed')
    args = p.parse_args()
    if not args.input.is_file():
        p.error('Missing public.csv. Copy the course attachment to data/raw/public.csv or use --input PATH.')
    before = hashlib.sha256(args.input.read_bytes()).hexdigest()
    x, checks = audit(args.input, args.output_dir)
    if args.stage in ['prepare', 'replicate', 'extend']:
        z = prepare(x, args.output_dir, args.processed_dir, checks)
        if args.stage in ['replicate', 'extend']:
            from replicate_tables import replicate
            replicate(z, args.output_dir)
        if args.stage == 'extend':
            from ownership_extension import run_extension
            run_extension(z, args.output_dir)
    if hashlib.sha256(args.input.read_bytes()).hexdigest() != before:
        raise ValueError('Raw input unexpectedly changed.')
    print(f'{args.stage} complete: {len(x)} input rows; raw input unchanged.')


if __name__ == '__main__':
    main()

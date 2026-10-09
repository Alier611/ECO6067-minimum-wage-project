"""Compute Tables 3 and 4; keep original benchmarks separate from estimates."""
import html
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import f as f_distribution

ROOT = Path(__file__).resolve().parent
COLS = ['PA', 'NJ', 'NJ_minus_PA', 'NJ_low', 'NJ_middle', 'NJ_high', 'low_minus_high', 'middle_minus_high']
ROWS = ['FTE before: available observations', 'FTE after: available observations',
        'Change in available-case means', 'Mean change: balanced sample',
        'Mean change: temporary closures set to zero']


def fit_ols(y, frame):
    """Classical OLS covariance for comparison with published Table 4."""
    X = np.column_stack([np.ones(len(frame)), frame.to_numpy(dtype=float)])
    y = np.asarray(y, dtype=float)
    if not np.isfinite(X).all() or not np.isfinite(y).all():
        raise ValueError('Nonfinite regression input.')
    n, k = X.shape
    if np.linalg.matrix_rank(X) != k:
        raise ValueError('Rank-deficient model.')
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    residual = y - X @ beta
    sse = float(residual @ residual)
    s2 = sse / (n - k)
    inverse = np.linalg.inv(X.T @ X)
    covariance = s2 * inverse
    standard_error = np.sqrt(np.diag(covariance))
    # HC1 is a separate diagnostic, not substituted for the original table.
    meat = X.T @ (X * residual[:, None] ** 2)
    hc1 = n / (n - k) * inverse @ meat @ inverse
    beta_check = np.linalg.solve(X.T @ X, X.T @ y)
    if not np.allclose(beta, beta_check, rtol=0, atol=1e-8):
        raise ValueError('Independent coefficient solver disagreement.')
    if not np.allclose(X.T @ residual, 0, rtol=0, atol=1e-7):
        raise ValueError('Residual orthogonality check failed.')
    # SVD construction provides a second covariance calculation.
    _, singular, vt = np.linalg.svd(X, full_matrices=False)
    covariance_check = s2 * (vt.T / singular ** 2) @ vt
    if not np.allclose(covariance, covariance_check, rtol=1e-8, atol=1e-8):
        raise ValueError('Independent covariance calculation disagreement.')
    return {'beta': beta, 'se': standard_error, 'hc1_se': np.sqrt(np.diag(hc1)),
            'covariance':covariance, 'hc1_covariance':hc1,
            'sse': sse, 'df': n - k, 'n': n, 'k': k, 'residual_sd': np.sqrt(s2),
            'terms': ['constant'] + list(frame.columns)}


def mean_cell(values):
    a = values.dropna().to_numpy(dtype=float)
    return float(a.mean()), float(a.std(ddof=1) / np.sqrt(len(a))), len(a)


def unbalanced_change(t):
    """Store-level influence-function SE for two linked available-case means.

    Missing contributions are zero only in the estimating-equation influence;
    no outcome is imputed, and denominators remain the observed wave counts.
    This is an explicit alternative to the undocumented published row-3 SE.
    """
    a, b = t.fte1, t.fte2
    ma, mb = float(a.mean()), float(b.mean())
    n, na, nb = len(t), int(a.count()), int(b.count())
    influence = n * (b - mb).fillna(0) / nb - n * (a - ma).fillna(0) / na
    return mb - ma, float(influence.std(ddof=1) / np.sqrt(n)), (na, nb)


def table3(z):
    groups = {'PA': z[z.STATE.eq(0)], 'NJ': z[z.STATE.eq(1)],
              'NJ_low': z[z.nj_wage_group.eq('low_4.25')],
              'NJ_middle': z[z.nj_wage_group.eq('middle_4.26_to_4.99')],
              'NJ_high': z[z.nj_wage_group.eq('high_at_least_5.00')]}
    records = []
    for row in range(1, 6):
        cells = {}
        for group, t in groups.items():
            if row == 3:
                value, se, n = unbalanced_change(t)
                n1, n2 = n
            else:
                variable = {1:'fte1', 2:'fte2', 4:'change_fte', 5:'change_fte_temporary_zero'}[row]
                value, se, n = mean_cell(t[variable])
                n1 = n2 = n
            cells[group] = {'estimate': value, 'standard_error': se, 'n1': n1, 'n2': n2}
        for name, a, b in [('NJ_minus_PA', 'NJ', 'PA'), ('low_minus_high', 'NJ_low', 'NJ_high'), ('middle_minus_high', 'NJ_middle', 'NJ_high')]:
            cells[name] = {'estimate': cells[a]['estimate'] - cells[b]['estimate'],
                           'standard_error': float(np.hypot(cells[a]['standard_error'], cells[b]['standard_error'])),
                           'n1': cells[a]['n1'], 'n2': cells[b]['n1']}
        for col in COLS:
            records.append({'row': row, 'row_label': ROWS[row-1], 'column': col, **cells[col],
                            'se_method': 'linked available-case influence function; independent groups' if row == 3 else 'sample-mean SE; independent-group variances for contrasts'})
    return pd.DataFrame(records)


def table4(z):
    t = z[z.table4_working].copy()
    chain = pd.get_dummies(t.CHAIN, prefix='chain', drop_first=True, dtype=float)
    controls = pd.concat([chain, t[['CO_OWNED']]], axis=1)
    regions = t[['CENTRALJ', 'SOUTHJ', 'PA1', 'PA2']]
    specifications = [('i', 'STATE', []), ('ii', 'STATE', [controls]),
                      ('iii', 'gap', []), ('iv', 'gap', [controls]), ('v', 'gap', [controls, regions])]
    summaries, full = [], []
    for model, treatment, extra in specifications:
        design = pd.concat([t[[treatment]], *extra], axis=1)
        fit = fit_ols(t.change_fte, design)
        reduced = fit_ols(t.change_fte, t[[treatment]])
        q = fit['k'] - reduced['k']
        if q:
            statistic = ((reduced['sse'] - fit['sse']) / q) / (fit['sse'] / fit['df'])
            p_value = float(f_distribution.sf(statistic, q, fit['df']))
        else:
            statistic = p_value = np.nan
        summaries.append({'model':model, 'treatment_variable':treatment,
                          'coefficient':float(fit['beta'][1]), 'standard_error':float(fit['se'][1]),
                          'hc1_standard_error_diagnostic':float(fit['hc1_se'][1]),
                          'chain_ownership_controls':bool(extra), 'region_controls':model == 'v',
                          'residual_sd':float(fit['residual_sd']), 'controls_p_value':p_value,
                          'controls_F_statistic':statistic, 'controls_df':q,
                          'residual_df':fit['df'], 'n':fit['n']})
        for term, coef, se in zip(fit['terms'], fit['beta'], fit['se']):
            full.append({'model':model,'term':term,'coefficient':float(coef),'standard_error':float(se)})
    # Omitted-region invariance: five exhaustive regions must span the same space.
    region_coefficients = {}
    for omitted in ['NORTHJ', 'CENTRALJ', 'SOUTHJ', 'PA1', 'PA2']:
        include = [r for r in ['NORTHJ', 'CENTRALJ', 'SOUTHJ', 'PA1', 'PA2'] if r != omitted]
        design = pd.concat([t[['gap']], controls, t[include]], axis=1)
        region_coefficients[omitted] = float(fit_ols(t.change_fte, design)['beta'][1])
    if np.ptp(list(region_coefficients.values())) > 1e-8:
        raise ValueError('Omitted-region invariance failed.')
    # Public author check.sas omits CO_OWNED in the level-change region model.
    # Keep the printed-table specification above; report the author variant separately.
    author_design = pd.concat([t[['gap']], chain, regions], axis=1)
    author_fit = fit_ols(t.change_fte, author_design)
    author_reduced = fit_ols(t.change_fte, t[['gap']])
    author_q = author_fit['k'] - author_reduced['k']
    author_F = ((author_reduced['sse'] - author_fit['sse']) / author_q) / (author_fit['sse'] / author_fit['df'])
    author_variant = {'model':'v_author_check_program','coefficient':float(author_fit['beta'][1]),
                      'standard_error':float(author_fit['se'][1]),'residual_sd':float(author_fit['residual_sd']),
                      'controls_p_value':float(f_distribution.sf(author_F,author_q,author_fit['df'])),
                      'n':author_fit['n'],'co_owned_included':False,
                      'note':'Public author check.sas variant; not silently substituted for the printed ownership-control specification.'}
    diagnostic = {'sample_n':len(t), 'dependent_mean':float(t.change_fte.mean()),
                  'dependent_sd':float(t.change_fte.std(ddof=1)),
                  'model_v_omitted_region_coefficients':region_coefficients,
                  'author_program_model_v_variant':author_variant,
                  'checks':'Coefficient solvers, covariance constructions, normal equations, full rank and omitted-region invariance passed.',
                  'inference_note':'Classical SE reproduce the paper convention; HC1 is supplementary. Neither addresses only two policy jurisdictions.'}
    return pd.DataFrame(summaries), pd.DataFrame(full), diagnostic


def comparisons(a, b, original):
    records = []
    for _, cell in a.iterrows():
        ri, ci = int(cell.row)-1, COLS.index(cell['column'])
        for metric, source in [('estimate','table3_estimates'), ('standard_error','table3_standard_errors')]:
            benchmark = original[source][ri][ci]
            computed = float(cell[metric])
            matched = f'{computed:.2f}' == f'{benchmark:.2f}'
            note = ''
            if not matched:
                note = ('Explicit alternative linked-sample SE; original row-3 method not recovered.'
                        if ri == 2 and metric == 'standard_error' else
                        'Small published-value mismatch; exact provenance unresolved, not forced to match.')
            records.append({'table':'Table 3','row_or_model':str(ri+1),'column_or_metric':cell['column'],
                            'metric':metric,'original':benchmark,'replication':computed,
                            'difference':computed-benchmark,'matches_printed_precision':matched,'note':note})
    for _, row in b.iterrows():
        source = next(item for item in original['table4'] if item['model'] == row.model)
        for metric in ['coefficient','standard_error','residual_sd','controls_p_value','n']:
            if source[metric] is None:
                continue
            computed, benchmark = float(row[metric]), source[metric]
            matched = computed == benchmark if metric == 'n' else f'{computed:.2f}' == f'{benchmark:.2f}'
            records.append({'table':'Table 4','row_or_model':row.model,'column_or_metric':metric,
                            'metric':metric,'original':benchmark,'replication':computed,
                            'difference':computed-benchmark,'matches_printed_precision':matched,
                            'note':'' if matched else 'Printed-table specification includes ownership; public author check.sas omits it. See the separately reported author variant.'})
    return pd.DataFrame(records)


def markdown_table3(a):
    lines = ['| Row | ' + ' | '.join(COLS) + ' |', '| --- | ' + ' | '.join(['---:']*len(COLS)) + ' |']
    for ri in range(1, 6):
        t = a[a.row.eq(ri)].set_index('column')
        lines.append('| ' + str(ri) + '. ' + ROWS[ri-1] + ' | ' + ' | '.join(f"{t.loc[c,'estimate']:.2f} ({t.loc[c,'standard_error']:.2f})" for c in COLS) + ' |')
    return '\n'.join(lines)


def markdown_table4(b):
    lines = ['| Model | Main coefficient (SE) | Chain / ownership | Region | Residual SD | Controls p | N |',
             '| --- | ---: | --- | --- | ---: | ---: | ---: |']
    for _, r in b.iterrows():
        p = '-' if pd.isna(r.controls_p_value) else f'{r.controls_p_value:.2f}'
        lines.append(f"| ({r.model}) | {r.coefficient:.2f} ({r.standard_error:.2f}) | {'yes' if r.chain_ownership_controls else 'no'} | {'yes' if r.region_controls else 'no'} | {r.residual_sd:.2f} | {p} | {r.n} |")
    return '\n'.join(lines)


def replicate(z, out):
    original = json.loads((ROOT / 'docs/paper_benchmarks.json').read_text(encoding='utf-8'))
    a = table3(z)
    b, full, diagnostic = table4(z)
    c = comparisons(a, b, original)
    a.to_csv(out / 'table3_full.csv', index=False)
    b.to_csv(out / 'table4_full.csv', index=False)
    full.to_csv(out / 'table4_all_coefficients.csv', index=False)
    c.to_csv(out / 'paper_comparison.csv', index=False)
    author_variant = diagnostic['author_program_model_v_variant']
    pd.DataFrame([author_variant]).to_csv(out / 'table4_author_program_variant.csv', index=False)
    (out / 'replication_checks.json').write_text(json.dumps(diagnostic, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    counts = c.groupby('table').matches_printed_precision.agg(['sum','count'])
    differs = c[~c.matches_printed_precision]
    difference_lines = ['| Table / row or model | Cell | Metric | Original | Replication |', '| --- | --- | --- | ---: | ---: |']
    for _, r in differs.iterrows():
        difference_lines.append(f'| {r.table} / {r.row_or_model} | {r.column_or_metric} | {r.metric} | {r.original:.2f} | {r.replication:.6f} |')
    report = f'''# ECO6067 核心表格复现阶段

本阶段已完成Table 3全部5行8列、Table 4全部5个模型的计算及逐项原文对比。
计算完成不等于每个原文数字完全匹配；下面保留全部差异。
原文基准来自学生上传论文印刷页780（PDF第9页），人工读取原表。
代码计算不读取基准数字；基准只用于计算完成后的比较。

## Table 3: employment levels and changes

单位：全职当量／店；括号内为标准误。

{markdown_table3(a)}

第1、2行分别使用每期可用FTE；第4行要求两期就业均可用；
第5行把4家暂时关闭店第二期就业改记为0。6家永久关闭店保留、就业为0。
第3行是两期可用样本均值之差，其标准误采用明确的餐厅级影响函数估计，
计入同一餐厅跨期观测的相关性；这与原文未交代的第3行标准误实现并不完全一致。
第1、2、4、5行使用样本均值标准误；不同组的对比将方差相加。

## Table 4: regression-adjusted models

所有模型含截距，使用同一357家样本；因变量为FTE变化。
模型(i)-(ii)的主要变量为NJ指示变量，(iii)-(v)为初始工资缺口GAP。
GAP是比例：0.10表示10%，系数不能当成整个NJ的平均就业政策效应。

{markdown_table4(b)}

回归标准误采用常规OLS残差方差估计，与原文前四列匹配；
额外HC1诊断标准误单列在CSV，不替代复现表的常规标准误。
Controls p是排除该列全部控制变量的联合F检验p值，不是政策变量p值。
完整控制变量系数见table4_all_coefficients.csv。

## 逐项对比与差异

Table 3共有80个数值对比，其中{int(counts.loc['Table 3','sum'])}个在两位小数精度内一致。
Table 4共有{int(counts.loc['Table 4','count'])}个数值对比，其中{int(counts.loc['Table 4','sum'])}个一致。
以下是所有不一致项，不把不一致自动视为程序错误，也不隐藏它们。

{chr(10).join(difference_lines)}

## 对差异的解释与调查状态

1. 非平衡样本DID实际为2.753605782981，与原文2.76相差约0.0064。
   前期回复称“约2.76”不够精确，本阶段更正为实际计算值2.7536（显示2.75）。
   不是断言原文只因四舍五入出现差异；原始分析程序未取得，来源仍未确定。
2. Table 3第3行标准误是我们明确选择的可辩护实现，原文计算规则未恢复。
   不用第4行标准误冒充第3行，也不把两期数据错误当作完全独立。
3. Table 4模型(v)按表格标注加入所有权变量，GAP为{b.loc[b.model.eq('v'),'coefficient'].iloc[0]:.8f}，
   标准误{b.loc[b.model.eq('v'),'standard_error'].iloc[0]:.8f}；原文11.91、7.39。
   已核对357样本、GAP定义、控制变量和矩阵满秩，并轮换五种地区基准。
   地区基准变化均得到相同结果，因此不能把差异归因于仅仅省略了不同基准地区。
   进一步获取作者公开数据包中的check.sas后，发现其对应水平变化模型省略CO_OWNED。
   按这个程序的规格，系数{author_variant['coefficient']:.8f}、标准误{author_variant['standard_error']:.8f}，
   两位小数均匹配原文11.91（7.39）。这解释了主要系数和标准误的差异。
   但该程序规格的残差标准差为{author_variant['residual_sd']:.8f}、控制变量联合p值
   为{author_variant['controls_p_value']:.8f}，不把它们声称为整列全部精确匹配。
   保留表格文字规格和作者核查程序规格，原文为何混合这些数值仍无法确认。
   作者README描述该程序用于书籍相关调查数据核查，不能断言它是当年期刊最终生产程序。

## 作者数据独立获取与核查

已从作者网站下载njmin.zip，用其public.dat核对课程CSV：410行、46列，
全部数值及缺失位置逐项完全一致。证据见author_source_verification.json。
这排除了当前作者公开数据与当前课程数据的数值差别，并不证明历史出版数据没有差别。
来源：https://davidcard.berkeley.edu/data_sets.html
下载：https://davidcard.berkeley.edu/data_sets/njmin.zip
说明：https://davidcard.berkeley.edu/readme/njmin-readme.txt
独立获取脚本：verify_author_data.py；它不改动课程输入。

## 质量检查与解释范围

OLS系数用两种求解方法核对；协方差用矩阵逆和SVD两种方法核对；
验证残差与全部回归列正交、模型满秩、地区基准不改变系数。
357样本因变量均值{diagnostic['dependent_mean']:.6f}、标准差{diagnostic['dependent_sd']:.6f}，
与原文显示的-0.237、8.825非常接近，保留完整精度。
完整流程重跑结果见reproducibility_check.json。

主要就业估计为正，与原文方向一致。但并非每个模型都在常规水平显著，
也不能推广为所有最低工资政策都会增加就业。只有一次政策前观测，
无法完成通常的政策前趋势检验；只有两个州，餐厅级OLS或HC1标准误
不能解决州级政策冲击的推断局限。

## 下一阶段

若已运行extend阶段，预先记录的所有权独立拓展结果见独立拓展说明.md。
课程指定核心表图、字数、语言及日期仍需从课程补充说明核对。
本文件只报告核心复现；最终报告或GitHub发布尚未完成。
'''
    (out / '核心复现说明.md').write_text(report, encoding='utf-8')
    # Human-readable static report: generated numbers only, no app or network.
    table_a = a.copy()
    pivot = table_a.assign(value=table_a.apply(lambda r: f'{r.estimate:.2f} ({r.standard_error:.2f})',axis=1)).pivot(index='row_label',columns='column',values='value').reindex(ROWS)[COLS]
    tables = [('Table 3 - estimates (standard errors)',pivot.to_html(escape=True)),
              ('Table 4 - regression results',b[['model','coefficient','standard_error','residual_sd','controls_p_value','n']].to_html(index=False,float_format=lambda v:f'{v:.4f}')),
              ('Model (v) author check-program variant: ownership omitted',pd.DataFrame([author_variant])[['coefficient','standard_error','residual_sd','controls_p_value','n']].to_html(index=False,float_format=lambda v:f'{v:.4f}')),
              ('All differences from the published tables',differs[['table','row_or_model','column_or_metric','metric','original','replication','note']].to_html(index=False,float_format=lambda v:f'{v:.6f}'))]
    body = ''.join('<h2>'+html.escape(title)+'</h2><div class="scroll">'+table+'</div>' for title,table in tables)
    page = '<!doctype html><html lang="zh"><meta charset="utf-8"><title>ECO6067 核心复现结果</title><style>body{font-family:Arial,"Microsoft YaHei",sans-serif;margin:32px;color:#172b42;line-height:1.6}h1{font-size:26px}h2{font-size:20px;margin-top:30px}table{border-collapse:collapse;font-size:13px}th,td{padding:8px 10px;border-bottom:1px solid #d9e2eb;text-align:right}th{background:#edf3f8}.scroll{overflow:auto}p{max-width:1000px}</style><h1>ECO6067 核心复现结果</h1><p>来源：Card and Krueger (1994), AER 84(4), p.780。当前阶段：核心表格计算与比较；尚未完成最终作业。</p><p><b>注意：</b>Table 3 第3行标准误采用明确的替代实现，未声称完全恢复原文方法。Table 4第五列并列显示论文表格规格和作者核查程序规格；所有权变量的纳入解释了主要系数与标准误的差异。完整解释见核心复现说明.md。</p>'+body+'</html>'
    (out / 'replication_results.html').write_text(page,encoding='utf-8')
    return a, b, c

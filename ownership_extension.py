"""Prespecified ownership heterogeneity extension; no result-based selection."""
import json

import numpy as np
import pandas as pd
from scipy.stats import t as student_t

from replicate_tables import fit_ols


def design(t, chain_controls):
    frame = t[['STATE','CO_OWNED']].astype(float).copy()
    frame['NJ_x_company_owned'] = frame.STATE * frame.CO_OWNED
    if chain_controls:
        frame = pd.concat([frame, pd.get_dummies(t.CHAIN,prefix='chain',drop_first=True,dtype=float)],axis=1)
    return frame


def contrast(fit, name, vector):
    l = np.asarray(vector,dtype=float)
    estimate = float(l @ fit['beta'])
    classical_se = float(np.sqrt(l @ fit['covariance'] @ l))
    hc1_se = float(np.sqrt(l @ fit['hc1_covariance'] @ l))
    critical = float(student_t.ppf(.975,fit['df']))
    p = float(2 * student_t.sf(abs(estimate/hc1_se),fit['df']))
    return {'effect':name,'estimate':estimate,'classical_se':classical_se,
            'hc1_se':hc1_se,'hc1_ci_lower':estimate-critical*hc1_se,
            'hc1_ci_upper':estimate+critical*hc1_se,'hc1_t_approx_p_value':p}


def coverage(t,model):
    rows=[]
    for s,label in [(0,'PA'),(1,'NJ')]:
        for owned,name in [(0,'franchise'),(1,'company_owned')]:
            cell=t[t.STATE.eq(s)&t.CO_OWNED.eq(owned)]
            if len(cell)<2:
                raise ValueError('Insufficient four-cell sample coverage.')
            rows.append({'model':model,'state':label,'ownership':name,'n':len(cell),
                         'mean_baseline_fte':float(cell.fte1.mean()),
                         'mean_change_fte':float(cell.outcome.mean()),
                         'initial_wage_n':int(cell.WAGE_ST.count()),
                         'mean_initial_wage':float(cell.WAGE_ST.mean())})
    return rows


def run_extension(z,out):
    balanced=z[z.table3_balanced].copy()
    primary=z[z.table4_working].copy()
    temporary_mask=z.table3_temporary_zero & z.WAGE_ST.notna() & (z.WAGE_ST2.notna() | z.STATUS2.isin([2,3,4,5]))
    temporary=z[temporary_mask].copy()
    specs=[('unadjusted_balanced',balanced,False,'change_fte'),
           ('primary_chain_adjusted',primary,True,'change_fte'),
           ('broad_balanced_chain_adjusted',balanced,True,'change_fte'),
           ('temporary_closures_zero',temporary,True,'change_fte_temporary_zero')]
    for chain in [1,2,3,4]:
        specs.append((f'exclude_chain_{chain}',primary[primary.CHAIN.ne(chain)].copy(),True,'change_fte'))
    effects,all_coefs,cells=[],[],[]
    primary_fit=None
    four_cell_variance_check=False
    for model,t,chain_controls,outcome in specs:
        t=t.copy()
        t['outcome']=t[outcome]
        cells.extend(coverage(t,model))
        frame=design(t,chain_controls)
        fit=fit_ols(t.outcome,frame)
        k=fit['k']
        franchise=np.zeros(k);franchise[1]=1
        company=franchise.copy();company[3]=1
        difference=np.zeros(k);difference[3]=1
        for name,l in [('franchise_DID',franchise),('company_owned_DID',company),('company_minus_franchise',difference)]:
            effects.append({'model':model,'n':fit['n'],'residual_df':fit['df'],
                            'chain_controls':chain_controls,**contrast(fit,name,l)})
        for term,beta,se,hc1 in zip(fit['terms'],fit['beta'],fit['se'],fit['hc1_se']):
            all_coefs.append({'model':model,'term':term,'coefficient':float(beta),
                              'classical_se':float(se),'hc1_se':float(hc1)})
        if model=='unadjusted_balanced':
            mean=t.groupby(['STATE','CO_OWNED']).outcome.mean()
            franchise_did=float(mean.loc[(1,0)]-mean.loc[(0,0)])
            company_did=float(mean.loc[(1,1)]-mean.loc[(0,1)])
            manual={'franchise_DID':franchise_did,'company_owned_DID':company_did,
                    'company_minus_franchise':company_did-franchise_did}
            current={r['effect']:r['estimate'] for r in effects if r['model']==model}
            if not all(np.isclose(manual[key],current[key],rtol=0,atol=1e-10) for key in manual):
                raise ValueError('Four-cell means and interaction-model coefficients disagree.')
            robust_variance=0.0
            for _,cell in t.groupby(['STATE','CO_OWNED']):
                residual=cell.outcome-cell.outcome.mean()
                robust_variance+=float((residual**2).sum())/len(cell)**2
            robust_variance*=len(t)/(len(t)-4)
            four_cell_variance_check=bool(np.isclose(robust_variance,fit['hc1_covariance'][3,3],rtol=0,atol=1e-10))
            if not four_cell_variance_check:
                raise ValueError('Four-cell direct HC1 variance and sandwich covariance disagree.')
        if model=='primary_chain_adjusted':
            primary_fit=fit
            reversed_t=t.copy()
            reversed_t['CO_OWNED']=1-reversed_t.CO_OWNED
            reversed_fit=fit_ols(reversed_t.outcome,design(reversed_t,True))
            if not np.isclose(reversed_fit['beta'][3],-fit['beta'][3],rtol=0,atol=1e-10):
                raise ValueError('Ownership reference reversal check failed.')
            if not np.isclose(reversed_fit['beta'][1],fit['beta'][1]+fit['beta'][3],rtol=0,atol=1e-10):
                raise ValueError('Company-owned sum contrast coefficient check failed.')
            v=np.zeros(fit['k']);v[1]=v[3]=1
            if not np.isclose(reversed_fit['hc1_covariance'][1,1],v@fit['hc1_covariance']@v,rtol=0,atol=1e-10):
                raise ValueError('Company-owned sum contrast covariance check failed.')
    results=pd.DataFrame(effects)
    results.to_csv(out/'extension_effects.csv',index=False)
    pd.DataFrame(all_coefs).to_csv(out/'extension_all_coefficients.csv',index=False)
    cell_table=pd.DataFrame(cells)
    cell_table.to_csv(out/'extension_sample_cells.csv',index=False)
    chain_rows=[]
    for s,label in [(0,'PA'),(1,'NJ')]:
        for owned,name in [(0,'franchise'),(1,'company_owned')]:
            cell=primary[primary.STATE.eq(s)&primary.CO_OWNED.eq(owned)]
            for c in [1,2,3,4]:
                chain_rows.append({'state':label,'ownership':name,'chain':c,
                                   'n':int(cell.CHAIN.eq(c).sum()),'share':float(cell.CHAIN.eq(c).mean())})
    pd.DataFrame(chain_rows).to_csv(out/'extension_chain_composition.csv',index=False)
    # Complete one-store-deletion check, not cherry-picked outlier exclusions.
    influence=[]
    primary_value=float(primary_fit['beta'][3])
    for index in primary.index:
        t=primary.drop(index=index)
        fit=fit_ols(t.change_fte,design(t,True))
        value=float(fit['beta'][3])
        influence.append({'omitted_store_key':primary.loc[index,'store_key'],
                          'interaction_estimate':value,'change_from_primary':value-primary_value})
    influence=pd.DataFrame(influence)
    # Only aggregate influence diagnostics are exported; no store IDs are needed.
    diagnostics={
        'primary_n':len(primary),'balanced_n':len(balanced),'temporary_zero_n':len(temporary),
        'four_cell_manual_contrasts':manual,
        'four_cell_mean_vs_regression_check':True,
        'four_cell_direct_variance_vs_HC1_check':four_cell_variance_check,
        'ownership_reference_reversal_check':True,
        'sum_contrast_uses_covariance':True,
        'coefficient_and_covariance_independent_checks':'Passed for every main, sensitivity and store-deletion model via shared fit_ols.',
        'sensitivity_specifications':[r[0] for r in specs],
        'store_deletion_count':len(influence),
        'store_deletion_interaction_min':float(influence.interaction_estimate.min()),
        'store_deletion_interaction_max':float(influence.interaction_estimate.max()),
        'store_deletion_max_absolute_change':float(influence.change_from_primary.abs().max()),
        'uncertainty':'HC1 plus residual-df Student t approximation; restaurant-level model diagnostics only.',
        'identification':'No pre-trend test is possible. Two states and potential ownership-specific state shocks prevent strong causal heterogeneity conclusions.'
    }
    (out/'extension_checks.json').write_text(json.dumps(diagnostics,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    r=results[results.model.eq('primary_chain_adjusted')].set_index('effect')
    d=r.loc['company_minus_franchise'];f=r.loc['franchise_DID'];c=r.loc['company_owned_DID']
    if d.hc1_ci_lower<=0<=d.hc1_ci_upper:
        conclusion='直营店与加盟店之间的差异估计不精确；置信区间包含0，当前分析没有清晰识别两类店反应不同的证据。不能因此认定两类店效果相同。'
    else:
        conclusion='直营店与加盟店的差异在餐厅级模型诊断中不包含0；仍不能把它直接确认为州级政策导致的因果差异。'
    cell_lines=['| State | Ownership | N | Baseline FTE | Change FTE | Initial wage |','| --- | --- | ---: | ---: | ---: | ---: |']
    for _,row in cell_table[cell_table.model.eq('primary_chain_adjusted')].iterrows():
        cell_lines.append(f'| {row.state} | {row.ownership} | {row.n} | {row.mean_baseline_fte:.2f} | {row.mean_change_fte:.2f} | {row.mean_initial_wage:.2f} |')
    main_lines=['| Contrast | Estimate | Classical SE | HC1 SE | HC1 95% CI | HC1 approximate p |','| --- | ---: | ---: | ---: | --- | ---: |']
    for effect in ['franchise_DID','company_owned_DID','company_minus_franchise']:
        row=r.loc[effect]
        main_lines.append(f'| {effect} | {row.estimate:.3f} | {row.classical_se:.3f} | {row.hc1_se:.3f} | [{row.hc1_ci_lower:.3f}, {row.hc1_ci_upper:.3f}] | {row.hc1_t_approx_p_value:.3f} |')
    sensitivity=['| Specification | N | Company minus franchise | HC1 95% CI | HC1 approximate p |','| --- | ---: | ---: | --- | ---: |']
    for _,row in results[results.effect.eq('company_minus_franchise')].iterrows():
        sensitivity.append(f'| {row.model} | {row.n} | {row.estimate:.3f} | [{row.hc1_ci_lower:.3f}, {row.hc1_ci_upper:.3f}] | {row.hc1_t_approx_p_value:.3f} |')
    report=f'''# ECO6067 独立拓展：直营店与加盟店的就业反应

## Research question / 研究问题

Does the employment response to the minimum-wage increase differ between
company-owned and franchised restaurants?
最低工资提高后，直营店与加盟店的就业反应是否不同？

本问题在初始方案中已确定。估计前另将具体模型和检验规则写入
docs/extension_plan.md并完成Git提交，不依据显著性挑选问题或模型。
不同所有权可能对应不同管理与调整方式，这是动机而非本数据已验证的机制。

## Empirical design / 研究方法

ΔFTE = a + b×NJ + c×CO_OWNED + d×(NJ×CO_OWNED) + chain controls + error.
ΔFTE为同一家餐厅的政策后减政策前就业变化；CO_OWNED是政策前所有权。
b是加盟店DID，b+d是直营店DID，d直接检验“直营店DID减加盟店DID”。
单位均为全职当量／店。检验d=0，不比较两组各自的显著性来推断差异。

主要模型使用与Table 4一致的357家餐厅，控制三个品牌指示变量。
标准误不照搬核心表格：并列显示常规OLS和HC1，主置信区间用HC1及残差自由度
的t近似。它们是餐厅级模型诊断，不能解决只有两个州的政策层面推断局限。

## Sample coverage / 样本覆盖

以下均值都使用主要模型的同一357家样本，不能与Table 3全样本均值直接混用。

{chr(10).join(cell_lines)}

品牌构成另见extension_chain_composition.csv。样本数和品牌控制并不保证
两类店在其他方面可比；地理位置或所有权类别的不同冲击仍可能影响结果。

## Main results / 主要结果

{chr(10).join(main_lines)}

直观说明：加盟店的调整后DID为{f.estimate:.2f}，直营店为{c.estimate:.2f}；
直营店减加盟店为{d.estimate:.2f}，其95%区间为
[{d.hc1_ci_lower:.2f}, {d.hc1_ci_upper:.2f}]，近似p值{d.hc1_t_approx_p_value:.3f}。
这些是调整后的相对变化，不表示每家餐厅都增加了该数量员工。

{conclusion}

The ownership interaction is estimated at {d.estimate:.3f} FTE per store
(HC1 SE {d.hc1_se:.3f}; 95% interval [{d.hc1_ci_lower:.3f}, {d.hc1_ci_upper:.3f}]).
These restaurant-level diagnostics should not be interpreted as definitive
policy-level inference or evidence that ownership effects are identical.

## Sensitivity checks / 稳健性检查

{chr(10).join(sensitivity)}

unadjusted_balanced是384家餐厅、无品牌控制的原始四组比较；
broad_balanced_chain_adjusted仍是384家，检查工资完整性筛选的影响；
temporary_closures_zero将暂时关闭店记为0，并为关闭店豁免第二期工资要求；
exclude_chain_1至4分别排除Burger King、KFC、Roy Rogers、Wendy's。
所有敏感性模型的四组样本量另见extension_sample_cells.csv；未挑选“最显著”版本。

逐一删除357家主要样本餐厅，交互项范围为
[{diagnostics['store_deletion_interaction_min']:.3f}, {diagnostics['store_deletion_interaction_max']:.3f}]，
最大绝对变化为{diagnostics['store_deletion_max_absolute_change']:.3f}。
这只说明单店对点估计的影响，不能证明结论对所有模型选择都稳健。

## Validation and limitations / 检查与局限

1. 直接用四组均值计算得到加盟店DID {manual['franchise_DID']:.6f}、
   直营店DID {manual['company_owned_DID']:.6f}，差异
   {manual['company_minus_franchise']:.6f}；与同样本交互回归一致。
2. 直营店效果b+d的标准误使用两系数间的协方差，没有直接把标准误相加。
   将直营／加盟的参照编码反转后，系数和方差再次核对一致；四组残差直接计算
   的HC1方差也与回归协方差一致。
3. 所有模型核对独立系数求解、独立协方差计算、矩阵满秩与残差正交。
4. 只有一次政策前调查，不能检验各所有权类别的政策前平行趋势。
   所有权特有的NJ冲击可能与交互项混淆；品牌控制不能排除全部混淆。
5. 只调查原本存在的餐厅，不能用本结果衡量政策对新店进入或长期就业的影响。
6. 此分析展示的是预先确定的问题、透明方法和不确定性；不以显著结果作为成功标准。

## Next step / 下一阶段

核心复现与独立拓展已计算，下一阶段整合英文实证报告、AI披露及最终提交说明。
本文件仍是阶段分析说明；GitHub尚未发布，课程的指定表图、报告字数与语言
仍须按课程补充要求核对。无需进行学生理解测验。
'''
    (out/'独立拓展说明.md').write_text(report,encoding='utf-8')
    return results,diagnostics

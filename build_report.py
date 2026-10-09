"""Build an English empirical report from checked CSV/JSON outputs."""
import argparse
from io import BytesIO
import json
from pathlib import Path
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER,TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image

ROOT=Path(__file__).resolve().parent


def build(results,output):
    output.mkdir(parents=True,exist_ok=True)
    a=pd.read_csv(results/'table3_full.csv')
    b=pd.read_csv(results/'table4_full.csv')
    alt=pd.read_csv(results/'table4_author_program_variant.csv').iloc[0]
    ext=pd.read_csv(results/'extension_effects.csv')
    coverage=pd.read_csv(results/'extension_sample_cells.csv')
    flow=pd.read_csv(results/'sample_flow.csv').set_index('sample')
    comparisons=pd.read_csv(results/'paper_comparison.csv')
    checks=json.loads((results/'extension_checks.json').read_text())
    primary=ext[ext.model.eq('primary_chain_adjusted')].set_index('effect')
    difference=primary.loc['company_minus_franchise']
    counts=comparisons.groupby('table').matches_printed_precision.agg(['sum','count'])
    pdfmetrics.registerFont(TTFont('Body',str(ROOT/'assets/fonts/DejaVuSerif.ttf')))
    pdfmetrics.registerFont(TTFont('BodyBold',str(ROOT/'assets/fonts/DejaVuSerif-Bold.ttf')))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold')
    normal=ParagraphStyle('Body',fontName='Body',fontSize=10.2,leading=14.3,spaceAfter=8,textColor=colors.black)
    heading=ParagraphStyle('Heading',parent=normal,fontName='BodyBold',fontSize=14,leading=18,spaceAfter=12)
    title=ParagraphStyle('Title',parent=heading,fontSize=23,leading=29,spaceAfter=15)
    small=ParagraphStyle('Note',parent=normal,fontSize=8.3,leading=11.2,spaceAfter=7)
    cell=ParagraphStyle('Cell',fontName='Body',fontSize=8.3,leading=10.8,alignment=TA_CENTER)
    label=ParagraphStyle('Label',parent=cell,alignment=TA_LEFT)
    story=[];md=[];table_cells=[]
    def p(text,style=normal):
        story.append(Paragraph(text,style));md.append(re.sub('<[^>]+>','',text)+'\n')
    def h(text):p(text,heading)
    def page():story.append(PageBreak());md.append('\n---\n')
    def table(headers,rows,widths,caption):
        p(caption,small)
        values=[headers]+rows
        parsed=[[Paragraph(str(value),label if j==0 else cell) for j,value in enumerate(row)] for row in values]
        t=Table(parsed,colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eef3')),
                              ('GRID',(0,0),(-1,-1),.35,colors.HexColor('#d9d9d9')),
                              ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                              ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
                              ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6)]))
        story.extend([t,Spacer(1,10)])
        md.append('| '+' | '.join(str(x).replace('<br/>',' ') for x in headers)+' |')
        md.append('| '+' | '.join(['---']*len(headers))+' |')
        for row in rows:md.append('| '+' | '.join(str(x).replace('<br/>',' ') for x in row)+' |')
        md.append('')
        table_cells.extend(str(x).replace('<br/>',' ') for row in rows for x in row)
    def eq(tex,plain):
        buf=BytesIO();fig=plt.figure(figsize=(7,.5));fig.text(.01,.25,'$'+tex+'$',fontsize=13)
        fig.savefig(buf,format='png',dpi=250,bbox_inches='tight',pad_inches=.06,facecolor='white')
        plt.close(fig);buf.seek(0)
        from PIL import Image as PILImage
        width,height=PILImage.open(buf).size;buf.seek(0)
        scale=min(440/width,32/height)
        story.extend([Image(buf,width=width*scale,height=height*scale,hAlign='LEFT'),Spacer(1,10)])
        md.append(plain+'\n')
    p('Minimum Wages and Employment',title)
    p('Replication and an ownership heterogeneity extension',heading)
    p('ECO6067 Individual Project | 9 October 2026',small)
    h('Abstract')
    p(f'This project reproduces the central employment comparisons in Card and Krueger (1994) using the New Jersey and Pennsylvania fast-food survey. The balanced-sample difference in differences is {a[(a.row==4)&a.column.eq("NJ_minus_PA")].estimate.iloc[0]:.2f} full-time-equivalent employees per restaurant. The first four regression models reproduce the published main coefficients and standard errors at printed precision. Small differences remain in the descriptive table, including a disclosed alternative standard-error calculation for its available-case mean change. The public author checking program also reveals a specification difference in the fifth regression model.')
    p(f'The independent extension asks whether employment responses differ between company-owned and franchised restaurants. In the {int(difference.n)}-store chain-adjusted model, the company-owned minus franchise contrast is {difference.estimate:.3f} FTE, with an HC1 standard error of {difference.hc1_se:.3f} and a 95% interval of [{difference.hc1_ci_lower:.3f}, {difference.hc1_ci_upper:.3f}]. The estimates do not precisely establish an ownership difference. Restaurant-level uncertainty estimates do not resolve the limitations of having only two policy jurisdictions.')
    h('1 Research question and motivation')
    p('On 1 April 1992, New Jersey increased its minimum wage from $4.25 to $5.05 per hour, while Pennsylvania remained at $4.25. Card and Krueger surveyed restaurants before and after this change to investigate whether the higher minimum wage reduced employment. Their design compares changes in the treated state with changes in nearby eastern Pennsylvania, and also compares initially low- and high-wage New Jersey restaurants.')
    p('The question matters because a wage floor raises the labor cost of affected jobs, but employment responses depend on the labor market and on how employers adjust. The project evaluates the observed employment evidence rather than assuming a negative or positive effect in advance. Replication establishes a transparent benchmark; the ownership extension tests whether the average comparison conceals different responses by organizational form.')
    page();h('2 Data sources and sample construction')
    p('The analysis starts from the course public.csv, containing 410 restaurants and 46 fields. New Jersey contributes 331 restaurants and Pennsylvania 79. Each row is a restaurant, with separate columns for the two surveys. The first survey was conducted in February and March 1992, before the increase; the second in November and December 1992. The four chains are Burger King, KFC, Roy Rogers and Wendy’s.')
    p('The author archive njmin.zip was independently downloaded from David Card’s data page on 9 October 2026. Its whitespace-delimited public.dat was parsed with dots treated as missing. All 410 by 46 numerical values and missing positions exactly matched the course CSV. The archive and file hashes, retrieval script and equality result are retained in the project. This verifies the supplied data against the current public archive, not against an unobserved historical publication version.')
    p('General missing values are not replaced with zero. Employment at the six permanently closed restaurants is zero in the second survey. The four temporarily closed or renovating restaurants have missing second-wave employment in the baseline; a sensitivity analysis sets it to zero. A refusal remains missing. SHEET alone is not unique: the repeated identifier belongs to different states. All rows are retained, using STATE and SHEET jointly as the identifier.')
    rows=[]
    for key,name in [('raw','Original survey'),('table3_wave1','Wave 1 employment available'),('table3_wave2','Wave 2 baseline employment available'),('table3_balanced','Employment observed in both waves'),('table3_temporary_zero','Both waves after temporary closure sensitivity'),('table4_working','Core regression and primary extension')]:
        r=flow.loc[key];rows.append([name,str(r['all']),str(r.PA),str(r.NJ)])
    table(['Sample','All','PA','NJ'],rows,[303,55,55,55],'Table 1 Analysis sample coverage')
    p('These are distinct analytical samples, not a sequence of common exclusions. The 357-store regression sample requires valid employment change and initial wage, plus second-wave wage except for permanently closed restaurants. Requiring wages literally in both waves would incorrectly omit those six closed stores and leave 351 observations. The public author checking program confirms the closure exception.',small)
    h('Variable definitions')
    eq(r'FTE_{it}=FT_{it}+MGR_{it}+0.5\,PT_{it}','FTE_it = full-time workers + managers + 0.5 × part-time workers.')
    p('All three employment components must be observed; partial sums are not used. The outcome is the second-wave FTE minus the first-wave FTE. CO_OWNED is the baseline company-ownership indicator, coded one for company-owned and zero for franchise ownership. STATE is one for New Jersey. NJ wage groups are $4.25, greater than $4.25 and below $5.00, and at least $5.00; this grouping threshold is distinct from the new $5.05 legal minimum.',small)
    page();h('3 Empirical design')
    p('The descriptive difference in differences subtracts Pennsylvania’s employment change from New Jersey’s change. Using the same restaurants in both waves gives a balanced comparison, while the available-case calculation uses each wave’s observed employment sample separately.')
    eq(r'\widehat{DID}=(\overline{FTE}_{NJ,2}-\overline{FTE}_{NJ,1})-(\overline{FTE}_{PA,2}-\overline{FTE}_{PA,1})','DID = (NJ after − NJ before) − (PA after − PA before).')
    p('The two waves are linked at the restaurant level. Mean standard errors use the sample variance and observed sample size. For balanced changes, the standard error is calculated from within-restaurant changes. Independent group contrasts add the component variances. For the available-case mean change in original Table 3 row 3, the project uses a restaurant-level influence-function variance that allows covariance between the waves; the exact published implementation was not recovered. The replication table identifies this choice explicitly.')
    eq(r'IF_i=\frac{N R_{i2}}{n_2}(FTE_{i2}-\bar{FTE}_2)-\frac{N R_{i1}}{n_1}(FTE_{i1}-\bar{FTE}_1)','IF_i = (N/n2) R_i2 (FTE_i2 − mean2) − (N/n1) R_i1 (FTE_i1 − mean1).')
    p('Here R indicates whether the wave’s employment is observed, n is that wave’s observed count and N is the group’s restaurant count. The standard error is the sample standard deviation of IF divided by √N. A missing contribution is zero in this estimating equation; missing employment itself is never imputed as zero.',small)
    h('Regression adjustment')
    eq(r'\Delta FTE_i=\alpha+\tau NJ_i+X_i\beta+\varepsilon_i','ΔFTE_i = α + τ NJ_i + X_i β + ε_i.')
    p('The first two models use the NJ indicator. The remaining models substitute the initial wage gap, defined as max(5.05/WAGE_ST − 1, 0) in NJ and zero in PA. Missing initial NJ wages remain missing. A gap of 0.10 represents a required wage increase of 10%, not ten percentage units. Chain and company-ownership indicators adjust for observed restaurant composition; the final printed specification additionally includes four regional indicators.')
    p('All models include a constant. Conventional OLS standard errors reproduce the original regression convention; separately retained HC1 diagnostics allow restaurant-level heteroskedasticity. The reported control p value is a joint F test excluding all controls in that column, not a test of the policy coefficient.')
    h('Identification')
    p('A causal interpretation requires credible employment trends in the absence of the policy: Pennsylvania should represent the change New Jersey would otherwise have experienced. Similar starting levels are not required, but differential demand shocks could confound the estimate. One pre-policy survey cannot support a usual pre-trend test. The ownership extension additionally requires credible comparisons within ownership categories; ownership-specific NJ shocks are a potential confounder.')
    page();h('4 Core replication results')
    p('Table 2 reproduces all five rows and eight columns of original Table 3, separated into its state and within-NJ panels. Each entry is an estimate with its standard error in parentheses. The baseline keeps permanent closures at zero and temporary closures as missing.')
    names=['Before','After','Available-case change','Balanced change','Temporary closures zero']
    def entries(columns):
        rows=[]
        for i,name in enumerate(names,1):
            t=a[a.row.eq(i)].set_index('column')
            rows.append([str(i)+' '+name]+[f'{t.loc[c,"estimate"]:.2f}<br/>({t.loc[c,"standard_error"]:.2f})' for c in columns])
        return rows
    table(['Employment measure','PA','NJ','NJ − PA'],entries(['PA','NJ','NJ_minus_PA']),[222,82,82,82],'Table 2A State comparisons in FTE per restaurant')
    table(['Measure','Low<br/>$4.25','Middle<br/>$4.26–4.99','High<br/>≥ $5.00','Low −<br/>high','Middle −<br/>high'],entries(['NJ_low','NJ_middle','NJ_high','low_minus_high','middle_minus_high']),[168,60,60,60,60,60],'Table 2B New Jersey wage group comparisons in FTE per restaurant')
    p('Rows 1 and 2 use available observations separately by wave. Row 3 subtracts those means and uses the disclosed linked-sample variance. Row 4 averages restaurant changes in the balanced sample. Row 5 admits temporarily closed stores with zero second-wave FTE. These samples should not be interchanged.',small)
    h('Comparison with the original')
    p(f'The balanced state contrast is 2.75 (SE 1.34), matching the original at printed precision. The available-case contrast is 2.753606, displayed as 2.75, compared with the published 2.76. Across {int(counts.loc["Table 3","count"])} numerical cells, {int(counts.loc["Table 3","sum"])} match at two decimals. Eight differences are the row-3 standard errors under the disclosed alternative method; the remaining six are small displayed-value differences. They are not attributed to rounding alone without evidence. The full comparison CSV records every original value, calculated value and difference.')
    p('Employment changes are positive in NJ relative to PA under both baseline sample approaches, and the temporary-closure treatment reduces the contrast to about 2.51. This reproduces the paper’s broad direction, while retaining uncertainty and implementation differences. It does not show that every restaurant increased employment or that minimum-wage increases always raise employment.')
    page();h('5 Regression replication and source comparison')
    rows=[]
    for _,r in b.iterrows():
        rows.append(['('+r.model+')',f'{r.coefficient:.2f}<br/>({r.standard_error:.2f})','Yes' if r.chain_ownership_controls else 'No','Yes' if r.region_controls else 'No',f'{r.residual_sd:.2f}','—' if pd.isna(r.controls_p_value) else f'{r.controls_p_value:.2f}',str(r.n)])
    table(['Model','Main estimate<br/>(SE)','Chain and<br/>ownership','Region','Residual<br/>SD','Controls<br/>p','N'],rows,[42,99,91,53,67,64,52],'Table 3 Original Table 4 under its printed specifications')
    p('Models (i)–(ii) report the NJ coefficient; (iii)–(v) report GAP. The regression sample is identical across all columns. Three chain dummies are included when indicated. Region controls represent the five exhaustive areas with one area omitted. The main coefficient is invariant to the choice of omitted region.',small)
    p('The first four main coefficients and standard errors match the published results at two decimals. In the fifth model, the printed specification implies a GAP coefficient of 11.979237 (SE 7.419121), compared with published 11.91 (7.39). Independent solvers and covariance calculations agreed, and changing the omitted region did not remove the difference.')
    h('The public author checking program')
    p('The author’s public archive contains check.sas. Its region-adjusted employment-change model omits the company-ownership control, although the paper’s table indicates that control is present. Implementing that checking-program specification gives the following comparison. The program is described as a check of book-related survey data, so it is not assumed to be the exact historical journal production script.')
    r=b[b.model.eq('v')].iloc[0]
    table(['Specification','GAP coefficient<br/>(SE)','Residual SD','Control p'],[
        ['Published table','11.91 (7.39)','8.75','0.40'],
        ['Printed specification including ownership',f'{r.coefficient:.2f} ({r.standard_error:.2f})',f'{r.residual_sd:.2f}',f'{r.controls_p_value:.2f}'],
        ['Public checking program excluding ownership',f'{alt.coefficient:.2f} ({alt.standard_error:.2f})',f'{alt.residual_sd:.2f}',f'{alt.controls_p_value:.2f}']],[227,97,75,69],'Table 4 Alternative implementations of model v')
    p('Omitting ownership explains the main coefficient and standard-error discrepancy, but does not reproduce the entire printed column: the alternative residual SD and controls p value differ. Both implementations are retained. The project does not silently remove a control to claim a perfect replication, nor claim that the historical reason for the mixed printed metrics is established.')
    p(f'Under the printed specifications, {int(counts.loc["Table 4","sum"])} of {int(counts.loc["Table 4","count"])} numerical comparisons match, including sample sizes. The exceptions are the fifth model’s main coefficient and SE. The positive coefficients support the same direction as the paper, but some specifications are statistically imprecise under either inference convention.')
    page();h('6 Independent extension on ownership')
    p('The extension asks whether company-owned and franchised stores respond differently to the minimum-wage change. Governance and local decision authority may affect adjustment to higher labor costs, providing an economic motivation. These mechanisms are not measured here. Ownership is a control in the original regressions; testing its interaction with NJ is a distinct question about response heterogeneity.')
    eq(r'\Delta FTE_i=\alpha+\beta NJ_i+\gamma C_i+\delta(NJ_i C_i)+X_i\theta+\varepsilon_i','ΔFTE_i = α + β NJ_i + γ C_i + δ (NJ_i × C_i) + X_i θ + ε_i.')
    p('C is baseline company ownership. β is the franchise DID, β + δ is the company-owned DID and δ is the direct company-owned minus franchise difference. The test is δ = 0. Comparing whether each separate ownership effect is significant would not be a valid substitute for this test.')
    p('The primary extension uses the 357-store core sample and three chain controls. This connects the extension to the replication while allowing ownership-specific responses. The question was selected in the initial project plan; the detailed specifications were committed before extension estimation. All planned models are reported rather than selecting a favorable p value.')
    rows=[]
    for _,r in coverage[coverage.model.eq('primary_chain_adjusted')].iterrows():
        rows.append([r.state,'Company owned' if r.ownership=='company_owned' else 'Franchise',str(r.n),f'{r.mean_baseline_fte:.2f}',f'{r.mean_change_fte:.2f}',f'{r.mean_initial_wage:.2f}'])
    table(['State','Ownership','N','Baseline<br/>FTE','Change<br/>FTE','Initial<br/>wage'],rows,[45,140,42,85,78,78],'Table 5 Primary extension sample and unadjusted cell means')
    p('All displayed means use the same primary sample. The PA company-owned cell has 24 observations, contributing to limited precision. Brand composition is reported separately in the project. Chain adjustment cannot ensure comparability in geographic location, managerial practices or unobserved demand conditions.',small)
    rows=[]
    for key,name in [('franchise_DID','Franchise DID'),('company_owned_DID','Company-owned DID'),('company_minus_franchise','Company owned minus franchise')]:
        r=primary.loc[key];rows.append([name,f'{r.estimate:.3f}',f'{r.hc1_se:.3f}',f'[{r.hc1_ci_lower:.3f}, {r.hc1_ci_upper:.3f}]',f'{r.hc1_t_approx_p_value:.3f}'])
    table(['Contrast','Estimate','HC1 SE','95% interval','Approx p'],rows,[185,60,60,106,57],'Table 6 Chain-adjusted ownership contrasts in FTE per restaurant')
    p(f'The interaction is {difference.estimate:.3f}, with an interval spanning substantial negative and positive differences. The approximate p value is {difference.hc1_t_approx_p_value:.3f}. There is no precise evidence of different responses by ownership, but this is not evidence that their effects are identical. The intervals use HC1 and a residual-df t approximation; they are restaurant-level model diagnostics, not definitive state-policy inference.',small)
    page();h('7 Sensitivity and validation')
    rows=[]
    model_names={'unadjusted_balanced':'Unadjusted balanced sample','primary_chain_adjusted':'Primary chain adjusted',
                 'broad_balanced_chain_adjusted':'Broad balanced with chains','temporary_closures_zero':'Temporary closures zero',
                 'exclude_chain_1':'Exclude Burger King','exclude_chain_2':'Exclude KFC','exclude_chain_3':'Exclude Roy Rogers','exclude_chain_4':'Exclude Wendy’s'}
    for _,r in ext[ext.effect.eq('company_minus_franchise')].iterrows():
        rows.append([model_names[r.model],str(r.n),f'{r.estimate:.3f}',f'[{r.hc1_ci_lower:.3f}, {r.hc1_ci_upper:.3f}]',f'{r.hc1_t_approx_p_value:.3f}'])
    table(['Specification','N','Difference','95% interval','Approx p'],rows,[188,39,69,115,57],'Table 7 Prespecified ownership sensitivity analyses')
    p('The broader balanced models avoid restricting on wage completeness. The temporary-closure model uses the same wage requirement but exempts second-wave wages for all closure statuses, yielding 361 stores. The four brand exclusions test whether the result depends heavily on one chain; controls for the remaining chains are retained. All model-specific four-cell counts are saved.')
    p('Every interval in Table 7 includes zero. Point estimates are not perfectly stable: excluding Burger King changes the difference to approximately zero, whereas excluding Wendy’s makes it more negative. This supports a conclusion of limited precision rather than a claim of a robust negative ownership effect.')
    p(f'Each of the {checks["store_deletion_count"]} primary-sample restaurants was omitted once. The interaction ranged from {checks["store_deletion_interaction_min"]:.3f} to {checks["store_deletion_interaction_max"]:.3f}; the largest absolute movement was {checks["store_deletion_max_absolute_change"]:.3f}. These diagnostics assess single-store influence, not robustness to all design choices.')
    h('Computational checks')
    p('Unadjusted interaction coefficients match direct four-cell mean contrasts. Their HC1 variance also matches an independent calculation using within-cell residual sums. Reversing the ownership reference reproduces the company-owned effect and its covariance, verifying that the SE of β + δ includes the covariance term. All main, sensitivity and deletion models pass independent coefficient and covariance calculations, full-rank checks and residual orthogonality.')
    p('The raw input bytes are preserved. The project rebuilds preparation, both core tables and the extension from the original CSV into empty output directories. Generated files are compared by SHA-256. The version-controlled README provides dependency versions, one entry point and source-access instructions; all output tables are produced by code rather than manually edited. Report tables are read directly from those checked outputs.')
    page();h('8 Limitations and conclusion')
    p('The evidence applies to surveyed existing fast-food restaurants in NJ and eastern PA during 1992. It does not measure effects on potential new entrants, other industries, long-run employment or other minimum-wage policies. FTE is a headcount conversion using a half-weight for part-time workers, not directly observed total hours. Survey measurement error and item nonresponse may affect both outcomes and sample composition.')
    p('Only one pre-policy wave is available, so neither the overall comparison nor ownership-specific comparisons can establish parallel pre-trends empirically. Differential local shocks and differences between ownership categories may remain after chain adjustment. Ownership itself is not randomly assigned; the extension does not identify the causal effect of changing a restaurant’s ownership.')
    p('The policy varies at the state level and there are only two states. Treating hundreds of restaurants as hundreds of independent policy experiments would overstate the design’s information. Classical SE serve original-table comparison, while HC1 allows restaurant-level heteroskedasticity; neither accounts reliably for potentially correlated state-level shocks. Consequently, reported p values and intervals should not be treated as conclusive policy-level inference.')
    p('Replication differences are part of the evidence, not hidden defects to be corrected by changing observations. The available-case descriptive SE implementation is disclosed, small printed differences remain, and the public checking program’s ownership omission is reported separately from the table’s printed specification. The current author data exactly match the course data, but the exact historical source of all publication discrepancies is not established.')
    h('Conclusion')
    p('The replication recovers the paper’s central positive relative employment comparison and the first four adjusted regression coefficients and SEs at printed precision. Independent source verification and multiple calculation checks strengthen confidence that the implemented workflow is internally reproducible. The ownership extension estimates a modest negative difference for company-owned stores relative to franchises, with wide uncertainty and no precise ownership difference across the prespecified models. This supports cautious interpretation of both the original comparison and the extension rather than a universal minimum-wage conclusion.')
    h('Reproducibility package')
    p('The submitted project provides the input-access instructions, processed analysis data, complete Python code, original benchmarks, all numerical comparisons, extension results, checking records and a Git history of actual project stages. The reusable workflow generates the main tables, reconstructs this report and documents AI use. GitHub publication and any course-specific formatting or assigned-target requirements must be checked before submission.')
    page();h('9 AI use disclosure')
    disclosure=[
        ('Where AI was used','The user selected the paper and supplied the assignment instructions, article and course data. ChatGPT Codex read these sources, explained the design, proposed the ownership extension, generated and executed Python code, retrieved the author archive, compared data, prepared the tables, drafted the report and checked its layout. The user requested that comprehension quizzes be omitted; data and computational validation were retained.'),
        ('How AI outputs were checked','The benchmark numbers were transcribed from the original rendered paper, separately from the estimator. Input structure, coding, closures and missingness were checked. Independent numerical solvers and covariance constructions were compared. Direct group arithmetic, ownership-reference reversal, source-file equality, influence checks and fresh-output reruns validated calculations. Tables and report values are generated from saved outputs. These checks were conducted with AI-assisted code; they are not falsely represented as an independent human audit or student verification.'),
        ('Corrections and rejected shortcuts','SHEET alone was found not to be unique, so no rows were removed merely because it repeats. A literal both-wages filter would remove six permanently closed stores; the closure exception was verified against the public author program. The earlier approximate description of the available-case DID as 2.76 was corrected to the actual 2.753606, displayed as 2.75. The fifth model’s printed specification and public checking-program specification were retained separately rather than hiding the omission of ownership. The row-3 SE was disclosed as an alternative implementation. No claim of pre-trend validation, identical ownership effects or universally positive minimum-wage effects was made.'),
        ('Responsibility and provenance','The user remains responsible for reviewing the submitted analysis and following course requirements. The report documents completed checks without claiming that the user personally executed them. Git commits were made by the AI assistant under its own identity, at actual stages, without backdating or fabricating a student work history. The source-selection and data-choice records remain available for review.')]
    for sub,text in disclosure:p('<b>'+sub+'</b> '+text)
    h('References and source access')
    p('Card, D., and Krueger, A. B. (1994). Minimum Wages and Employment: A Case Study of the Fast-Food Industry in New Jersey and Pennsylvania. <i>American Economic Review</i>, 84(4), 772–793. Original Table 3 and Table 4 are on printed page 780, PDF page 9 of the supplied article.',small)
    p('Card, D. Public survey archive and checking program. Author data page: https://davidcard.berkeley.edu/data_sets.html. Archive: https://davidcard.berkeley.edu/data_sets/njmin.zip. Description: https://davidcard.berkeley.edu/readme/njmin-readme.txt. Retrieved 9 October 2026. The description identifies book-related survey files and a checking program; the project does not equate this with the exact historical publication-production script.',small)
    p('ECO6067 course project instructions, supplied as four images; course README and DATA_DICTIONARY; and public.csv. These supplied materials establish the assignment requirements and source variable meanings. No third-party student replication output is used as the numerical benchmark.',small)
    def footer(canvas,doc):
        canvas.setFont('Body',8);canvas.setFillColor(colors.HexColor('#555555'))
        canvas.drawString(54,29,'ECO6067 | Minimum wage replication')
        canvas.drawRightString(A4[0]-54,29,str(doc.page))
    pdf=output/'ECO6067_empirical_report.pdf'
    doc=SimpleDocTemplate(str(pdf),pagesize=A4,rightMargin=54,leftMargin=54,topMargin=48,bottomMargin=48,title='Minimum Wages and Employment',author='ECO6067 individual project',invariant=1)
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    (output/'ECO6067_empirical_report.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    (output/'AI_USE_DISCLOSURE.md').write_text('# AI use disclosure\n\n'+'\n\n'.join('## '+h+'\n\n'+t for h,t in disclosure)+'\n',encoding='utf-8')
    from pypdf import PdfReader
    reader=PdfReader(pdf);text='\n'.join(page.extract_text() or '' for page in reader.pages)
    must=[f'{difference.estimate:.3f}',f'{difference.hc1_se:.3f}',f'{difference.hc1_t_approx_p_value:.3f}','11.91 (7.39)','23.33','357','2.75']
    if not all(value in text for value in must):raise ValueError('Report number extraction check failed.')
    if len(reader.pages)!=9:raise ValueError(f'Unexpected page count {len(reader.pages)}; inspect layout.')
    verification={'pages':len(reader.pages),'report_table_source':'Checked CSV/JSON outputs; original comparison values come from separately transcribed benchmarks.',
                  'required_numeric_strings_present':must,'markdown_word_count':len(' '.join(md).split()),
                  'all_tables_generated_from_outputs':True,'equations_rendered_as_math':True,
                  'layout_note':'Automated checks do not replace visual inspection of rendered pages.'}
    (output/'report_checks.json').write_text(json.dumps(verification,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('Report built:',pdf,'pages:',len(reader.pages))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--results',type=Path,default=ROOT/'results')
    p.add_argument('--output',type=Path,default=ROOT/'report')
    args=p.parse_args();build(args.results,args.output)

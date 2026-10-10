Minimum Wages and Employment

Replication and an ownership heterogeneity extension

ECO6067 Individual Project | 9 October 2026

Name: WANG Ruiyue | Student ID: 3036761820

Abstract

This project reproduces the central employment comparisons in Card and Krueger (1994) using the New Jersey and Pennsylvania fast-food survey. The balanced-sample difference in differences is 2.75 full-time-equivalent employees per restaurant. The first four regression models reproduce the published main coefficients and standard errors at printed precision. Small differences remain in the descriptive table, including a disclosed alternative standard-error calculation for its available-case mean change. The public author checking program also reveals a specification difference in the fifth regression model.

The independent extension asks whether employment responses differ between company-owned and franchised restaurants. In the 357-store chain-adjusted model, the company-owned minus franchise contrast is -0.942 FTE, with an HC1 standard error of 2.579 and a 95% interval of [-6.014, 4.129]. The estimates do not precisely establish an ownership difference. Restaurant-level uncertainty estimates do not resolve the limitations of having only two policy jurisdictions.

1 Research question and motivation

On 1 April 1992, New Jersey increased its minimum wage from $4.25 to $5.05 per hour, while Pennsylvania remained at $4.25. Card and Krueger surveyed restaurants before and after this change to investigate whether the higher minimum wage reduced employment. Their design compares changes in the treated state with changes in nearby eastern Pennsylvania, and also compares initially low- and high-wage New Jersey restaurants.

The question matters because a wage floor raises the labor cost of affected jobs, but employment responses depend on the labor market and on how employers adjust. The project evaluates the observed employment evidence rather than assuming a negative or positive effect in advance. Replication establishes a transparent benchmark; the ownership extension tests whether the average comparison conceals different responses by organizational form.


---

2 Data sources and sample construction

The analysis starts from the course public.csv, containing 410 restaurants and 46 fields. New Jersey contributes 331 restaurants and Pennsylvania 79. Each row is a restaurant, with separate columns for the two surveys. The first survey was conducted in February and March 1992, before the increase; the second in November and December 1992. The four chains are Burger King, KFC, Roy Rogers and Wendy’s.

The author archive njmin.zip was independently downloaded from David Card’s data page on 9 October 2026. Its whitespace-delimited public.dat was parsed with dots treated as missing. All 410 by 46 numerical values and missing positions exactly matched the course CSV. The archive and file hashes, retrieval script and equality result are retained in the project. This verifies the supplied data against the current public archive, not against an unobserved historical publication version.

General missing values are not replaced with zero. Employment at the six permanently closed restaurants is zero in the second survey. The four temporarily closed or renovating restaurants have missing second-wave employment in the baseline; a sensitivity analysis sets it to zero. A refusal remains missing. SHEET alone is not unique: the repeated identifier belongs to different states. All rows are retained, using STATE and SHEET jointly as the identifier.

Table 1 Analysis sample coverage

| Sample | All | PA | NJ |
| --- | --- | --- | --- |
| Original survey | 410 | 79 | 331 |
| Wave 1 employment available | 398 | 77 | 321 |
| Wave 2 baseline employment available | 396 | 77 | 319 |
| Employment observed in both waves | 384 | 75 | 309 |
| Both waves after temporary closure sensitivity | 388 | 75 | 313 |
| Core regression and primary extension | 357 | 67 | 290 |

These are distinct analytical samples, not a sequence of common exclusions. The 357-store regression sample requires valid employment change and initial wage, plus second-wave wage except for permanently closed restaurants. Requiring wages literally in both waves would incorrectly omit those six closed stores and leave 351 observations. The public author checking program confirms the closure exception.

Variable definitions

FTE_it = full-time workers + managers + 0.5 × part-time workers.

All three employment components must be observed; partial sums are not used. The outcome is the second-wave FTE minus the first-wave FTE. CO_OWNED is the baseline company-ownership indicator, coded one for company-owned and zero for franchise ownership. STATE is one for New Jersey. NJ wage groups are $4.25, greater than $4.25 and below $5.00, and at least $5.00; this grouping threshold is distinct from the new $5.05 legal minimum.


---

3 Empirical design

The descriptive difference in differences subtracts Pennsylvania’s employment change from New Jersey’s change. Using the same restaurants in both waves gives a balanced comparison, while the available-case calculation uses each wave’s observed employment sample separately.

DID = (NJ after − NJ before) − (PA after − PA before).

The two waves are linked at the restaurant level. Mean standard errors use the sample variance and observed sample size. For balanced changes, the standard error is calculated from within-restaurant changes. Independent group contrasts add the component variances. For the available-case mean change in original Table 3 row 3, the project uses a restaurant-level influence-function variance that allows covariance between the waves; the exact published implementation was not recovered. The replication table identifies this choice explicitly.

IF_i = (N/n2) R_i2 (FTE_i2 − mean2) − (N/n1) R_i1 (FTE_i1 − mean1).

Here R indicates whether the wave’s employment is observed, n is that wave’s observed count and N is the group’s restaurant count. The standard error is the sample standard deviation of IF divided by √N. A missing contribution is zero in this estimating equation; missing employment itself is never imputed as zero.

Regression adjustment

ΔFTE_i = α + τ NJ_i + X_i β + ε_i.

The first two models use the NJ indicator. The remaining models substitute the initial wage gap, defined as max(5.05/WAGE_ST − 1, 0) in NJ and zero in PA. Missing initial NJ wages remain missing. A gap of 0.10 represents a required wage increase of 10%, not ten percentage units. Chain and company-ownership indicators adjust for observed restaurant composition; the final printed specification additionally includes four regional indicators.

All models include a constant. Conventional OLS standard errors reproduce the original regression convention; separately retained HC1 diagnostics allow restaurant-level heteroskedasticity. The reported control p value is a joint F test excluding all controls in that column, not a test of the policy coefficient.

Identification

A causal interpretation requires credible employment trends in the absence of the policy: Pennsylvania should represent the change New Jersey would otherwise have experienced. Similar starting levels are not required, but differential demand shocks could confound the estimate. One pre-policy survey cannot support a usual pre-trend test. The ownership extension additionally requires credible comparisons within ownership categories; ownership-specific NJ shocks are a potential confounder.


---

4 Core replication results

Table 2 reproduces all five rows and eight columns of original Table 3, separated into its state and within-NJ panels. Each entry is an estimate with its standard error in parentheses. The baseline keeps permanent closures at zero and temporary closures as missing.

Table 2A State comparisons in FTE per restaurant

| Employment measure | PA | NJ | NJ − PA |
| --- | --- | --- | --- |
| 1 Before | 23.33 (1.35) | 20.44 (0.51) | -2.89 (1.44) |
| 2 After | 21.17 (0.94) | 21.03 (0.52) | -0.14 (1.08) |
| 3 Available-case change | -2.17 (1.22) | 0.59 (0.47) | 2.75 (1.31) |
| 4 Balanced change | -2.28 (1.25) | 0.47 (0.48) | 2.75 (1.34) |
| 5 Temporary closures zero | -2.28 (1.25) | 0.23 (0.49) | 2.51 (1.35) |

Table 2B New Jersey wage group comparisons in FTE per restaurant

| Measure | Low $4.25 | Middle $4.26–4.99 | High ≥ $5.00 | Low − high | Middle − high |
| --- | --- | --- | --- | --- | --- |
| 1 Before | 19.56 (0.77) | 20.08 (0.84) | 22.25 (1.14) | -2.69 (1.37) | -2.17 (1.41) |
| 2 After | 20.88 (1.01) | 20.96 (0.76) | 20.21 (1.03) | 0.66 (1.44) | 0.74 (1.27) |
| 3 Available-case change | 1.32 (0.81) | 0.87 (0.67) | -2.04 (0.98) | 3.36 (1.27) | 2.91 (1.19) |
| 4 Balanced change | 1.20 (0.82) | 0.71 (0.69) | -2.16 (1.01) | 3.36 (1.30) | 2.87 (1.22) |
| 5 Temporary closures zero | 0.90 (0.87) | 0.49 (0.69) | -2.39 (1.02) | 3.29 (1.34) | 2.88 (1.23) |

Rows 1 and 2 use available observations separately by wave. Row 3 subtracts those means and uses the disclosed linked-sample variance. Row 4 averages restaurant changes in the balanced sample. Row 5 admits temporarily closed stores with zero second-wave FTE. These samples should not be interchanged.

Comparison with the original

The balanced state contrast is 2.75 (SE 1.34), matching the original at printed precision. The available-case contrast is 2.753606, displayed as 2.75, compared with the published 2.76. Across 80 numerical cells, 66 match at two decimals. Eight differences are the row-3 standard errors under the disclosed alternative method; the remaining six are small displayed-value differences. They are not attributed to rounding alone without evidence. The full comparison CSV records every original value, calculated value and difference.

Employment changes are positive in NJ relative to PA under both baseline sample approaches, and the temporary-closure treatment reduces the contrast to about 2.51. This reproduces the paper’s broad direction, while retaining uncertainty and implementation differences. It does not show that every restaurant increased employment or that minimum-wage increases always raise employment.


---

5 Regression replication and source comparison

Table 3 Original Table 4 under its printed specifications

| Model | Main estimate (SE) | Chain and ownership | Region | Residual SD | Controls p | N |
| --- | --- | --- | --- | --- | --- | --- |
| (i) | 2.33 (1.19) | No | No | 8.79 | — | 357 |
| (ii) | 2.30 (1.20) | Yes | No | 8.78 | 0.34 | 357 |
| (iii) | 15.65 (6.08) | No | No | 8.76 | — | 357 |
| (iv) | 14.92 (6.21) | Yes | No | 8.76 | 0.44 | 357 |
| (v) | 11.98 (7.42) | Yes | Yes | 8.75 | 0.40 | 357 |

Models (i)–(ii) report the NJ coefficient; (iii)–(v) report GAP. The regression sample is identical across all columns. Three chain dummies are included when indicated. Region controls represent the five exhaustive areas with one area omitted. The main coefficient is invariant to the choice of omitted region.

The first four main coefficients and standard errors match the published results at two decimals. In the fifth model, the printed specification implies a GAP coefficient of 11.979237 (SE 7.419121), compared with published 11.91 (7.39). Independent solvers and covariance calculations agreed, and changing the omitted region did not remove the difference.

The public author checking program

The author’s public archive contains check.sas. Its region-adjusted employment-change model omits the company-ownership control, although the paper’s table indicates that control is present. Implementing that checking-program specification gives the following comparison. The program is described as a check of book-related survey data, so it is not assumed to be the exact historical journal production script.

Table 4 Alternative implementations of model v

| Specification | GAP coefficient (SE) | Residual SD | Control p |
| --- | --- | --- | --- |
| Published table | 11.91 (7.39) | 8.75 | 0.40 |
| Printed specification including ownership | 11.98 (7.42) | 8.75 | 0.40 |
| Public checking program excluding ownership | 11.91 (7.39) | 8.74 | 0.31 |

Omitting ownership explains the main coefficient and standard-error discrepancy, but does not reproduce the entire printed column: the alternative residual SD and controls p value differ. Both implementations are retained. The project does not silently remove a control to claim a perfect replication, nor claim that the historical reason for the mixed printed metrics is established.

Under the printed specifications, 21 of 23 numerical comparisons match, including sample sizes. The exceptions are the fifth model’s main coefficient and SE. The positive coefficients support the same direction as the paper, but some specifications are statistically imprecise under either inference convention.


---

6 Independent extension on ownership

The extension asks whether company-owned and franchised stores respond differently to the minimum-wage change. Governance and local decision authority may affect adjustment to higher labor costs, providing an economic motivation. These mechanisms are not measured here. Ownership is a control in the original regressions; testing its interaction with NJ is a distinct question about response heterogeneity.

ΔFTE_i = α + β NJ_i + γ C_i + δ (NJ_i × C_i) + X_i θ + ε_i.

C is baseline company ownership. β is the franchise DID, β + δ is the company-owned DID and δ is the direct company-owned minus franchise difference. The test is δ = 0. Comparing whether each separate ownership effect is significant would not be a valid substitute for this test.

The primary extension uses the 357-store core sample and three chain controls. This connects the extension to the replication while allowing ownership-specific responses. The question was selected in the initial project plan; the detailed specifications were committed before extension estimation. All planned models are reported rather than selecting a favorable p value.

Table 5 Primary extension sample and unadjusted cell means

| State | Ownership | N | Baseline FTE | Change FTE | Initial wage |
| --- | --- | --- | --- | --- | --- |
| PA | Franchise | 43 | 26.41 | -2.24 | 4.52 |
| PA | Company owned | 24 | 18.64 | -1.92 | 4.88 |
| NJ | Franchise | 187 | 20.97 | 0.40 | 4.59 |
| NJ | Company owned | 103 | 19.68 | -0.16 | 4.65 |

All displayed means use the same primary sample. The PA company-owned cell has 24 observations, contributing to limited precision. Brand composition is reported separately in the project. Chain adjustment cannot ensure comparability in geographic location, managerial practices or unobserved demand conditions.

Table 6 Chain-adjusted ownership contrasts in FTE per restaurant

| Contrast | Estimate | HC1 SE | 95% interval | Approx p |
| --- | --- | --- | --- | --- |
| Franchise DID | 2.641 | 2.084 | [-1.457, 6.739] | 0.206 |
| Company-owned DID | 1.699 | 1.539 | [-1.328, 4.725] | 0.270 |
| Company owned minus franchise | -0.942 | 2.579 | [-6.014, 4.129] | 0.715 |

The interaction is -0.942, with an interval spanning substantial negative and positive differences. The approximate p value is 0.715. There is no precise evidence of different responses by ownership, but this is not evidence that their effects are identical. The intervals use HC1 and a residual-df t approximation; they are restaurant-level model diagnostics, not definitive state-policy inference.


---

7 Sensitivity and validation

Table 7 Prespecified ownership sensitivity analyses

| Specification | N | Difference | 95% interval | Approx p |
| --- | --- | --- | --- | --- |
| Unadjusted balanced sample | 384 | -1.095 | [-5.869, 3.678] | 0.652 |
| Primary chain adjusted | 357 | -0.942 | [-6.014, 4.129] | 0.715 |
| Broad balanced with chains | 384 | -1.142 | [-5.797, 3.514] | 0.630 |
| Temporary closures zero | 361 | -0.717 | [-5.797, 4.363] | 0.782 |
| Exclude Burger King | 209 | 0.053 | [-6.226, 6.332] | 0.987 |
| Exclude KFC | 283 | -0.359 | [-6.254, 5.537] | 0.905 |
| Exclude Roy Rogers | 267 | -0.698 | [-6.982, 5.586] | 0.827 |
| Exclude Wendy’s | 312 | -1.846 | [-7.162, 3.470] | 0.495 |

The broader balanced models avoid restricting on wage completeness. The temporary-closure model uses the same wage requirement but exempts second-wave wages for all closure statuses, yielding 361 stores. The four brand exclusions test whether the result depends heavily on one chain; controls for the remaining chains are retained. All model-specific four-cell counts are saved.

Every interval in Table 7 includes zero. Point estimates are not perfectly stable: excluding Burger King changes the difference to approximately zero, whereas excluding Wendy’s makes it more negative. This supports a conclusion of limited precision rather than a claim of a robust negative ownership effect.

Each of the 357 primary-sample restaurants was omitted once. The interaction ranged from -1.611 to -0.070; the largest absolute movement was 0.872. These diagnostics assess single-store influence, not robustness to all design choices.

Computational checks

Unadjusted interaction coefficients match direct four-cell mean contrasts. Their HC1 variance also matches an independent calculation using within-cell residual sums. Reversing the ownership reference reproduces the company-owned effect and its covariance, verifying that the SE of β + δ includes the covariance term. All main, sensitivity and deletion models pass independent coefficient and covariance calculations, full-rank checks and residual orthogonality.

The raw input bytes are preserved. The project rebuilds preparation, both core tables and the extension from the original CSV into empty output directories. Generated files are compared by SHA-256. The version-controlled README provides dependency versions, one entry point and source-access instructions; all output tables are produced by code rather than manually edited. Report tables are read directly from those checked outputs.


---

8 Limitations and conclusion

The evidence applies to surveyed existing fast-food restaurants in NJ and eastern PA during 1992. It does not measure effects on potential new entrants, other industries, long-run employment or other minimum-wage policies. FTE is a headcount conversion using a half-weight for part-time workers, not directly observed total hours. Survey measurement error and item nonresponse may affect both outcomes and sample composition.

Only one pre-policy wave is available, so neither the overall comparison nor ownership-specific comparisons can establish parallel pre-trends empirically. Differential local shocks and differences between ownership categories may remain after chain adjustment. Ownership itself is not randomly assigned; the extension does not identify the causal effect of changing a restaurant’s ownership.

The policy varies at the state level and there are only two states. Treating hundreds of restaurants as hundreds of independent policy experiments would overstate the design’s information. Classical SE serve original-table comparison, while HC1 allows restaurant-level heteroskedasticity; neither accounts reliably for potentially correlated state-level shocks. Consequently, reported p values and intervals should not be treated as conclusive policy-level inference.

Replication differences are part of the evidence, not hidden defects to be corrected by changing observations. The available-case descriptive SE implementation is disclosed, small printed differences remain, and the public checking program’s ownership omission is reported separately from the table’s printed specification. The current author data exactly match the course data, but the exact historical source of all publication discrepancies is not established.

Conclusion

The replication recovers the paper’s central positive relative employment comparison and the first four adjusted regression coefficients and SEs at printed precision. Independent source verification and multiple calculation checks strengthen confidence that the implemented workflow is internally reproducible. The ownership extension estimates a modest negative difference for company-owned stores relative to franchises, with wide uncertainty and no precise ownership difference across the prespecified models. This supports cautious interpretation of both the original comparison and the extension rather than a universal minimum-wage conclusion.

Reproducibility package

The submitted project provides the input-access instructions, processed analysis data, complete Python code, original benchmarks, all numerical comparisons, extension results, checking records and a Git history of actual project stages. The reusable workflow generates the main tables, reconstructs this report and documents AI use. GitHub publication and any course-specific formatting or assigned-target requirements must be checked before submission.


---

9 AI use disclosure

Where AI was used The user selected the paper and supplied the assignment instructions, article and course data. ChatGPT Codex read these sources, explained the design, proposed the ownership extension, generated and executed Python code, retrieved the author archive, compared data, prepared the tables, drafted the report and checked its layout. The user requested that comprehension quizzes be omitted; data and computational validation were retained.

How AI outputs were checked The benchmark numbers were transcribed from the original rendered paper, separately from the estimator. Input structure, coding, closures and missingness were checked. Independent numerical solvers and covariance constructions were compared. Direct group arithmetic, ownership-reference reversal, source-file equality, influence checks and fresh-output reruns validated calculations. Tables and report values are generated from saved outputs. These checks were conducted with AI-assisted code; they are not falsely represented as an independent human audit or student verification.

Corrections and rejected shortcuts SHEET alone was found not to be unique, so no rows were removed merely because it repeats. A literal both-wages filter would remove six permanently closed stores; the closure exception was verified against the public author program. The earlier approximate description of the available-case DID as 2.76 was corrected to the actual 2.753606, displayed as 2.75. The fifth model’s printed specification and public checking-program specification were retained separately rather than hiding the omission of ownership. The row-3 SE was disclosed as an alternative implementation. No claim of pre-trend validation, identical ownership effects or universally positive minimum-wage effects was made.

Responsibility and provenance The user remains responsible for reviewing the submitted analysis and following course requirements. The report documents completed checks without claiming that the user personally executed them. Git commits were made by the AI assistant under its own identity, at actual stages, without backdating or fabricating a student work history. The source-selection and data-choice records remain available for review.

References and source access

Card, D., and Krueger, A. B. (1994). Minimum Wages and Employment: A Case Study of the Fast-Food Industry in New Jersey and Pennsylvania. American Economic Review, 84(4), 772–793. Original Table 3 and Table 4 are on printed page 780, PDF page 9 of the supplied article.

Card, D. Public survey archive and checking program. Author data page: https://davidcard.berkeley.edu/data_sets.html. Archive: https://davidcard.berkeley.edu/data_sets/njmin.zip. Description: https://davidcard.berkeley.edu/readme/njmin-readme.txt. Retrieved 9 October 2026. The description identifies book-related survey files and a checking program; the project does not equate this with the exact historical publication-production script.

ECO6067 course project instructions, supplied as four images; course README and DATA_DICTIONARY; and public.csv. These supplied materials establish the assignment requirements and source variable meanings. No third-party student replication output is used as the numerical benchmark.


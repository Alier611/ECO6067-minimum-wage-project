# Analysis rules fixed before formal replication

## Record identity

Keep all 410 observations. SHEET alone has a repeated value (407), associated
with distinct states and chains. STATE + SHEET is unique in the supplied data.
Use this composite key for this dataset; do not assume it generalizes to other
files. Do not remove rows merely because SHEET repeats.

## Employment and closure handling

FTE1 = EMPFT + NMGRS + 0.5 * EMPPT.
FTE2 components = EMPFT2 + NMGRS2 + 0.5 * EMPPT2.
All three components must be observed; no partial sum over missing components.
Base FTE2: permanent closures (STATUS2=3) are 0; refusals (0) and temporary
closures / renovations (2,4,5) are missing; answered stores use the components.
Sensitivity FTE2: statuses 2,3,4,5 are 0; refusals remain missing.
Change = FTE2 - FTE1. Do not impute other employment or wage missing values.

## Wage gap and wage groups

GAP = 0 in PA. In NJ with observed initial wage:
GAP = max(5.05 / WAGE_ST - 1, 0).
Missing initial NJ wage remains missing. GAP is a fraction, not a percent.
NJ Table 3 groups: exactly 4.25; greater than 4.25 and less than 5.00;
at least 5.00. The 5.00 grouping threshold is distinct from the 5.05 policy rate.

## Samples

Table 3 waves: use the available FTE observations separately in each wave.
Table 3 balanced: require FTE1 and base FTE2.
Table 3 temporary-zero sensitivity: require FTE1 and sensitivity FTE2.
Table 4 working sample: require balanced FTE, initial wage, and second wage
unless permanently closed. This retains the six permanently closed stores,
whose second-period wage is absent, giving 357 observations in this input.
The literal rule requiring both wages gives 351. Keep both counts in the audit.
This exception is an explicit implementation interpretation, validated against
the published sample and first-four-column coefficients; it is not asserted
to be read from the unavailable original author code.

Record all masks separately. Do not drop missing values across all 46 columns.
Future control-variable models must check missingness in their actual controls.

## Scope

Working replication target: Table 3 and Table 4; instructor-assigned target pending.
Independent extension: whether employment responses differ by company ownership.
Record this question before estimating extension effects. Plan a direct interaction
test, show four-cell sample coverage, control for chain composition, and report
confidence intervals. Do not infer group differences by comparing significance.
Core robustness checks already present in the paper do not alone constitute a
new extension. No causal mechanism is established solely by ownership comparisons.

No student-understanding checks. Retain data, computational and reproducibility
checks, and honest AI-use disclosure.

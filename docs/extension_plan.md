# Independent extension: ownership heterogeneity

Question fixed in the initial plan: does the employment response to the NJ
minimum-wage increase differ between company-owned and franchised restaurants?
Ownership is the first-wave CO_OWNED indicator, not a post-treatment variable.
Direction of the contrast: company-owned minus franchise.

Motivation: governance and local decision authority may affect a restaurant's
response to a cost change. This dataset does not observe those mechanisms, so
the project tests employment-response differences without claiming to identify
why any difference occurs. Ownership was a control in the original core table;
the extension tests an interaction, rather than relabeling that control as new.

Specifications and checks fixed before estimating this extension:

1. Descriptive four cells: state x ownership. Show sample sizes, baseline FTE,
   employment changes, wages and chain composition. All means label their sample.
2. Unadjusted model on the 384-store balanced FTE sample:
   change_FTE = a + b*NJ + c*CO_OWNED + d*(NJ*CO_OWNED) + error.
   b is franchise DID; b+d is company-owned DID; d is their direct difference.
   Verify coefficients against manually constructed four-cell mean contrasts.
3. Primary extension: same interaction plus three chain indicators, using the
   357-store Table 4 wage-valid sample. This keeps the primary extension connected
   to core replication and controls for chain composition. Test d=0 directly.
4. Report classical and HC1 standard errors separately. Primary uncertainty
   summary: HC1 with residual-df t approximation and 95% confidence intervals.
   These are restaurant-level model diagnostics, not robust state-policy inference.
5. Sensitivity: (a) chain-adjusted model on all 384 balanced stores, without a
   wage-validity restriction; (b) temporary closures set to zero, using the same
   wage rule with wage2 exempt for all closure statuses 2,3,4,5; (c) exclude each
   of the four chains in turn from the primary sample, retaining chain controls.
   Do not select the version that produces the smallest p value.
6. Show four-cell coverage in every sensitivity model; reject rank deficiency.
   Confirm covariance-based uncertainty for sums such as b+d, including their
   covariance. Show the direct interaction test, not separate significance claims.
7. Influence check: drop each primary-sample store individually and record the
   interaction estimate range and most influential change. This is a sensitivity
   diagnostic; it is not a formal robustness certificate.
8. Integrate all outputs into the single run entry point, rerun from the raw CSV,
   preserve raw bytes, and compare generated-file hashes.

Identification caveats: a causal heterogeneity claim requires credible comparisons
within ownership categories. Brand and geographic composition, ownership-specific
NJ shocks, measurement error and missing responses may confound the contrast.
Only one pre-policy wave prevents a pre-trend test. There are only two states;
HC1 and the ordinary t approximation do not solve correlated policy-level shocks.
No interpretation of an insignificant result as evidence of identical effects.

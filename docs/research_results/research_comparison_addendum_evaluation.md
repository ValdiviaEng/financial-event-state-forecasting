RESEARCH COMPARISON ADDENDUM: EVALUATION AND BENCHMARK FAMILY COMPARISON

Purpose

This document extends `docs/research_results/research_comparison.md` without modifying it.

Its purpose is to compare evaluation and benchmark families in more detail, because in this project evaluation methodology is not just reporting. It is part of the science.


SECTION 1. EVALUATION-SPECIFIC COMPARISON METHODOLOGY

Evaluation families are compared using the master framework plus evaluation-specific factors.

Evaluation-specific measured factors

1. Leakage-detection power
- how strongly the evaluation family protects against timing leakage or overlap contamination

2. Selection-bias resistance
- how well the family resists multiple-testing or backtest-overfitting illusion

3. Temporal realism
- how well the evaluation family matches the actual forecasting chronology

4. Statistical rigor
- how strong the family is for supporting defensible inference

5. Communication clarity
- how easy it is to explain the evaluation setup and its meaning to a thesis reader

6. Sample-efficiency burden
- how much usable data the method consumes or discards, with higher score meaning lower burden

7. Automation readiness
- how easily the repo can execute this family repeatedly and reliably

8. Lockbox compatibility
- how naturally the method coexists with a final untouched holdout policy


SECTION 2. EVALUATION FAMILIES INCLUDED

- single chronological holdout
- k-fold style random splitting
- walk-forward
- purged walk-forward
- purged plus embargoed walk-forward
- final lockbox holdout
- paired forecast-comparison tests
- bootstrap interval reporting
- probabilistic scoring and calibration suite
- backtest-overfitting diagnostics


SECTION 3. DETAILED EVALUATION FAMILY PROFILES

Single chronological holdout
- Leakage-detection power: 2
- Selection-bias resistance: 2
- Temporal realism: 4
- Statistical rigor: 2
- Communication clarity: 5
- Sample-efficiency burden: 5
- Automation readiness: 5
- Lockbox compatibility: 5
- Comments:
  - easy and intuitive
  - too weak alone for this thesis

Random k-fold style splitting
- Leakage-detection power: 1
- Selection-bias resistance: 2
- Temporal realism: 1
- Statistical rigor: 2
- Communication clarity: 4
- Sample-efficiency burden: 5
- Automation readiness: 5
- Lockbox compatibility: 2
- Comments:
  - generally inappropriate for this time-ordered finance setting

Walk-forward
- Leakage-detection power: 4
- Selection-bias resistance: 4
- Temporal realism: 5
- Statistical rigor: 4
- Communication clarity: 4
- Sample-efficiency burden: 4
- Automation readiness: 4
- Lockbox compatibility: 5
- Comments:
  - strong default time-aware family

Purged walk-forward
- Leakage-detection power: 5
- Selection-bias resistance: 4
- Temporal realism: 5
- Statistical rigor: 5
- Communication clarity: 4
- Sample-efficiency burden: 3
- Automation readiness: 4
- Lockbox compatibility: 5
- Comments:
  - excellent for overlapping multi-horizon labels

Purged plus embargoed walk-forward
- Leakage-detection power: 5
- Selection-bias resistance: 5
- Temporal realism: 5
- Statistical rigor: 5
- Communication clarity: 4
- Sample-efficiency burden: 3
- Automation readiness: 4
- Lockbox compatibility: 5
- Comments:
  - strongest current evaluation family for this repo and task

Final lockbox holdout
- Leakage-detection power: 4
- Selection-bias resistance: 5
- Temporal realism: 5
- Statistical rigor: 4
- Communication clarity: 5
- Sample-efficiency burden: 3
- Automation readiness: 4
- Lockbox compatibility: 5
- Comments:
  - excellent final reporting layer, insufficient alone for development

Paired forecast-comparison tests
- Leakage-detection power: 2
- Selection-bias resistance: 3
- Temporal realism: 3
- Statistical rigor: 5
- Communication clarity: 3
- Sample-efficiency burden: 4
- Automation readiness: 4
- Lockbox compatibility: 4
- Comments:
  - strong comparison supplement after saved predictions exist

Bootstrap interval reporting
- Leakage-detection power: 2
- Selection-bias resistance: 3
- Temporal realism: 3
- Statistical rigor: 4
- Communication clarity: 3
- Sample-efficiency burden: 4
- Automation readiness: 3
- Lockbox compatibility: 4
- Comments:
  - useful uncertainty-on-metrics layer, not a substitute for clean splits

Probabilistic scoring and calibration suite
- Leakage-detection power: 2
- Selection-bias resistance: 3
- Temporal realism: 3
- Statistical rigor: 5
- Communication clarity: 3
- Sample-efficiency burden: 3
- Automation readiness: 3
- Lockbox compatibility: 4
- Comments:
  - highly valuable if probabilistic outputs exist

Backtest-overfitting diagnostics
- Leakage-detection power: 3
- Selection-bias resistance: 5
- Temporal realism: 3
- Statistical rigor: 5
- Communication clarity: 3
- Sample-efficiency burden: 3
- Automation readiness: 2
- Lockbox compatibility: 4
- Comments:
  - not a replacement for walk-forward, but a strong meta-evaluation layer when the search space grows


SECTION 4. EVALUATION FAMILY COMPARATIVE TABLE

Evaluation family | LDP | SBR | TR | SR | CC | SEB | AR | LC | SVS | BIS | EFS | COS | Comments
----------------- | --- | --- | -- | -- | -- | --- | -- | -- | --- | --- | --- | --- | --------
Single chronological holdout | 2 | 2 | 4 | 2 | 5 | 5 | 5 | 5 | 2.8 | 2.9 | 4.8 | 4.8 | Easy and intuitive, too weak alone
Random k-fold | 1 | 2 | 1 | 2 | 4 | 5 | 5 | 2 | 1.8 | 1.8 | 4.8 | 3.0 | Generally inappropriate here
Walk-forward | 4 | 4 | 5 | 4 | 4 | 4 | 4 | 5 | 4.3 | 4.3 | 4.1 | 4.4 | Strong default time-aware family
Purged walk-forward | 5 | 4 | 5 | 5 | 4 | 3 | 4 | 5 | 4.6 | 4.8 | 3.8 | 4.2 | Strong for overlapping-label settings
Purged + embargoed walk-forward | 5 | 5 | 5 | 5 | 4 | 3 | 4 | 5 | 4.7 | 4.9 | 3.8 | 4.0 | Strongest current benchmark family
Final lockbox holdout | 4 | 5 | 5 | 4 | 5 | 3 | 4 | 5 | 4.0 | 4.5 | 3.7 | 4.3 | Great final layer, not enough alone
Paired forecast tests | 2 | 3 | 3 | 5 | 3 | 4 | 4 | 4 | 3.9 | 4.4 | 3.5 | 4.1 | Strong supplement after saved predictions exist
Bootstrap intervals | 2 | 3 | 3 | 4 | 3 | 4 | 3 | 4 | 3.5 | 3.8 | 3.2 | 3.8 | Useful metric-uncertainty layer
Probabilistic scoring/calibration suite | 2 | 3 | 3 | 5 | 3 | 3 | 3 | 4 | 4.0 | 4.1 | 3.1 | 3.4 | Valuable if probabilistic outputs exist
Backtest-overfitting diagnostics | 3 | 5 | 3 | 5 | 3 | 3 | 2 | 4 | 4.2 | 4.6 | 3.0 | 3.6 | Powerful meta-evaluation when search space expands

Legend
- LDP = Leakage-detection power
- SBR = Selection-bias resistance
- TR = Temporal realism
- SR = Statistical rigor
- CC = Communication clarity
- SEB = Sample-efficiency burden, higher means lower burden
- AR = Automation readiness
- LC = Lockbox compatibility


SECTION 5. SIMILARITY NOTES FOR EVALUATION

- Purged walk-forward and purged plus embargoed walk-forward are similar enough that the difference should be justified by actual overlap structure, not by fashion.
- Walk-forward and final lockbox are complementary, not substitutes.
- Paired forecast-comparison tests and bootstrap intervals are both secondary comparison layers, not split families.
- Probabilistic scoring and calibration are also secondary unless the model family itself becomes probabilistic.


SECTION 6. NON-DECISION SUMMARY FOR EVALUATION

This addendum does not choose the final evaluation protocol.

What it shows clearly is:
- random k-fold style evaluation is structurally weak for this project
- walk-forward is good
- purged and purged-plus-embargo walk-forward are best for the current multi-horizon setting
- final lockbox logic is highly valuable as a final reporting layer
- statistical comparison and backtest-overfitting diagnostics become more important as the search space widens
- probabilistic scoring is a later add-on, not a replacement for clean temporal benchmark design

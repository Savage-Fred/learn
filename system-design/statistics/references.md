# Authoritative References & Citations: Statistics for Data Analysis & Experimentation

This curriculum grounds all concepts, exercises, and rubrics in peer-reviewed academic literature, formal standards (RFCs, NIST, IETF), foundational textbooks, and verified tier-1 industry interview loops.

## Citable Bibliography

### Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing (2020)
- **Authors**: Ron Kohavi, Diane Tang, Ya Xu
- **Type**: `book`
- **Canonical URL / DOI**: [https://www.cambridge.org/core/books/trustworthy-online-controlled-experiments/D97B26382DEF7E123BEBF29C99026219](https://www.cambridge.org/core/books/trustworthy-online-controlled-experiments/D97B26382DEF7E123BEBF29C99026219)
- **Role Relevance**: Track-1-SWE, Track-4-Research-Eng
- **Core Invariants Extracted**:
  - Sample Ratio Mismatch (SRM) invalidates experiment conclusions.
  - CUPED eliminates pre-experiment variance using covariance adjustments.
  - SUTVA violations distort treatment effect estimates in marketplaces.
- **Interview Loop Calibration**:
  - *Target Company & Level*: Netflix (L5)
  - *Round*: Experimentation & Statistical Design
  - *Prompt Summary*: Design an experimentation platform for personalized video recommendation algorithms accounting for shared network interference and continuous metric monitoring.
  - *Expected Evaluation Signals*:
    - Identifies SUTVA violation and proposes switchback or cluster randomization
    - Calculates sample size using power analysis and applies CUPED

```bibtex
@book{kohavi2020trustworthy,
  title={Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing},
  author={Kohavi, Ron and Tang, Diane and Xu, Ya},
  year={2020},
  publisher={Cambridge University Press}
}
```

### Improving the Sensitivity of Online Controlled Experiments by Utilizing Pre-Experiment Data (2013)
- **Authors**: Alex Deng, Ya Xu, Ron Kohavi, Toby Walker
- **Type**: `paper`
- **Canonical URL / DOI**: [https://dl.acm.org/doi/10.1145/2433396.2433413](https://dl.acm.org/doi/10.1145/2433396.2433413)
- **Role Relevance**: Track-1-SWE, Track-4-Research-Eng
- **Core Invariants Extracted**:
  - CUPED variance reduction factor is strictly 1 - rho^2.
  - Estimator is provably unbiased under pre-experiment randomization.
- **Interview Loop Calibration**:
  - *Target Company & Level*: Meta (L5)
  - *Round*: Data Systems Architecture
  - *Prompt Summary*: Explain how variance reduction techniques allow high-frequency product experimentation without increasing user sample sizes.
  - *Expected Evaluation Signals*:
    - Derives CUPED optimal theta from ordinary least squares regression
    - Identifies conditions where pre-experiment data is unavailable

```bibtex
@inproceedings{deng2013improving,
  title={Improving the Sensitivity of Online Controlled Experiments by Utilizing Pre-Experiment Data},
  author={Deng, Alex and Xu, Ya and Kohavi, Ron and Walker, Toby},
  booktitle={WSDM},
  pages={445--454},
  year={2013}
}
```

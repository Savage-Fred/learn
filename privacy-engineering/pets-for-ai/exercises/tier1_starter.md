# Exercise TIER1_STARTER: Shadow-Model Membership Inference Attack on PyTorch Classifier

**Objective**: Build a membership inference attack against a trained PyTorch model using confidence score thresholding and a shadow model.

---

## Problem Statement

Implement `MembershipInferenceEvaluator`. Given a target classifier model, a dataset of known training members, and a dataset of known non-members: compute model loss and maximum softmax probabilities. Fit a logistic regression shadow classifier to predict membership. Return classification accuracy, ROC-AUC, and empirical privacy leakage advantage.

---

## Invariant Scaffolding & Guidance

- Training samples typically produce higher maximum softmax probability and lower cross-entropy loss than non-training samples.
- MIA advantage measures deviation from random 50% guessing: Adv = 2 * |Accuracy - 0.5|.

---

## Starter Code

```python
import numpy as np

class MembershipInferenceEvaluator:
    def evaluate_leakage(self, member_losses: np.ndarray, non_member_losses: np.ndarray) -> dict:
        # TODO: Compute threshold attack accuracy, ROC-AUC, and privacy advantage
        pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Overfitted model (100% train acc, 60% test acc) exhibits high MIA advantage (> 0.40).
- [ ] **Test Case**: Well-regularized or differentially private model exhibits low MIA advantage (~0.0).
- [ ] **Test Case**: Computes correct ROC-AUC curve matching Scikit-Learn metrics.

---

## Solution & Invariant Check

Calculates optimal threshold on cross-entropy loss minimizing balanced classification error; computes ROC curve.
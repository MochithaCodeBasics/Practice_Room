"""
Validator for Question 6: Boosting Classifier - Fraud Detection
"""
from sklearn.metrics import f1_score, roc_auc_score
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from _validator_utils import (
    check_result_structure,
    extract_metrics,
    check_metric_threshold,
    load_hidden_test_data,
    get_performance_level,
)

TARGET_COLUMN = 'is_fraud'
REQUIRED_METRICS = ['roc_auc', 'f1']
METRIC_THRESHOLDS = {
    'roc_auc': {'min': 0.7, 'valid_range': (0, 1)},
    'f1': {'min': 0.7, 'valid_range': (0, 1)},
}
PERFORMANCE_THRESHOLDS = {'excellent': 0.85, 'good': 0.75}
MAX_LEAKAGE_GAP = 0.17


def _normalize_util_msg(msg: str) -> str:
    return msg.replace("\u274c", "[FAIL] ").replace("\u26a0\ufe0f", "[WARN] ").replace("\u26a0", "[WARN] ")


def validate(user_module) -> str:
    folder_path = os.path.dirname(__file__)
    try:
        try:
            result = user_module.main()
            if not isinstance(result, tuple) or len(result) != 2:
                return '[FAIL] main() must return (model, result) tuple'
            model, your_result = result
        except Exception as e:
            return f'[FAIL] main() failed: {e}'

        error = check_result_structure(your_result, REQUIRED_METRICS)
        if error:
            return _normalize_util_msg(error)

        error, your_metrics = extract_metrics(your_result, REQUIRED_METRICS)
        if error:
            return _normalize_util_msg(error)

        for metric_name, thresholds in METRIC_THRESHOLDS.items():
            error = check_metric_threshold(
                metric_name,
                your_metrics[metric_name],
                min_val=thresholds.get('min'),
                max_val=thresholds.get('max'),
                valid_range=thresholds.get('valid_range'),
            )
            if error:
                return f"{_normalize_util_msg(error)} (Your result)"

        if not hasattr(model, 'predict') or not hasattr(model, 'predict_proba'):
            return '[FAIL] Returned model must implement both predict() and predict_proba() for hidden-test validation.'

        error, X_test, y_test = load_hidden_test_data(folder_path, TARGET_COLUMN)
        if error:
            return _normalize_util_msg(error)

        try:
            y_pred = model.predict(X_test)
        except Exception as e:
            return f'[FAIL] model.predict() failed on hidden test data: {e}'

        try:
            y_pred_proba = model.predict_proba(X_test)
            if getattr(y_pred_proba, 'ndim', 1) == 2 and y_pred_proba.shape[1] >= 2:
                y_pred_proba = y_pred_proba[:, 1]
        except Exception as e:
            return f'[FAIL] model.predict_proba() failed on hidden test data: {e}'

        test_metrics = {
            'f1': f1_score(y_test, y_pred, pos_label=1, zero_division=0),
            'roc_auc': roc_auc_score(y_test, y_pred_proba),
        }

        for metric_name, thresholds in METRIC_THRESHOLDS.items():
            error = check_metric_threshold(
                metric_name,
                test_metrics[metric_name],
                min_val=thresholds.get('min'),
                max_val=thresholds.get('max'),
                valid_range=thresholds.get('valid_range'),
            )
            if error:
                return f"{_normalize_util_msg(error)} (Test data)"

        auc_gap = your_metrics['roc_auc'] - test_metrics['roc_auc']
        if auc_gap > MAX_LEAKAGE_GAP:
            return f"[WARN] Possible overfitting/data leakage: Your ROC-AUC={your_metrics['roc_auc']:.4f} >> Test ROC-AUC={test_metrics['roc_auc']:.4f}"
        f1_gap = your_metrics['f1'] - test_metrics['f1']
        if f1_gap > MAX_LEAKAGE_GAP:
            return f"[WARN] Possible overfitting/data leakage: Your F1={your_metrics['f1']:.4f} >> Test F1={test_metrics['f1']:.4f}"

        if (
            abs(float(your_metrics['roc_auc']) - float(test_metrics['roc_auc'])) < 1e-12
            and abs(float(your_metrics['f1']) - float(test_metrics['f1'])) < 1e-12
        ):
            return '[FAIL] Suspicious output: public and hidden-test metrics are identical.'

        perf_level = get_performance_level(test_metrics['roc_auc'], PERFORMANCE_THRESHOLDS)
        return (
            '\u2705 Correct! Well done.\n'
            f"   Your Metrics: ROC-AUC={your_metrics['roc_auc']:.4f}, F1={your_metrics['f1']:.4f}\n"
            f"   Test Metrics: ROC-AUC={test_metrics['roc_auc']:.4f}, F1={test_metrics['f1']:.4f}\n"
            f"   {perf_level} fraud detection"
        )
    except Exception as e:
        return f'[WARN] Validation error: {e}'

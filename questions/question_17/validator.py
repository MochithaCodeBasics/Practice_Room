"""
Validator for Question 2: Multiple Linear Regression with Encoding
"""
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score
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

TARGET_COLUMN = "sales"
FEATURE_COLUMNS = ["region", "channel", "ad_spend", "discount"]
REQUIRED_METRICS = ["mse", "r2", "n_features"]
METRIC_THRESHOLDS = {
    "r2": {"min": 0.85, "valid_range": (0, 1)},
    "mse": {"max": 80000000, "valid_range": (0, np.inf)},
    "n_features": {"min": 7},
}
PERFORMANCE_THRESHOLDS = {"excellent": 0.92, "good": 0.85}
MAX_LEAKAGE_GAP = 0.15


def _normalize_util_msg(msg: str) -> str:
    return msg.replace("\u274c", "[FAIL] ").replace("\u26a0\ufe0f", "[WARN] ").replace("\u26a0", "[WARN] ")


def validate(user_module) -> str:
    folder_path = os.path.dirname(__file__)
    try:
        try:
            result = user_module.main()
            if not isinstance(result, tuple) or len(result) != 2:
                return "[FAIL] main() must return (model, result) tuple"
            model, your_result = result
        except Exception as e:
            return f"[FAIL] main() failed: {e}"

        error = check_result_structure(your_result, REQUIRED_METRICS)
        if error:
            return _normalize_util_msg(error)

        error, your_metrics = extract_metrics(your_result, REQUIRED_METRICS)
        if error:
            return _normalize_util_msg(error)

        for metric_name in ["r2", "mse"]:
            th = METRIC_THRESHOLDS[metric_name]
            error = check_metric_threshold(
                metric_name,
                your_metrics[metric_name],
                min_val=th.get("min"),
                max_val=th.get("max"),
                valid_range=th.get("valid_range"),
            )
            if error:
                return f"{_normalize_util_msg(error)} (Your result)"

        min_n_features = METRIC_THRESHOLDS["n_features"]["min"]
        if float(your_metrics["n_features"]) < min_n_features:
            return f"[FAIL] n_features should be >= {min_n_features} after encoding (got {your_metrics['n_features']})."

        error, X_test, y_test = load_hidden_test_data(folder_path, TARGET_COLUMN)
        if error:
            return _normalize_util_msg(error)
        X_test = X_test[FEATURE_COLUMNS]

        try:
            y_pred = model.predict(X_test)
        except Exception as e:
            return (
                f"[FAIL] model.predict() failed on hidden test data: {e}\n"
                "   [HINT] Use a Pipeline so one-hot encoding is applied automatically at predict time."
            )

        test_metrics = {
            "r2": r2_score(y_test, y_pred),
            "mse": mean_squared_error(y_test, y_pred),
        }

        for metric_name in ["r2", "mse"]:
            th = METRIC_THRESHOLDS[metric_name]
            error = check_metric_threshold(
                metric_name,
                test_metrics[metric_name],
                min_val=th.get("min"),
                max_val=th.get("max"),
                valid_range=th.get("valid_range"),
            )
            if error:
                return f"{_normalize_util_msg(error)} (Test data)\n   [HINT] Ensure preprocessing is fitted on training data and reused consistently."

        r2_gap = your_metrics["r2"] - test_metrics["r2"]
        if r2_gap > MAX_LEAKAGE_GAP:
            return f"[WARN] Possible overfitting/data leakage: Your R2={your_metrics['r2']:.4f} >> Test R2={test_metrics['r2']:.4f}"

        if (
            abs(float(your_metrics["r2"]) - float(test_metrics["r2"])) < 1e-12
            and abs(float(your_metrics["mse"]) - float(test_metrics["mse"])) < 1e-12
        ):
            return "[FAIL] Suspicious output: public and hidden-test metrics are identical."

        perf_level = get_performance_level(test_metrics["r2"], PERFORMANCE_THRESHOLDS)
        return (
            "\u2705 Correct! Well done.\n"
            f"   Your Metrics: R2={your_metrics['r2']:.4f}, MSE={your_metrics['mse']:,.2f}, Features={int(round(your_metrics['n_features']))}\n"
            f"   Test Metrics: R2={test_metrics['r2']:.4f}, MSE={test_metrics['mse']:,.2f}\n"
            f"   {perf_level} performance"
        )
    except Exception as e:
        return f"[WARN] Validation error: {e}"

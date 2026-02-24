"""
Validator for Question 7: CNN for Shape Classification
"""
import os
import sys
from unittest.mock import patch

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from _validator_utils import (  # noqa: E402
    extract_metrics,
    get_performance_level,
)
import question  # noqa: E402

# ================================
# Question-Specific Configuration
# ================================
REQUIRED_METRICS = ["accuracy", "macro_f1"]


def get_input_variables():
    return {"get_dataset_path": question.get_dataset_path}


METRIC_THRESHOLDS = {
    "accuracy": {"min": 0.85, "valid_range": (0, 1)},
    "macro_f1": {"min": 0.83, "valid_range": (0, 1)},
}
HIDDEN_THRESHOLDS = {
    "accuracy": 0.80,
    "macro_f1": 0.78,
}
PERFORMANCE_THRESHOLDS = {"excellent": 0.92, "good": 0.88}


def _validate_result_df(result: pd.DataFrame) -> str | None:
    if not isinstance(result, pd.DataFrame):
        return "[FAIL] main() must return a pandas DataFrame with performance metrics."

    if list(result.columns) != ["metric", "value"]:
        return (
            "[FAIL] Result DataFrame must have exactly these columns in order: "
            "['metric', 'value']."
        )

    if result["metric"].duplicated().any():
        return "[FAIL] Result DataFrame contains duplicate metric rows."

    metric_names = result["metric"].astype(str).str.lower()
    missing_metrics = [m for m in REQUIRED_METRICS if m not in set(metric_names)]
    if missing_metrics:
        return (
            f"[FAIL] Missing required metrics: {set(missing_metrics)}\n"
            "   [HINT] Calculate both overall accuracy and macro-averaged F1 score"
        )

    return None


def _check_thresholds(metrics_dict: dict, thresholds: dict, hidden: bool = False) -> str | None:
    for metric_name, cfg in thresholds.items():
        value = metrics_dict.get(metric_name)
        if value is None:
            return f"[FAIL] Metric `{metric_name}` missing after extraction."

        if hidden:
            if value < cfg:
                return (
                    f"âŒ Hidden Test Case Failed: {metric_name} {value:.4f} is too low "
                    f"on hidden data (expected > {cfg:.2f})."
                )
            continue

        valid_range = cfg["valid_range"]
        if not (valid_range[0] <= value <= valid_range[1]):
            return (
                f"[FAIL] {metric_name}={value:.4f} is out of valid range {valid_range}\n"
                "   [HINT] Check your metric calculation"
            )

        min_val = cfg.get("min")
        if min_val is not None and value < min_val:
            if metric_name == "accuracy":
                return (
                    "[FAIL] Model accuracy is below required threshold\n"
                    f"   Current: {value:.4f}\n"
                    "   [HINT] Hints:\n"
                    "      - Add more convolutional layers for better feature extraction\n"
                    "      - Increase training epochs (try 15-20)\n"
                    "      - Try different learning rates (e.g., 0.001)"
                )
            if metric_name == "macro_f1":
                return (
                    "[FAIL] Macro F1 score is below required threshold\n"
                    f"   Current: {value:.4f}\n"
                    "   ðŸ’¡ Hints:\n"
                    "      - Ensure balanced class performance\n"
                    "      - Check if all classes are predicted correctly\n"
                    "      - Increase model capacity or training time"
                )
    return None


def _enforce_cnn_components(user_code: str | None) -> str | None:
    # If source is unavailable, skip this check (platform-dependent).
    if not user_code:
        return None

    lower = user_code.lower()
    missing = []
    if "conv2d" not in lower:
        missing.append("Conv2d layers")
    if all(x not in lower for x in ["pool", "maxpool", "avgpool"]):
        missing.append("Pooling layers")
    if "linear" not in lower:
        missing.append("Linear (fully connected) layers")

    if missing:
        return (
            "[FAIL] CNN architecture requirements not satisfied.\n"
            "   Missing required components:\n"
            + "\n".join(f"      - {m}" for m in missing)
            + "\n   [HINT] Ensure your model includes Conv2d, Pooling, and Linear layers."
        )
    return None


def validate(user_module, user_code=None, user_df=None) -> str:
    """
    Validate user's solution for Question 7.
    """
    try:
        # 1) Run main() or use injected DataFrame
        if user_df is not None:
            result = user_df
        else:
            try:
                result = user_module.main()
            except Exception as e:
                return f"[FAIL] main() failed: {str(e)}"

        # 2) Strict DataFrame schema + required metrics
        error = _validate_result_df(result)
        if error:
            return error

        # 3) Numeric metric extraction + public thresholds
        error, metrics_dict = extract_metrics(result, REQUIRED_METRICS)
        if error:
            return error
        error = _check_thresholds(metrics_dict, METRIC_THRESHOLDS, hidden=False)
        if error:
            return error

        # 4) Enforce CNN architecture components when source is available
        error = _enforce_cnn_components(user_code)
        if error:
            return error

        # 5) Hidden test on hidden_data.pt by patching dataset path resolver
        try:
            hidden_dataset_path = os.path.join(os.path.dirname(__file__), "hidden_data.pt")
            if os.path.exists(hidden_dataset_path):
                with patch.object(user_module, "get_dataset_path", create=True) as mocked_get_path:
                    mocked_get_path.return_value = hidden_dataset_path
                    hidden_result = user_module.main()

                error = _validate_result_df(hidden_result)
                if error:
                    return f"[FAIL] Hidden Test Case Failed: {error}"

                error, hidden_metrics = extract_metrics(hidden_result, REQUIRED_METRICS)
                if error:
                    return f"[FAIL] Hidden Test Case Failed: {error}"

                error = _check_thresholds(hidden_metrics, HIDDEN_THRESHOLDS, hidden=True)
                if error:
                    return error

                if (
                    abs(float(hidden_metrics['accuracy']) - float(metrics_dict['accuracy'])) < 1e-12
                    and abs(float(hidden_metrics['macro_f1']) - float(metrics_dict['macro_f1'])) < 1e-12
                ):
                    return "[FAIL] Hidden Test Case Failed: Output appears hardcoded (public and hidden metrics are identical)."
        except Exception as e:
            return f"[FAIL] Hidden Test Case Execution Failed: {str(e)}"

        # 6) Success
        perf_level = get_performance_level(metrics_dict["accuracy"], PERFORMANCE_THRESHOLDS)
        success_msg = (
            "[PASS] Correct! Your CNN model works great!\n"
            "   [INFO] Performance Metrics:\n"
            f"      - Accuracy: {metrics_dict['accuracy']:.4f}\n"
            f"      - Macro F1: {metrics_dict['macro_f1']:.4f}\n"
            f"   [INFO] {perf_level} performance\n"
        )
        if user_code:
            success_msg += "   [INFO] Complete CNN architecture detected!"
        else:
            success_msg += "   [WARN] Architecture source check skipped (user_code not provided)."
        return success_msg

    except Exception as e:
        return f"[WARN] Validation error: {str(e)}"

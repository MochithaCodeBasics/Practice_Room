import builtins
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from _validator_utils import (
    check_metric_threshold,
    check_result_structure,
    extract_metrics,
    get_performance_level,
)

REQUIRED_METRICS = ["accuracy", "final_loss"]
METRIC_THRESHOLDS = {
    "accuracy": {"min": 0.80, "valid_range": (0, 1)},
    "final_loss": {"max": 0.8, "valid_range": (0, np.inf)},
}
PERFORMANCE_THRESHOLDS = {"excellent": 0.80, "good": 0.70}


def validate(user_module, user_code=None, user_df=None) -> str:
    try:
        if not hasattr(user_module, "main") or not callable(getattr(user_module, "main", None)):
            return "[FAIL] Function `main()` is not defined."

        # 1. Get result DataFrame (from user_df or by calling main())
        if user_df is not None:
            result = user_df
        else:
            try:
                result = user_module.main()
                if not isinstance(result, pd.DataFrame):
                    return "[FAIL] main() must return a pandas DataFrame. Return only the result DataFrame."
            except Exception as e:
                return f"[FAIL] main() failed: {e}"

        # 2. Validate implementation (basic library checks)
        if user_code is not None:
            bad_frameworks = ["import torch", "from torch", "import tensorflow", "from tensorflow"]
            if any(x in user_code for x in bad_frameworks):
                return "[FAIL] Your implementation should use NumPy only, not PyTorch or other deep learning libraries."
            if "numpy" not in user_code and "np." not in user_code:
                return "[FAIL] Your implementation should use NumPy for array operations."

        # 3. Validate result structure
        error = check_result_structure(result, REQUIRED_METRICS)
        if error:
            return error

        # 4. Extract metrics
        error, metrics = extract_metrics(result, REQUIRED_METRICS)
        if error:
            return error

        # 5. Check metric thresholds
        for metric_name, thresholds in METRIC_THRESHOLDS.items():
            error = check_metric_threshold(
                metric_name,
                metrics[metric_name],
                min_val=thresholds.get("min"),
                max_val=thresholds.get("max"),
                valid_range=thresholds.get("valid_range"),
            )
            if error:
                if metric_name == "accuracy" and metrics[metric_name] < 0.55:
                    return f"{error}\n[HINT] Accuracy barely better than random (0.5). Check your backpropagation implementation."
                if metric_name == "final_loss" and metrics[metric_name] > 0.8:
                    return f"{error}\n[HINT] Loss is too high. Did your model train[INFO] Check learning rate and number of epochs."
                return error

        # 6. Validate on hidden test data (anti-cheat)
        try:
            data_file = os.path.join(os.path.dirname(__file__), "hidden_test_case.csv")
            if os.path.exists(data_file):
                hidden_df = pd.read_csv(data_file)

                original_module_data = getattr(user_module, "data", None)
                had_module_data = hasattr(user_module, "data")
                original_builtin_data = getattr(builtins, "data", None)
                had_builtin_data = hasattr(builtins, "data")

                try:
                    user_module.data = hidden_df
                    builtins.data = hidden_df
                    hidden_result = user_module.main()
                finally:
                    if had_module_data:
                        user_module.data = original_module_data
                    elif hasattr(user_module, "data"):
                        delattr(user_module, "data")

                    if had_builtin_data:
                        builtins.data = original_builtin_data
                    elif hasattr(builtins, "data"):
                        delattr(builtins, "data")

                if not isinstance(hidden_result, pd.DataFrame):
                    return "[FAIL] Hidden Test Case Failed: `main()` must return a pandas DataFrame on hidden data."

                error = check_result_structure(hidden_result, REQUIRED_METRICS)
                if error:
                    return f"[FAIL] Hidden Test Case Failed: {error}"

                error, hidden_metrics = extract_metrics(hidden_result, REQUIRED_METRICS)
                if error:
                    return f"[FAIL] Hidden Test Case Failed: {error}"

                if hidden_metrics["accuracy"] < 0.70:
                    return f"[FAIL] Hidden Test Case Failed: Accuracy {hidden_metrics['accuracy']:.4f} is too low on hidden data."
                if hidden_metrics["final_loss"] > 1.0:
                    return f"[FAIL] Hidden Test Case Failed: final_loss {hidden_metrics['final_loss']:.4f} is too high on hidden data."

                # Anti-cheat heuristic: exact same public/hidden metric table is a strong hardcoding signal.
                if (
                    abs(float(hidden_metrics["accuracy"]) - float(metrics["accuracy"])) < 1e-12
                    and abs(float(hidden_metrics["final_loss"]) - float(metrics["final_loss"])) < 1e-12
                ):
                    return "[FAIL] Hidden Test Case Failed: Output appears hardcoded (public and hidden metrics are identical)."
        except Exception as e:
            return f"[FAIL] Hidden Test Case Execution Failed: {e}"

        # 7. Success
        perf_level = get_performance_level(metrics["accuracy"], PERFORMANCE_THRESHOLDS)
        return (
            f"[PASS] Correct! Your NumPy neural network works!\n"
            f"   [INFO] Accuracy: {metrics['accuracy']:.4f}\n"
            f"   [INFO] Final Loss: {metrics['final_loss']:.4f}\n"
            f"   [INFO] {perf_level} performance\n"
            f"   [INFO] Well done implementing forward and backward propagation from scratch!"
        )

    except Exception as e:
        return f"[WARN] Validation error: {e}"

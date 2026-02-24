import os
import math
import random
import pandas as pd


REQUIRED_COLUMNS = ["metric", "value"]
REQUIRED_METRICS = ["n_customers", "n_churned", "n_retained", "churn_rate_pct"]


def _approx_equal(a, b, tol=1e-2):
    return math.isclose(float(a), float(b), abs_tol=tol, rel_tol=0.0)


def _expected_metrics(df: pd.DataFrame) -> dict:
    n_customers = int(len(df))
    n_churned = int((df["churn"] == 1).sum())
    n_retained = int((df["churn"] == 0).sum())
    churn_rate_pct = round((n_churned / n_customers) * 100, 2) if n_customers else 0.0
    return {
        "n_customers": n_customers,
        "n_churned": n_churned,
        "n_retained": n_retained,
        "churn_rate_pct": churn_rate_pct,
    }


def _validate_result(result, expected, label):
    if not isinstance(result, pd.DataFrame):
        return f"❌ {label}: Expected pandas DataFrame, got {type(result).__name__}."

    if list(result.columns) != REQUIRED_COLUMNS:
        return f"❌ {label}: Expected columns {REQUIRED_COLUMNS}, got {list(result.columns)}."

    if len(result) != len(REQUIRED_METRICS):
        return f"❌ {label}: Expected {len(REQUIRED_METRICS)} rows, got {len(result)}."

    metrics_seen = result["metric"].tolist()
    if set(metrics_seen) != set(REQUIRED_METRICS):
        return f"❌ {label}: Metrics mismatch. Expected {REQUIRED_METRICS}, got {metrics_seen}."

    if len(metrics_seen) != len(set(metrics_seen)):
        return f"❌ {label}: Duplicate metric rows found."

    value_map = dict(zip(result["metric"], result["value"]))
    for key in REQUIRED_METRICS:
        if key not in value_map:
            return f"❌ {label}: Missing metric `{key}`."
        actual = value_map[key]
        expected_val = expected[key]
        if key in {"n_customers", "n_churned", "n_retained"}:
            try:
                if int(actual) != int(expected_val):
                    return f"❌ {label}: `{key}` expected {expected_val}, got {actual}."
            except Exception:
                return f"❌ {label}: `{key}` must be an integer-like value."
        else:
            try:
                if not _approx_equal(actual, expected_val):
                    return f"❌ {label}: `{key}` expected {expected_val}, got {actual}."
            except Exception:
                return f"❌ {label}: `{key}` must be numeric."

    # Consistency checks
    if int(value_map["n_churned"]) + int(value_map["n_retained"]) != int(value_map["n_customers"]):
        return f"❌ {label}: `n_churned + n_retained` must equal `n_customers`."

    rate = float(value_map["churn_rate_pct"])
    if rate < 0 or rate > 100:
        return f"❌ {label}: `churn_rate_pct` must be between 0 and 100."

    return None


def validate(user_module):
    try:
        if not hasattr(user_module, "analyze_churn"):
            return "❌ Function `analyze_churn(df)` is not defined."

        func = user_module.analyze_churn
        if not callable(func):
            return "❌ `analyze_churn` is not callable."

        base = os.path.dirname(__file__)
        public_df = pd.read_csv(os.path.join(base, "churn.csv"))
        hidden_df = pd.read_csv(os.path.join(base, "hidden_test_data.csv"))

        # Public test
        public_out = func(public_df.copy())
        err = _validate_result(public_out, _expected_metrics(public_df), "Public test")
        if err:
            return err

        # Hidden file-based test
        hidden_out = func(hidden_df.copy())
        err = _validate_result(hidden_out, _expected_metrics(hidden_df), "Hidden test 1")
        if err:
            return err

        # Hidden randomized adversarial test (seeded)
        random.seed(2026)
        rows = []
        for i in range(15):
            rows.append({
                "customer_id": 1000 + i,
                "churn": random.randint(0, 1),
            })
        rand_df = pd.DataFrame(rows)
        rand_out = func(rand_df.copy())
        err = _validate_result(rand_out, _expected_metrics(rand_df), "Hidden test 2")
        if err:
            return err

        return "✅ Correct! All test cases passed successfully."
    except Exception as e:
        return f"⚠️ Validation error: {e}"

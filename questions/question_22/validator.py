"""
Validator for Question 7: K-Means Clustering
"""
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from _validator_utils import (
    check_result_structure,
    extract_metrics,
    check_metric_threshold,
    get_performance_level,
)

FEATURE_COLUMNS = ['total_spend', 'txn_count', 'recency_days']
REQUIRED_METRICS = ['silhouette_score']
METRIC_THRESHOLDS = {'silhouette_score': {'min': 0.5, 'valid_range': (-1, 1)}}
PERFORMANCE_THRESHOLDS = {'excellent': 0.6, 'good': 0.5}


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

        error = check_metric_threshold(
            'silhouette_score',
            your_metrics['silhouette_score'],
            min_val=METRIC_THRESHOLDS['silhouette_score']['min'],
            valid_range=METRIC_THRESHOLDS['silhouette_score']['valid_range'],
        )
        if error:
            return _normalize_util_msg(error)

        train_path = os.path.join(folder_path, 'data.csv')
        test_path = os.path.join(folder_path, 'hidden_test_data.csv')
        if not os.path.exists(train_path) or not os.path.exists(test_path):
            return '[WARN] Data files missing for validation.'
        try:
            df_train = pd.read_csv(train_path)
            df_test = pd.read_csv(test_path)
        except Exception as e:
            return f'[WARN] Test data validation failed: {e}'

        X_train = df_train[FEATURE_COLUMNS]
        X_test = df_test[FEATURE_COLUMNS]

        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.metrics import silhouette_score

        if isinstance(model, Pipeline):
            try:
                labels_pred = model.predict(X_test)
            except Exception as e:
                return f'[FAIL] Pipeline prediction failed on hidden test data: {e}'
            try:
                X_test_transformed = X_test.copy()
                for _, transform in model.steps[:-1]:
                    X_test_transformed = transform.transform(X_test_transformed)
            except Exception:
                scaler = StandardScaler().fit(X_train)
                X_test_transformed = scaler.transform(X_test)
        else:
            scaler = StandardScaler().fit(X_train)
            X_test_transformed = scaler.transform(X_test)
            try:
                labels_pred = model.predict(X_test_transformed)
            except Exception as e:
                return (
                    f'[FAIL] Model prediction failed on hidden test data: {e}\n'
                    '   [HINT] If you did not use a Pipeline, return a model that expects scaled inputs.'
                )

        if len(set(labels_pred)) < 2:
            return f'[FAIL] Model predicted only {len(set(labels_pred))} cluster(s). K-Means requires at least 2.'

        val_score = silhouette_score(X_test_transformed, labels_pred)
        if val_score < 0.4:
            return f'[FAIL] Test Silhouette Score too low: {val_score:.4f} (Expected > 0.4)'

        if abs(float(your_metrics['silhouette_score']) - float(val_score)) < 1e-12:
            return '[FAIL] Suspicious output: public and hidden-test silhouette scores are identical.'

        perf_level = get_performance_level(your_metrics['silhouette_score'], PERFORMANCE_THRESHOLDS)
        return (
            '\u2705 Correct! Well done.\n'
            f"   Your Silhouette Score: {your_metrics['silhouette_score']:.4f}\n"
            f"   Test Silhouette Score: {val_score:.4f}\n"
            f"   {perf_level} clustering quality"
        )
    except Exception as e:
        return f'[WARN] Validation error: {e}'

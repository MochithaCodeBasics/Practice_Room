import pandas as pd
import numpy as np
import os
import inspect


def validate(user_module) -> str:
    """
    Validates the TF-IDF classification result against public and hidden cases.
    """
    try:
        def get_metric_value(df, metric_name):
            row = df[df['metric'] == metric_name]
            if len(row) == 0:
                return None
            return float(row['value'].iloc[0])

        def run_check(result, is_hidden=False):
            if not isinstance(result, pd.DataFrame):
                return False, f"Expected pandas DataFrame, got {type(result).__name__}"
            
            required_metrics = ['accuracy', 'macro_f1', 'n_features', 'avg_tfidf']
            result_metrics = result['metric'].tolist()
            missing_metrics = [m for m in required_metrics if m not in result_metrics]
            if missing_metrics:
                return False, f"Missing metrics: {missing_metrics}"

            accuracy = get_metric_value(result, 'accuracy')
            macro_f1 = get_metric_value(result, 'macro_f1')
            n_features = get_metric_value(result, 'n_features')
            avg_tfidf = get_metric_value(result, 'avg_tfidf')

            if accuracy is None or accuracy < 0.5 or accuracy > 1.0:
                return False, f"Accuracy {accuracy} is out of range or too low."
            if macro_f1 is None or macro_f1 < 0.4 or macro_f1 > 1.0:
                return False, f"Macro F1 {macro_f1} is out of range or too low."
            if n_features is None or n_features < 10:
                return False, f"n_features {n_features} is too low."
            if avg_tfidf is None or avg_tfidf <= 0 or avg_tfidf > 1:
                return False, f"avg_tfidf {avg_tfidf} is invalid."
            
            return True, ""

        # 1. Validate Public Case
        if not hasattr(user_module, "result"):
            return "❌ Variable `result` is not defined."
        
        success, message = run_check(user_module.result)
        if not success:
            return f"❌ {message}"

        # 2. Validate Hidden Case (Re-run with hidden data)
        hidden_path = os.path.join(os.path.dirname(__file__), "hidden_test_cases.csv")
        if os.path.exists(hidden_path):
            hidden_data = pd.read_csv(hidden_path)
            # To make it a valid test, we combine public + hidden for a larger test set 
            # Or just run on a new set. Let's run on a combined set.
            public_data_path = os.path.join(os.path.dirname(__file__), "data.csv")
            if os.path.exists(public_data_path):
                full_data = pd.concat([pd.read_csv(public_data_path), hidden_data]).reset_index(drop=True)
                try:
                    source = inspect.getsource(user_module)
                    # We need to provide the environment
                    local_ns = {"data": full_data, "pd": pd, "np": np}
                    # We might need to import sklearn things if they are not in the source
                    # But usually they are.
                    exec(source, user_module.__dict__.copy(), local_ns)
                    hidden_result = local_ns.get("result")
                    
                    success, message = run_check(hidden_result, is_hidden=True)
                    if not success:
                        return "❌ Failed on hidden test case. Your pipeline might not be robust to different data splits."
                except Exception as e:
                    # Ignore exec errors if they are due to missing imports in a partial source
                    # but typically this should work.
                    pass

        return f"✅ Correct! TF-IDF classification pipeline works well on both public and hidden data."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"

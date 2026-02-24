import pandas as pd
import os
import inspect
import builtins


def validate(user_module) -> str:
    """
    Validates the sentiment analysis result against public and hidden cases.
    """
    try:
        def run_check(data, result, is_hidden=False):
            if not isinstance(result, pd.DataFrame):
                return False, f"Expected pandas DataFrame, got {type(result).__name__}"
            
            required_cols = ['review', 'label', 'score']
            missing_cols = [col for col in required_cols if col not in result.columns]
            if missing_cols:
                return False, f"Missing columns: {missing_cols}"
            
            if len(result) != len(data):
                return False, f"Expected {len(data)} rows, got {len(result)}."

            valid_labels = ['POSITIVE', 'NEGATIVE']
            for idx, row in result.iterrows():
                label = row['label']
                score = row['score']
                if label not in valid_labels:
                    return False, f"Invalid label '{label}' at row {idx}. Use POSITIVE or NEGATIVE."
                if not isinstance(score, (int, float)) or score < 0 or score > 1:
                    return False, f"Invalid score {score} at row {idx}."
                if data.iloc[idx]['review'] != row['review']:
                    return False, f"Review text mismatch at row {idx}."
            
            return True, ""

        # 1. Validate Public Case
        if not hasattr(user_module, "result"):
            return "❌ Variable `result` is not defined. Ensure your code creates a 'result' DataFrame."
        
        # Fallback for data if not explicitly defined in module (it's usually in builtins)
        data = getattr(user_module, "data", None)
        if data is None:
            data = getattr(builtins, "data", None)
            
        if data is None:
            return "❌ Variable `data` is not defined and could not be found in builtins."
        
        success, message = run_check(data, user_module.result)
        if not success:
            return f"❌ {message}"

        # 2. Validate Hidden Cases
        hidden_path = os.path.join(os.path.dirname(__file__), "hidden_test_cases.csv")
        if os.path.exists(hidden_path):
            hidden_data = pd.read_csv(hidden_path)
            try:
                # OPTIMIZATION: Reuse user's classifier instead of re-running everything
                if not hasattr(user_module, "classifier"):
                    return "❌ `classifier` pipeline not found. Please define it as in the sample code."
                
                classifier = user_module.classifier
                reviews = hidden_data["review"].tolist()
                
                # Run prediction on hidden data
                predictions = classifier(reviews, truncation=True)
                
                hidden_result = pd.DataFrame({
                    "review": reviews,
                    "label": [p["label"] for p in predictions],
                    "score": [p["score"] for p in predictions]
                })
                
                success, message = run_check(hidden_data, hidden_result, is_hidden=True)
                if not success:
                    return "❌ Failed on hidden test cases. Make sure your pipeline is initialized correctly."
            except Exception as e:
                return f"⚠️ Error validating hidden cases: {str(e)}"

        return "✅ Correct! All test cases passed successfully."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"

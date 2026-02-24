import pandas as pd
import os
import inspect


def validate(user_module) -> str:
    """
    Validates the tokenization result against public and hidden cases.
    """
    try:
        def run_check(data, result, is_hidden=False):
            if not isinstance(result, pd.DataFrame):
                return False, f"Expected pandas DataFrame, got {type(result).__name__}"
            
            required_cols = ['input_ids', 'attention_mask']
            missing_cols = [col for col in required_cols if col not in result.columns]
            if missing_cols:
                return False, f"Missing columns: {missing_cols}"
            
            if len(result) != len(data):
                return False, f"Expected {len(data)} rows, got {len(result)}."

            for idx, row in result.iterrows():
                input_ids = row['input_ids']
                attention_mask = row['attention_mask']
                
                if not isinstance(input_ids, list) or not isinstance(attention_mask, list):
                    return False, f"Row {idx}: input_ids and attention_mask must be lists."
                
                if len(input_ids) != len(attention_mask):
                    return False, f"Row {idx}: Length mismatch between input_ids and attention_mask."
                
                if any(v not in [0, 1] for v in attention_mask):
                    return False, f"Row {idx}: attention_mask contains invalid values (must be 0 or 1)."
                
                if len(input_ids) < 2:
                    return False, f"Row {idx}: input_ids should have at least 2 tokens (CLS/SEP)."
            
            return True, ""

        # 1. Validate Public Case
        if not hasattr(user_module, "result"):
            return "❌ Variable `result` is not defined."
        
        # Note: 'data' is injected by the platform into the module namespace or builtins
        # so we check if result exists and proceed to run_check which takes the data object.
        import builtins
        data_obj = getattr(user_module, "data", getattr(builtins, "data", None))
        if data_obj is None:
            return "❌ Input `data` not found in execution context."
            
        success, message = run_check(data_obj, user_module.result)
        if not success:
            return f"❌ {message}"
        # 2. Validate Hidden Cases
        hidden_path = os.path.join(os.path.dirname(__file__), "hidden_test_cases.csv")
        if os.path.exists(hidden_path):
            hidden_data = pd.read_csv(hidden_path)
            try:
                # OPTIMIZATION: Reuse user's tokenizer instead of re-running everything
                if not hasattr(user_module, "tokenizer"):
                    return "❌ `tokenizer` not found. Please define it as in the sample code."
                
                tokenizer = user_module.tokenizer
                texts = hidden_data["text"].tolist()
                
                # Run tokenization on hidden data
                encoded = tokenizer(texts, padding=True, truncation=True)
                
                hidden_result = pd.DataFrame({
                    "input_ids": encoded["input_ids"],
                    "attention_mask": encoded["attention_mask"]
                })
                
                success, message = run_check(hidden_data, hidden_result, is_hidden=True)
                if not success:
                    return "❌ Failed on hidden test cases. Make sure your tokenizer is correctly initialized."
            except Exception as e:
                return f"⚠️ Error validating hidden cases: {str(e)}"

        return "✅ Correct! All test cases passed successfully."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"

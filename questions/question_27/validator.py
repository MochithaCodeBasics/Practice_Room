import pandas as pd
import re
import os
import inspect
import question
import io
import contextlib


def get_input_variables() -> dict:
    """
    Returns input variables to be injected into the user's namespace.
    """
    return {"data": question.get_input_data()}


def validate(user_module) -> str:
    """
    Validates the regex extraction result.
    
    Checks:
    1. Result is a pandas DataFrame
    2. Required columns exist
    3. Extracted values match expected patterns (Public and Hidden)
    """
    try:
        # Define extraction functions for validation (ground truth)
        def extract_order_id(msg):
            match = re.search(r'ORD-\d+', str(msg))
            return match.group() if match else ""
        
        def extract_email(msg):
            match = re.search(r'[\w.-]+@[\w.-]+\.\w+', str(msg))
            return match.group() if match else ""
        
        def extract_phone(msg):
            match = re.search(r'(\+?\d[\d\s-]{8,}\d)', str(msg))
            return match.group().strip() if match else ""
        
        def extract_amount(msg):
            match = re.search(r'₹[\d,]+(?:\.\d{1,2})?', str(msg))
            return match.group() if match else ""

        def run_check(data, result, is_hidden=False):
            if not isinstance(result, pd.DataFrame):
                return False, f"Expected pandas DataFrame, got {type(result).__name__}"
            
            required_cols = ['order_id', 'email', 'phone', 'amount']
            missing_cols = [col for col in required_cols if col not in result.columns]
            if missing_cols:
                return False, f"Missing columns: {missing_cols}"
            
            if len(result) != len(data):
                return False, f"Expected {len(data)} rows, got {len(result)}."

            errors = []
            for idx, row in data.iterrows():
                msg = row['message']
                result_row = result.iloc[idx]
                
                # order_id
                expected = extract_order_id(msg)
                actual = str(result_row['order_id']).strip()
                if actual != expected:
                    errors.append(f"Row {idx}: order_id expected '{expected}', got '{actual}'")
                
                # email
                expected = extract_email(msg)
                actual = str(result_row['email']).strip()
                if actual != expected:
                    errors.append(f"Row {idx}: email expected '{expected}', got '{actual}'")
                
                # phone
                expected = extract_phone(msg)
                actual = str(result_row['phone']).strip()
                exp_norm = re.sub(r'\s+', '', expected)
                act_norm = re.sub(r'\s+', '', actual)
                if act_norm != exp_norm:
                    errors.append(f"Row {idx}: phone expected '{expected}', got '{actual}'")
                
                # amount
                expected = extract_amount(msg)
                actual = str(result_row['amount']).strip()
                if actual != expected:
                    errors.append(f"Row {idx}: amount expected '{expected}', got '{actual}'")

            if errors:
                if is_hidden:
                    return False, "Failed on hidden test case data. Make sure your regex covers various formats."
                return False, "; ".join(errors[:2])
            return True, ""

        # 1. Enforce function contract
        if not hasattr(user_module, "extract_order_details"):
            return "[FAIL] Function `extract_order_details(message)` is not defined."
        if not callable(user_module.extract_order_details):
            return "[FAIL] `extract_order_details` is not callable."

        # 2. Validate Public Case
        if not hasattr(user_module, "result"):
            return "❌ Variable `result` is not defined."
        
        public_data = question.get_input_data()
        success, message = run_check(public_data, user_module.result)
        if not success:
            return f"❌ {message}"

        # 3. Validate Hidden Cases
        hidden_path = os.path.join(os.path.dirname(__file__), "hidden_test_cases.csv")
        if os.path.exists(hidden_path):
            hidden_data = pd.read_csv(hidden_path)
            # Re-run student logic for hidden data
            try:
                source = inspect.getsource(user_module)
                local_ns = {"data": hidden_data, "pd": pd, "re": re}
                
                # To prevent user's hardcoded 'data' from overwriting the test case:
                globals_dict = user_module.__dict__.copy()
                globals_dict["data"] = hidden_data
                
                # Suppress student's print statements for hidden cases
                f = io.StringIO()
                with contextlib.redirect_stdout(f):
                    exec(source, globals_dict, local_ns)
                
                hidden_result = local_ns.get("result")
                
                success, message = run_check(hidden_data, hidden_result, is_hidden=True)
                if not success:
                    return f"❌ {message}"
            except Exception as e:
                return f"⚠️ Error validating hidden cases: {str(e)}"

        return "✅ Correct! All test cases passed successfully."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"

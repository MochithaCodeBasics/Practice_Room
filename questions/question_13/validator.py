import pandas as pd
import spacy
import os
import inspect
import question
import io
import contextlib


def get_input_variables() -> dict:
    """
    Returns input variables to be injected into the user's namespace.
    """
    return {"text": question.get_input_text()}


def run_test(text, user_module, nlp) -> tuple[bool, str]:
    """
    Runs a single test case.
    Returns (success, message).
    """
    try:
        # Load spaCy model and get expected entities
        doc = nlp(text)
        expected_entities = []
        for ent in doc.ents:
            expected_entities.append({
                'entity_text': ent.text,
                'entity_label': ent.label_,
                'start_char': ent.start_char,
                'end_char': ent.end_char
            })
        
        expected_df = pd.DataFrame(expected_entities)
        if not expected_df.empty:
            expected_df = expected_df.sort_values('start_char').reset_index(drop=True)

        # Get result from user_module if provided, else re-run
        if hasattr(user_module, "result") and text == question.get_input_text():
            result = user_module.result
        else:
            # Re-run student logic for hidden case
            # We need to simulate the environment
            try:
                source = inspect.getsource(user_module)
                # Remove imports and other things to avoid re-loading nlp[INFO] 
                # Actually, let's keep it simple for now and re-exec.
                # To speed up, we can inject the nlp object if they use a global one
                local_ns = {"text": text, "pd": pd, "spacy": spacy}
                if hasattr(user_module, "nlp"):
                     local_ns["nlp"] = user_module.nlp

                # To prevent user's hardcoded 'text' from overwriting the test case:
                globals_dict = user_module.__dict__.copy()
                globals_dict["text"] = text
                
                # Suppress student's print statements for hidden cases
                f = io.StringIO()
                with contextlib.redirect_stdout(f):
                    exec(source, globals_dict, local_ns)
                
                result = local_ns.get("result")
            except Exception as e:
                return False, f"Error re-running code: {str(e)}"

        # Check if result is a DataFrame
        if not isinstance(result, pd.DataFrame):
            return False, f"Expected pandas DataFrame, got {type(result).__name__}"

        # Check required columns
        required_cols = ['entity_text', 'entity_label', 'start_char', 'end_char']
        missing_cols = [col for col in required_cols if col not in result.columns]
        if missing_cols:
            return False, f"Missing columns: {missing_cols}"

        # Check if result is sorted by start_char
        if not result.empty:
            if not result['start_char'].is_monotonic_increasing:
                return False, "Result is not sorted by start_char in ascending order."

        # Compare results
        result_reset = result.reset_index(drop=True)
        
        if len(result_reset) != len(expected_df):
            return False, f"Expected {len(expected_df)} entities, got {len(result_reset)}."

        # Check each entity
        for idx in range(len(expected_df)):
            exp_row = expected_df.iloc[idx]
            res_row = result_reset.iloc[idx]
            
            if res_row['entity_text'] != exp_row['entity_text']:
                return False, f"Entity {idx+1}: Expected text '{exp_row['entity_text']}', got '{res_row['entity_text']}'"
            
            if res_row['entity_label'] != exp_row['entity_label']:
                return False, f"Entity {idx+1}: Expected label '{exp_row['entity_label']}', got '{res_row['entity_label']}'"
            
            if res_row['start_char'] != exp_row['start_char']:
                return False, f"Entity {idx+1}: Expected start_char {exp_row['start_char']}, got {res_row['start_char']}"
            
            if res_row['end_char'] != exp_row['end_char']:
                return False, f"Entity {idx+1}: Expected end_char {exp_row['end_char']}, got {res_row['end_char']}"

        return True, ""

    except Exception as e:
        return False, f"Validation error: {str(e)}"


def validate(user_module) -> str:
    """
    Validates the NER extraction result against public and hidden test cases.
    """
    try:
        # Load spaCy model for validation
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            return "⚠️ spaCy model 'en_core_web_sm' is not installed. Run: python -m spacy download en_core_web_sm"

        # 1. Validate Public Case
        public_text = question.get_input_text()
        success, message = run_test(public_text, user_module, nlp)
        if not success:
            return f"❌ {message}"

        # 2. Validate Hidden Cases
        hidden_path = os.path.join(os.path.dirname(__file__), "hidden_test_cases.csv")
        if os.path.exists(hidden_path):
            hidden_df = pd.read_csv(hidden_path)
            for idx, row in hidden_df.iterrows():
                hidden_text = row['text']
                success, message = run_test(hidden_text, user_module, nlp)
                if not success:
                    # Generic message for hidden failure to avoid leakage
                    return f"❌ Failed on hidden test case {idx+1}. Make sure your code generalizes well."

        return "✅ Correct! All test cases passed successfully."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"

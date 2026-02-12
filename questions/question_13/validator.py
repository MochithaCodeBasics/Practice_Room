import pandas as pd
import spacy
import question


def get_input_variables() -> dict:
    """
    Returns input variables to be injected into the user's namespace.
    """
    return {"text": question.get_input_text()}


def validate(user_module) -> str:
    """
    Validates the NER extraction result.
    
    Checks:
    1. Result is a pandas DataFrame
    2. Required columns exist
    3. Character offsets match entity spans
    4. Results sorted by start_char
    5. Entity labels match spaCy's predictions
    """
    try:
        # Check if result exists
        if not hasattr(user_module, "result"):
            return "❌ Variable `result` is not defined."

        result = user_module.result

        # Check if result is a DataFrame
        if not isinstance(result, pd.DataFrame):
            return f"❌ Expected pandas DataFrame, got {type(result).__name__}"

        # Check required columns
        required_cols = ['entity_text', 'entity_label', 'start_char', 'end_char']
        missing_cols = [col for col in required_cols if col not in result.columns]
        if missing_cols:
            return f"❌ Missing columns: {missing_cols}"

        # Get the text from the question module (injected into user's namespace)
        text = question.get_input_text()

        # Load spaCy model and get expected entities
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            return "⚠️ spaCy model 'en_core_web_sm' is not installed. Run: python -m spacy download en_core_web_sm"

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

        # Check if result is sorted by start_char
        if not result.empty:
            if not result['start_char'].is_monotonic_increasing:
                return "❌ Result is not sorted by start_char in ascending order."

        # Compare results
        result_reset = result.reset_index(drop=True)
        
        if len(result_reset) != len(expected_df):
            return f"❌ Expected {len(expected_df)} entities, got {len(result_reset)}."

        # Check each entity
        for idx in range(len(expected_df)):
            exp_row = expected_df.iloc[idx]
            res_row = result_reset.iloc[idx]
            
            if res_row['entity_text'] != exp_row['entity_text']:
                return f"❌ Entity {idx+1}: Expected text '{exp_row['entity_text']}', got '{res_row['entity_text']}'"
            
            if res_row['entity_label'] != exp_row['entity_label']:
                return f"❌ Entity {idx+1}: Expected label '{exp_row['entity_label']}', got '{res_row['entity_label']}'"
            
            if res_row['start_char'] != exp_row['start_char']:
                return f"❌ Entity {idx+1}: Expected start_char {exp_row['start_char']}, got {res_row['start_char']}"
            
            if res_row['end_char'] != exp_row['end_char']:
                return f"❌ Entity {idx+1}: Expected end_char {exp_row['end_char']}, got {res_row['end_char']}"

        return "✅ Correct! All named entities extracted correctly."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"

import os
import logging

# Suppress HuggingFace warnings and progress bars
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN_LOGIN"] = "1"
# Only show errors
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)

# Lazy load to prevent timeout and unnecessary imports at top level
# from sentence_transformers import SentenceTransformer, util

_model = None
CATEGORY_THRESHOLD = 0.4
SAMPLE_COUNT = 2


def _sim(text_a, text_b):
    global _model
    from sentence_transformers import SentenceTransformer, util
    if _model is None:
        print("SYSTEM: Loading judgement model (all-MiniLM-L6-v2)...", flush=True)
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    embs = _model.encode([text_a, text_b], convert_to_tensor=True)
    return util.cos_sim(embs[0], embs[1]).item()


def _run_case(user_module, tc):
    required_keys = {"name", "amount", "category"}

    try:
        result = user_module.extract_financial_info(tc["input"])
    except Exception as e:
        return f"Crashed on input \"{tc['input']}\" → {type(e).__name__}: {e}"

    if not isinstance(result, dict):
        return f"Output must be a dictionary, got {type(result).__name__}."

    if not required_keys <= set(result.keys()):
        missing = required_keys - set(result.keys())
        return f"Missing keys: {missing}."

    if not isinstance(result["name"], str):
        return "'name' must be a string."

    if not isinstance(result["amount"], (int, float)):
        return "'amount' must be a number."

    if not isinstance(result["category"], str) or len(result["category"].strip()) == 0:
        return "'category' must be a non-empty string."

    if tc["expected_name"] not in result["name"].strip().lower():
        return f"Expected name to contain '{tc['expected_name']}', got '{result['name']}'."

    try:
        parsed_amount = int(float(result["amount"]))
    except (ValueError, TypeError):
        return f"Could not parse amount '{result['amount']}' as a number."
    if parsed_amount != tc["expected_amount"]:
        return f"Expected amount {tc['expected_amount']}, got {result['amount']}."

    cat_score = _sim(result["category"], tc["expected_category"])
    if cat_score < CATEGORY_THRESHOLD:
        return (
            f"Category '{result['category']}' is not semantically close to "
            f"'{tc['expected_category']}' (similarity: {cat_score:.2f}, threshold: {CATEGORY_THRESHOLD})."
        )

    return None


def validate(user_module):
    if not hasattr(user_module, "extract_financial_info"):
        return "❌ Function extract_financial_info is not defined."

    test_cases = [
        {
            "input": "John paid 4500 for office supplies",
            "expected_name": "john",
            "expected_amount": 4500,
            "expected_category": "office supplies",
        },
        {
            "input": "Sara spent 200 on groceries",
            "expected_name": "sara",
            "expected_amount": 200,
            "expected_category": "groceries",
        },
        {
        "input": "Mike paid 99 for a taxi ride",
        "expected_name": "mike",
        "expected_amount": 99,
        "expected_category": "taxi ride",
        },
        {
        "input": "Alice spent 1500 on electronics",
        "expected_name": "alice",
        "expected_amount": 1500,
        "expected_category": "electronics",
        },
        {
        "input": "Bob paid 350 for restaurant dinner",
        "expected_name": "bob",
        "expected_amount": 350,
        "expected_category": "restaurant dinner",
        },
    ]

    total = len(test_cases)
    passed = 0
    feedback = []

    for i, tc in enumerate(test_cases, 1):
        error = _run_case(user_module, tc)
        is_sample = i <= SAMPLE_COUNT

        if error is None:
            passed += 1
            label = f"Sample Test {i}" if is_sample else f"Hidden Test {i}"
            feedback.append(f"✅ {label}: Passed")
        elif is_sample:
            feedback.append(f"❌ Sample Test {i}: {error}")
        else:
            feedback.append(f"❌ Hidden Test {i}: Failed")

    summary = "\n".join(feedback)

    if passed == total:
        return f"✅ {passed}/{total} test cases passed! Structured information extracted correctly.\n\n{summary}"
    else:
        return f"❌ {passed}/{total} test cases passed.\n\n{summary}"

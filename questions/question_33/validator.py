import re
import os
import logging

# Suppress HuggingFace warnings and progress bars
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN_LOGIN"] = "1"
# Only show errors
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)

# Lazy load to prevent timeout and unnecessary imports at top level
# Lazy load to prevent timeout
# from sentence_transformers import SentenceTransformer, util

_model = None
TOPIC_THRESHOLD = 0.5
SAMPLE_COUNT = 2


def _sim(text_a, text_b):
    global _model
    from sentence_transformers import SentenceTransformer, util
    if _model is None:
        print("SYSTEM: Loading judgement model (all-MiniLM-L6-v2)...", flush=True)
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    embs = _model.encode([text_a, text_b], convert_to_tensor=True)
    return util.cos_sim(embs[0], embs[1]).item()


def _run_case(user_module, question):
    try:
        output = user_module.refine_question(question)
    except Exception as e:
        return f"Crashed on input \"{question}\" → {type(e).__name__}: {e}"

    if not isinstance(output, str):
        return f"Output must be a string, got {type(output).__name__}."

    output_stripped = output.strip()

    if len(output_stripped) < 10:
        return f"Refined question is too short ({len(output_stripped)} chars). Expected a meaningful question."

    if "?" not in output_stripped:
        return f"Refined output must be a question (missing '?'). Got: \"{output_stripped}\""

    score = _sim(output_stripped, question)
    if score < TOPIC_THRESHOLD:
        return (
            f"Refined question lost the original topic "
            f"(similarity: {score:.2f}, threshold: {TOPIC_THRESHOLD}). "
            f"Input: \"{question}\", Got: \"{output_stripped}\""
        )

    return None


def validate(user_module):
    if not hasattr(user_module, "refine_question"):
        return "❌ Function refine_question is not defined."

    test_cases = [
        "Explain RAG",
        "how does ai work",
        "tell me bout transformers",
        "whats prompt eng",
        "diff btwn llm and slm",
    ]

    total = len(test_cases)
    passed = 0
    feedback = []

    for i, question in enumerate(test_cases, 1):
        error = _run_case(user_module, question)
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
        return f"✅ {passed}/{total} test cases passed! Questions refined correctly.\n\n{summary}"
    else:
        return f"❌ {passed}/{total} test cases passed.\n\n{summary}"

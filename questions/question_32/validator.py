import re
# Lazy load to prevent timeout on import
# from sentence_transformers import SentenceTransformer, util

_model = None
RELEVANCE_THRESHOLD = 0.45
SAMPLE_COUNT = 2


def _sim(text_a, text_b):
    global _model
    from sentence_transformers import SentenceTransformer, util
    if _model is None:
        print("SYSTEM: Loading judgement model (all-MiniLM-L6-v2)...", flush=True)
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    embs = _model.encode([text_a, text_b], convert_to_tensor=True)
    return util.cos_sim(embs[0], embs[1]).item()


def _run_case(user_module, text):
    try:
        output = user_module.generate_summary(text)
    except Exception as e:
        return f"Crashed → {type(e).__name__}: {e}"

    if not isinstance(output, str):
        return f"Output must be a string, got {type(output).__name__}."

    output_stripped = output.strip()

    if len(output_stripped) == 0:
        return "Output cannot be empty."

    sentences = re.split(r'(?<=[.!?])\s+', output_stripped)
    if len(sentences) > 1:
        return f"Output must be a single sentence, got {len(sentences)} sentences."

    score = _sim(output_stripped, text)
    if score < RELEVANCE_THRESHOLD:
        return (
            f"Summary is not semantically relevant to the input "
            f"(similarity: {score:.2f}, threshold: {RELEVANCE_THRESHOLD})."
        )

    return None


def validate(user_module):
    if not hasattr(user_module, "generate_summary"):
        return "❌ Function generate_summary is not defined."

    test_cases = [
        "Revenue increased significantly. Expenses also rose. Profits declined.",
        "The product launched last month. Users loved it. Downloads hit a million.",
        "Sales dropped in Q3. Marketing budget was cut. New hires were frozen.",
        "The server crashed at midnight. Engineers fixed it by morning. No data was lost.",
        "Customer complaints increased. Response time was slow. Satisfaction scores fell.",
    ]

    total = len(test_cases)
    passed = 0
    feedback = []

    for i, text in enumerate(test_cases, 1):
        error = _run_case(user_module, text)
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
        return f"✅ {passed}/{total} test cases passed! Single-sentence summaries generated correctly.\n\n{summary}"
    else:
        return f"❌ {passed}/{total} test cases passed.\n\n{summary}"

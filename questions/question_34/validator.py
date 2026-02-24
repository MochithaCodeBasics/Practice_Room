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
MATCH_THRESHOLD = 0.65
SAMPLE_COUNT = 2


def _best_match(candidate, options):
    global _model
    from sentence_transformers import SentenceTransformer, util
    if _model is None:
        print("SYSTEM: Loading judgement model (all-MiniLM-L6-v2)...", flush=True)
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    cand_emb = _model.encode(candidate, convert_to_tensor=True)
    opt_embs = _model.encode(options, convert_to_tensor=True)
    scores = util.cos_sim(cand_emb, opt_embs)[0]
    best_idx = scores.argmax().item()
    return options[best_idx], scores[best_idx].item()


def _run_case(user_module, tc):
    try:
        result = user_module.semantic_search(tc["documents"], tc["query"])
    except Exception as e:
        return f"Crashed on query \"{tc['query']}\" → {type(e).__name__}: {e}"

    if not isinstance(result, str):
        return f"Output must be a string, got {type(result).__name__}."

    matched_doc, score = _best_match(result.strip(), tc["documents"])

    if score < MATCH_THRESHOLD:
        return (
            f"Output does not match any provided document "
            f"(best similarity: {score:.2f}, threshold: {MATCH_THRESHOLD}). "
            f"Got: \"{result}\""
        )

    if matched_doc != tc["expected"]:
        return (
            f"Wrong document selected for query \"{tc['query']}\". "
            f"Expected: \"{tc['expected']}\", got closest match: \"{matched_doc}\"."
        )

    return None


def validate(user_module):
    if not hasattr(user_module, "semantic_search"):
        return "❌ Function semantic_search is not defined."

    test_cases = [
        {
            "documents": [
                "AI is powerful",
                "Dogs are animals",
                "GenAI uses large language models",
            ],
            "query": "language models",
            "expected": "GenAI uses large language models",
        },
        {
            "documents": [
                "Python is a programming language",
                "The sun is a star",
                "Machine learning needs data",
            ],
            "query": "coding in Python",
            "expected": "Python is a programming language",
        },
        {
            "documents": [
                "Water boils at 100 degrees Celsius",
                "Neural networks learn patterns from data",
                "Rain falls from clouds",
            ],
            "query": "deep learning architectures",
            "expected": "Neural networks learn patterns from data",
        },
        {
            "documents": [
                "Photosynthesis converts sunlight to energy",
                "SQL is used to query databases",
                "The moon orbits the Earth",
            ],
            "query": "database management",
            "expected": "SQL is used to query databases",
        },
        {
            "documents": [
                "Electric cars reduce emissions",
                "Transformers revolutionized NLP",
                "The ocean covers 71 percent of Earth",
            ],
            "query": "natural language processing breakthroughs",
            "expected": "Transformers revolutionized NLP",
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
        return f"✅ {passed}/{total} test cases passed! Relevant documents selected correctly.\n\n{summary}"
    else:
        return f"❌ {passed}/{total} test cases passed.\n\n{summary}"

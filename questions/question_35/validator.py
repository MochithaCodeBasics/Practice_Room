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
GROUNDING_THRESHOLD = 0.4
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


def _run_case(user_module, tc):
    try:
        output = user_module.rag_answer(tc["documents"], tc["question"])
    except Exception as e:
        return f"Crashed on question \"{tc['question']}\" → {type(e).__name__}: {e}"

    if not isinstance(output, str):
        return f"Output must be a string, got {type(output).__name__}."

    output_stripped = output.strip()

    if len(output_stripped) < 15:
        return (
            f"Answer is too short ({len(output_stripped)} chars) "
            f"to be meaningful for \"{tc['question']}\"."
        )

    q_score = _sim(output_stripped, tc["question"])
    if q_score < RELEVANCE_THRESHOLD:
        return (
            f"Answer is not relevant to the question \"{tc['question']}\" "
            f"(similarity: {q_score:.2f}, threshold: {RELEVANCE_THRESHOLD})."
        )

    g_score = _sim(output_stripped, tc["relevant_doc"])
    if g_score < GROUNDING_THRESHOLD:
        return (
            f"Answer does not appear grounded in the provided documents "
            f"(similarity: {g_score:.2f}, threshold: {GROUNDING_THRESHOLD})."
        )

    return None


def validate(user_module):
    if not hasattr(user_module, "rag_answer"):
        return "❌ Function rag_answer is not defined."

    test_cases = [
        {
            "documents": [
                "RAG improves LLM accuracy by grounding responses",
                "Prompt engineering controls model output",
            ],
            "question": "Why is RAG useful?",
            "relevant_doc": "RAG improves LLM accuracy by grounding responses",
        },
        {
            "documents": [
                "Transformers use self-attention mechanisms",
                "CNNs are used for image classification",
            ],
            "question": "How do transformers process text?",
            "relevant_doc": "Transformers use self-attention mechanisms",
        },
        {
            "documents": [
                "Fine-tuning adapts a pretrained model to a specific task",
                "Data augmentation increases training data variety",
            ],
            "question": "What is fine-tuning in machine learning?",
            "relevant_doc": "Fine-tuning adapts a pretrained model to a specific task",
        },
        {
            "documents": [
                "Vector databases store embeddings for similarity search",
                "Relational databases use SQL for structured queries",
            ],
            "question": "How do vector databases work?",
            "relevant_doc": "Vector databases store embeddings for similarity search",
        },
        {
            "documents": [
                "Tokenization splits text into smaller units called tokens",
                "Stemming reduces words to their root form",
            ],
            "question": "What is tokenization in NLP?",
            "relevant_doc": "Tokenization splits text into smaller units called tokens",
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
        return f"✅ {passed}/{total} test cases passed! RAG-style answers generated correctly.\n\n{summary}"
    else:
        return f"❌ {passed}/{total} test cases passed.\n\n{summary}"

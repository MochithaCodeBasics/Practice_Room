def validate(user_module) -> str:
    try:
        import random
        import re

        if not hasattr(user_module, "routing_agent"):
            return "❌ Function routing_agent is not defined."

        func = user_module.routing_agent
        if not callable(func):
            return "❌ routing_agent is not callable."

        def _contains_number(text: str, expected: int) -> bool:
            return str(expected) in re.findall(r"-?\d+", text)

        random.seed(2026)
        # --- Public Test Case ---
        try:
            result_math = func("What is 5 + 7?")
            result_general = func("Tell me a fun fact")

            if not isinstance(result_math, str) or not isinstance(result_general, str):
                return "❌ Output must be a string."

            if not _contains_number(result_math, 12):
                return "❌ Math query did not return the correct answer."
            if result_math.strip().lower() == result_general.strip().lower():
                return "❌ Routing agent did not route queries to different handlers."
        except Exception as e:
            return f"❌ Public Test Failed: {str(e)}"

        # --- Hidden Test Cases ---
        hidden_tests = [
            ("What is 25 * 4?", "math", 100),
            ("What is the capital of Spain?", "fact", "Madrid"),
        ]
        for _ in range(3):
            a = random.randint(2, 20)
            b = random.randint(2, 20)
            hidden_tests.append((f"What is {a} + {b}?", "math", a + b))

        math_outputs = []
        fact_outputs = []
        for i, (query, kind, expected) in enumerate(hidden_tests, 1):
            try:
                res = func(query)
                if not isinstance(res, str):
                     return f"❌ Hidden Test Case {i} Failed: Output must be a string."

                if kind == "math":
                    passed = _contains_number(res, int(expected))
                    math_outputs.append(res.strip().lower())
                else:
                    passed = str(expected) in res
                    fact_outputs.append(res.strip().lower())
                if not passed:
                     return f"❌ Hidden Test Case {i} Failed."
            except Exception as e:
                return f"❌ Hidden Test Case {i} Failed with error: {str(e)}"

        if math_outputs and fact_outputs and any(m == f for m in math_outputs for f in fact_outputs):
            return "❌ Suspicious output: identical response used for routed math and fact queries."

        return "✅ Correct! All test cases passed successfully."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"

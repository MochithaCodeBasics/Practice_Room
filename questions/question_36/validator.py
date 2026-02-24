def validate(user_module) -> str:
    try:
        # Lazy import
        import random
        import re

        if not hasattr(user_module, "reasoning_agent"):
            return "❌ Function reasoning_agent is not defined."

        func = user_module.reasoning_agent
        if not callable(func):
            return "❌ reasoning_agent is not callable."

        def _contains_expected_number(text: str, expected: int) -> bool:
            # Require exact numeric token match (avoids passing on partial overlaps).
            nums = re.findall(r"-?\d+", text)
            return str(expected) in nums

        random.seed(2026)
        # --- Public Test Case ---
        try:
            result = func("What is 10 * 2?")
            if not isinstance(result, str):
                return "❌ Output must be a string."

            if not _contains_expected_number(result, 20):
                return "❌ Final answer is incorrect. Expected result to contain '20'."
        except Exception as e:
             return f"❌ Public Test Failed: {str(e)}"

        # --- Hidden Test Cases ---
        hidden_tests = [
            ("What is 50 + 50?", 100),
            ("If I have 5 apples and eat 2, how many do I have?", 3),
            ("What is 9 - 4?", 5),
        ]
        for _ in range(3):
            a = random.randint(2, 50)
            b = random.randint(2, 50)
            op = random.choice(["+", "-", "*"])
            expr = f"{a} {op} {b}"
            expected = eval(expr)
            hidden_tests.append((f"What is {expr}?", int(expected)))

        seen_outputs = set()
        for i, (query, expected_subs) in enumerate(hidden_tests, 1):
            try:
                res = func(query)
                if not isinstance(res, str):
                     return f"❌ Hidden Test Case {i} Failed: Output must be a string."
                res_norm = res.strip()
                if not res_norm:
                    return f"❌ Hidden Test Case {i} Failed: Empty output."
                seen_outputs.add(res_norm.lower())

                if not _contains_expected_number(res_norm, expected_subs):
                     return f"❌ Hidden Test Case {i} Failed."
            except Exception as e:
                return f"❌ Hidden Test Case {i} Failed with error: {str(e)}"

        if len(seen_outputs) < 2:
            return "❌ Suspicious output: identical response across different reasoning prompts."

        return "✅ Correct! All test cases passed successfully."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"

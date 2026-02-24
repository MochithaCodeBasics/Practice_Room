def validate(user_module) -> str:
    try:
        # Lazy import
        import random
        import re

        if not hasattr(user_module, "simple_tool_agent"):
            return "❌ Function simple_tool_agent is not defined."

        func = user_module.simple_tool_agent
        if not callable(func):
            return "❌ simple_tool_agent is not callable."

        def _contains_number(text: str, expected: int) -> bool:
            return str(expected) in re.findall(r"-?\d+", text)

        random.seed(2026)
        # --- Public Test Case ---
        try:
            result = func("What is 3 + 5?")
            if not isinstance(result, str):
                return "❌ Output must be a string."
             
            if not _contains_number(result, 8):
                return "❌ Agent did not correctly use the tool to compute 3 + 5."
        except Exception as e:
            return f"❌ Public Test Failed: {str(e)}"

        # --- Hidden Test Cases ---
        # Format: (query, expected_numeric_answer)
        hidden_tests = [
            ("What is 15 * 4?", 60),
            ("What is 100 - 45?", 55),
            ("What is 8 + 2 * 3?", 14),
        ]
        for _ in range(3):
            a = random.randint(2, 200)
            b = random.randint(2, 200)
            op = random.choice(["+", "-", "*"])
            expr = f"{a} {op} {b}"
            hidden_tests.append((f"What is {expr}?", int(eval(expr))))

        seen_outputs = set()
        for i, (query, expected_value) in enumerate(hidden_tests, 1):
            try:
                res = func(query)
                if not isinstance(res, str):
                    return f"❌ Hidden Test Case {i} Failed: Output must be a string."
                res_norm = res.strip()
                if not res_norm:
                    return f"❌ Hidden Test Case {i} Failed: Empty output."
                seen_outputs.add(res_norm.lower())
                 
                # Check for answer correctness
                if not _contains_number(res_norm, expected_value):
                    return f"❌ Hidden Test Case {i} Failed."
            except Exception as e:
                return f"❌ Hidden Test Case {i} Failed with error: {str(e)}"

        if len(seen_outputs) < 2:
            return "❌ Suspicious output: identical response across different tool-use prompts."

        return "✅ Correct! All test cases passed successfully."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"

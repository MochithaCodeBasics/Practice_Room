def validate(user_module) -> str:
    try:
        import random
        import re

        if not hasattr(user_module, "task_planning_agent"):
            return "❌ Function task_planning_agent is not defined."

        func = user_module.task_planning_agent
        if not callable(func):
            return "❌ task_planning_agent is not callable."

        random.seed(2026)

        def _extract_steps(text: str):
            return [line.strip() for line in text.split("\n") if line.strip()]

        def _looks_enumerated(lines):
            enum_count = 0
            for line in lines:
                if re.match(r"^(\d+[.)]|[-*•])\s+", line):
                    enum_count += 1
            return enum_count >= max(1, len(lines) // 2)

        # --- Public Test Case ---
        try:
            result = func("Plan a 3-step morning routine")
            if not isinstance(result, str):
                return "❌ Output must be a string."

            steps = _extract_steps(result)
            if len(steps) < 3:
                return "❌ Expected at least 3 executed steps in the output."
            if not _looks_enumerated(steps):
                return "❌ Steps should be clearly enumerated (numbered or bulleted)."
        except Exception as e:
            return f"❌ Public Test Failed: {str(e)}"

        # --- Hidden Test Cases ---
        # Format: (query, min_steps)
        hidden_tests = [
            ("Plan a 2-step workout", 2, ["workout", "exercise", "stretch"]),
            ("Plan a 5-step travel itinerary", 5, ["travel", "trip", "itinerary"]),
        ]
        # Seeded additional hidden prompts to reduce hardcoding.
        hidden_tests.extend([
            (f"Plan a {n}-step study routine", n, ["study", "read", "review"])
            for n in (3, 4)
        ])

        seen_outputs = set()
        for i, (query, min_steps, keywords) in enumerate(hidden_tests, 1):
            try:
                res = func(query)
                if not isinstance(res, str):
                     return f"❌ Hidden Test Case {i} Failed: Output must be a string."
                res_norm = res.strip()
                if not res_norm:
                    return f"❌ Hidden Test Case {i} Failed: Empty output."
                seen_outputs.add(res_norm.lower())

                steps = _extract_steps(res_norm)
                if len(steps) < min_steps:
                    return f"❌ Hidden Test Case {i} Failed."
                if not _looks_enumerated(steps):
                    return f"❌ Hidden Test Case {i} Failed: steps should be enumerated."
                if keywords and not any(k in res_norm.lower() for k in keywords):
                    return f"❌ Hidden Test Case {i} Failed: plan seems unrelated to the requested task."
                if len({s.lower() for s in steps}) < min_steps:
                    return f"❌ Hidden Test Case {i} Failed: repeated steps detected."
            except Exception as e:
                return f"❌ Hidden Test Case {i} Failed with error: {str(e)}"

        if len(seen_outputs) < 2:
            return "❌ Suspicious output: identical plan returned for different requests."

        return "✅ Correct! All test cases passed successfully."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"

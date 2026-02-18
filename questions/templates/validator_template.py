"""
Reference template for Practice Room validator authoring.
Upload this file as `validator.py`.
"""

def validate(user_code_module):
    try:
        # Call learner function and compare output.
        # Example:
        # result = user_code_module.solve()
        # if result == expected:
        #     return "[PASS] Correct!"
        # return "[FAIL] Expected X, got Y"
        return "[PASS] Replace this with real validation logic."
    except Exception as exc:
        return f"[FAIL] Runtime error: {exc}"

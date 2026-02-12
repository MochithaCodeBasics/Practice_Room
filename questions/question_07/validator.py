import os
import math
import tempfile

def _approx_equal(a: float, b: float, tol: float = 1e-2) -> bool:
    return math.isclose(float(a), float(b), abs_tol=tol, rel_tol=0.0)

def validate(user_module) -> str:
    try:
        # 1) Function existence
        if not hasattr(user_module, "generate_sales_summary"):
            return "❌ Function `generate_sales_summary(file_path)` is not defined."

        func = getattr(user_module, "generate_sales_summary")

        if not callable(func):
            return "❌ `generate_sales_summary` exists but is not callable."

        # 2) Test Case 1: provided sales.txt inside this question folder
        # NOTE: validator.py sits inside questions/<folder>/validator.py
        # so sales.txt is in the same directory as this file.
        base_dir = os.path.dirname(__file__)
        sales_path = os.path.join(base_dir, "sales.txt")

        if not os.path.exists(sales_path):
            return "⚠️ Validation error: sales.txt not found in the question folder."

        out1 = func(sales_path)

        if not isinstance(out1, dict):
            return "❌ Output must be a dictionary."

        expected1 = {
            "Apple": 169.75,
            "Banana": 50.50,
            "Milk": 70.40,
            "Bread": 35.75,
            "Eggs": 80.00
        }

        # keys must match exactly
        if set(out1.keys()) != set(expected1.keys()):
            return f"❌ Dictionary keys mismatch. Expected keys: {sorted(expected1.keys())}"

        # values must match (tolerance)
        for k, v in expected1.items():
            if k not in out1:
                return f"❌ Missing key: {k}"
            if not _approx_equal(out1[k], v):
                return f"❌ Incorrect total for '{k}'. Expected {v}, got {out1[k]}"

        # 3) Test Case 2: hidden temp file (generalization)
        hidden_data = """Apple,10
Apple,2.25
Banana,5.5
Milk,1
Milk,2
"""

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write(hidden_data)
            tmp_path = f.name

        try:
            out2 = func(tmp_path)

            if not isinstance(out2, dict):
                return "❌ Output must be a dictionary."

            expected2 = {"Apple": 12.25, "Banana": 5.50, "Milk": 3.00}

            if set(out2.keys()) != set(expected2.keys()):
                return "❌ Hidden test failed: keys mismatch."

            for k, v in expected2.items():
                if not _approx_equal(out2[k], v):
                    return f"❌ Hidden test failed: '{k}' expected {v}, got {out2[k]}"
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass

        return "✅ Correct! Well done."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"

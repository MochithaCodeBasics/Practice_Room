import os
import math
import tempfile

def _approx_equal(a: float, b: float, tol: float = 1e-2) -> bool:
    return math.isclose(float(a), float(b), abs_tol=tol, rel_tol=0.0)


def _run_file_test(func, file_content, expected, label):
    """Create a temp file, run func, compare to expected dict, clean up."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write(file_content)
        tmp_path = f.name

    try:
        out = func(tmp_path)

        if not isinstance(out, dict):
            return f"❌ {label}: Output must be a dictionary."

        if set(out.keys()) != set(expected.keys()):
            return f"❌ {label}: Dictionary keys mismatch."

        for k, v in expected.items():
            if k not in out:
                return f"❌ {label}: Missing key."
            if not _approx_equal(out[k], v):
                return f"❌ {label}: Incorrect total for a product."
        return None
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


def validate(user_module) -> str:
    try:
        # 1) Function existence
        if not hasattr(user_module, "generate_sales_summary"):
            return "❌ Function `generate_sales_summary(file_path)` is not defined."

        func = getattr(user_module, "generate_sales_summary")

        if not callable(func):
            return "❌ `generate_sales_summary` exists but is not callable."

        # ── Test Case 1: bundled sales.txt ──
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

        if set(out1.keys()) != set(expected1.keys()):
            return "❌ Test case 1: Dictionary keys mismatch."

        for k, v in expected1.items():
            if k not in out1:
                return "❌ Test case 1: Missing key."
            if not _approx_equal(out1[k], v):
                return "❌ Test case 1: Incorrect total for a product."

        # ── Test Case 2: hidden – basic aggregation ──
        hidden2 = "Apple,10\nApple,2.25\nBanana,5.5\nMilk,1\nMilk,2\n"
        expected2 = {"Apple": 12.25, "Banana": 5.50, "Milk": 3.00}
        err = _run_file_test(func, hidden2, expected2, "Hidden test 1")
        if err:
            return err

        # ── Test Case 3: hidden – single product ──
        hidden3 = "Widget,99.99\nWidget,0.01\n"
        expected3 = {"Widget": 100.0}
        err = _run_file_test(func, hidden3, expected3, "Hidden test 2")
        if err:
            return err

        # ── Test Case 4: hidden – single line ──
        hidden4 = "Laptop,1500.50\n"
        expected4 = {"Laptop": 1500.50}
        err = _run_file_test(func, hidden4, expected4, "Hidden test 3")
        if err:
            return err

        # ── Test Case 5: hidden – many products, decimal precision ──
        hidden5 = (
            "A,0.10\nB,0.20\nC,0.30\nA,0.10\nB,0.20\nC,0.30\n"
            "A,0.10\nB,0.20\nC,0.30\n"
        )
        expected5 = {"A": 0.30, "B": 0.60, "C": 0.90}
        err = _run_file_test(func, hidden5, expected5, "Hidden test 4")
        if err:
            return err

        return "✅ Correct! All test cases passed successfully."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"

import random
import math


def _approx_equal(a: float, b: float, tol: float = 1e-2) -> bool:
    return math.isclose(float(a), float(b), abs_tol=tol, rel_tol=0.0)


def validate(user_module) -> str:
    try:
        if not hasattr(user_module, "calculate_final_price"):
            return "❌ Function calculate_final_price is not defined."

        func = user_module.calculate_final_price

        # --- Helper to verify one call ---
        def _check(args, kwargs, expected, label):
            result = round(func(*args, **kwargs), 2)
            if not _approx_equal(result, expected):
                return f"❌ {label} failed."
            return None

        # Test Case 1 – matches the example in the problem
        err = _check((1000, 50, 100), {"coupon": 10, "loyalty": 5}, 983.25, "Test case 1")
        if err:
            return err

        # Test Case 2 – args + single kwarg
        # 500 + 20 = 520 → 10% off → 468.0
        err = _check((500, 20), {"tax": 10}, 468.0, "Test case 2")
        if err:
            return err

        # Test Case 3 – only extra args, no kwargs
        # 300 + 50 + 25 = 375.0
        err = _check((300, 50, 25), {}, 375.0, "Test case 3")
        if err:
            return err

        # Test Case 4 – base price only
        err = _check((1000,), {}, 1000.0, "Test case 4")
        if err:
            return err

        # Test Case 5 – edge: zero extra charges, one zero-percent discount
        # 250 → 0% discount → 250.0
        err = _check((250,), {"promo": 0}, 250.0, "Test case 5")
        if err:
            return err

        # Test Case 6 – edge: many kwargs applied sequentially
        # 1000 → 10% off → 900 → 20% off → 720 → 5% off → 684.0
        err = _check((1000,), {"a": 10, "b": 20, "c": 5}, 684.0, "Test case 6")
        if err:
            return err

        # Test Case 7 – hidden dynamic test (random values)
        random.seed(42)  # deterministic but hidden from learner
        base = random.randint(100, 5000)
        extras = [random.randint(10, 200) for _ in range(random.randint(1, 4))]
        discounts = {f"d{i}": random.randint(1, 20) for i in range(random.randint(1, 3))}

        # Compute expected answer
        total = base + sum(extras)
        for pct in discounts.values():
            total *= (1 - pct / 100)
        expected = round(total, 2)

        result = round(func(base, *extras, **discounts), 2)
        if not _approx_equal(result, expected):
            return "❌ Hidden test case failed."

        return "✅ Correct! All test cases passed successfully."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"

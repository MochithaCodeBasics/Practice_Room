import math
import random

def _approx_equal(a: float, b: float, tol: float = 1e-2) -> bool:
    """Check if two floats are approximately equal within tolerance."""
    return math.isclose(float(a), float(b), abs_tol=tol, rel_tol=0.0)


def validate(user_module) -> str:
    try:
        # ── 1) Check class existence ──
        if not hasattr(user_module, "DiscountCalculator"):
            return "❌ Class `DiscountCalculator` is not defined."

        if not hasattr(user_module, "RegularCustomer"):
            return "❌ Class `RegularCustomer` is not defined."

        if not hasattr(user_module, "PremiumCustomer"):
            return "❌ Class `PremiumCustomer` is not defined."

        DiscountCalculator = user_module.DiscountCalculator
        RegularCustomer = user_module.RegularCustomer
        PremiumCustomer = user_module.PremiumCustomer

        # ── 2) Check inheritance ──
        if not issubclass(RegularCustomer, DiscountCalculator):
            return "❌ `RegularCustomer` must inherit from `DiscountCalculator`."

        if not issubclass(PremiumCustomer, DiscountCalculator):
            return "❌ `PremiumCustomer` must inherit from `DiscountCalculator`."

        # ── 3) TypeError for non-numeric input ──
        try:
            customer = RegularCustomer("invalid")
            customer.final_amount()
            return "❌ Expected `TypeError` for non-numeric amount, but no exception was raised."
        except TypeError:
            pass
        except Exception as e:
            return f"❌ Expected `TypeError` for non-numeric amount, got {type(e).__name__}."

        # ── 4) ValueError for negative amount ──
        try:
            customer = RegularCustomer(-100)
            customer.final_amount()
            return "❌ Expected `ValueError` for negative amount, but no exception was raised."
        except ValueError:
            pass
        except Exception as e:
            return f"❌ Expected `ValueError` for negative amount, got {type(e).__name__}."

        # ── 5) ValueError for zero amount ──
        try:
            customer = PremiumCustomer(0)
            customer.final_amount()
            return "❌ Expected `ValueError` for zero amount, but no exception was raised."
        except ValueError:
            pass
        except Exception as e:
            return f"❌ Expected `ValueError` for zero amount, got {type(e).__name__}."

        # ── 6) RegularCustomer discount (5%) – example values ──
        regular = RegularCustomer(1000)
        if not _approx_equal(regular.final_amount(), 950.0):
            return "❌ Test case 1 failed (RegularCustomer)."

        regular2 = RegularCustomer(200)
        if not _approx_equal(regular2.final_amount(), 190.0):
            return "❌ Test case 2 failed (RegularCustomer)."

        # ── 7) PremiumCustomer discount (15%) – example values ──
        premium = PremiumCustomer(1000)
        if not _approx_equal(premium.final_amount(), 850.0):
            return "❌ Test case 3 failed (PremiumCustomer)."

        premium2 = PremiumCustomer(500)
        if not _approx_equal(premium2.final_amount(), 425.0):
            return "❌ Test case 4 failed (PremiumCustomer)."

        # ── 8) Hidden dynamic tests with random amounts ──
        random.seed(99)
        for i in range(3):
            amount = round(random.uniform(50, 10000), 2)

            r = RegularCustomer(amount)
            expected_regular = round(amount * 0.95, 2)
            if not _approx_equal(r.final_amount(), expected_regular):
                return f"❌ Hidden test {i + 1} failed (RegularCustomer)."

            p = PremiumCustomer(amount)
            expected_premium = round(amount * 0.85, 2)
            if not _approx_equal(p.final_amount(), expected_premium):
                return f"❌ Hidden test {i + 1} failed (PremiumCustomer)."

        # ── 9) Edge: float amount ──
        r_float = RegularCustomer(99.99)
        expected_float = round(99.99 * 0.95, 2)
        if not _approx_equal(r_float.final_amount(), expected_float):
            return "❌ Hidden test failed (float amount)."

        return "✅ Correct! All test cases passed successfully."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"

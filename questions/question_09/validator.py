import math

def _approx_equal(a: float, b: float, tol: float = 1e-2) -> bool:
    """Check if two floats are approximately equal within tolerance."""
    return math.isclose(float(a), float(b), abs_tol=tol, rel_tol=0.0)


def validate(user_module) -> str:
    try:
        # 1) Check if all required classes exist
        if not hasattr(user_module, "DiscountCalculator"):
            return "❌ Class `DiscountCalculator` is not defined."
        
        if not hasattr(user_module, "RegularCustomer"):
            return "❌ Class `RegularCustomer` is not defined."
        
        if not hasattr(user_module, "PremiumCustomer"):
            return "❌ Class `PremiumCustomer` is not defined."
        
        DiscountCalculator = user_module.DiscountCalculator
        RegularCustomer = user_module.RegularCustomer
        PremiumCustomer = user_module.PremiumCustomer
        
        # 2) Check inheritance
        if not issubclass(RegularCustomer, DiscountCalculator):
            return "❌ `RegularCustomer` must inherit from `DiscountCalculator`."
        
        if not issubclass(PremiumCustomer, DiscountCalculator):
            return "❌ `PremiumCustomer` must inherit from `DiscountCalculator`."
        
        # 3) Test TypeError for invalid type
        try:
            customer = RegularCustomer("invalid")
            customer.final_amount()
            return "❌ Expected `TypeError` for non-numeric amount, but no exception was raised."
        except TypeError:
            pass  # Expected behavior
        except Exception as e:
            return f"❌ Expected `TypeError` for non-numeric amount, got {type(e).__name__}: {str(e)}"
        
        # 4) Test ValueError for non-positive amount
        try:
            customer = RegularCustomer(-100)
            customer.final_amount()
            return "❌ Expected `ValueError` for negative amount, but no exception was raised."
        except ValueError:
            pass  # Expected behavior
        except Exception as e:
            return f"❌ Expected `ValueError` for negative amount, got {type(e).__name__}: {str(e)}"
        
        try:
            customer = PremiumCustomer(0)
            customer.final_amount()
            return "❌ Expected `ValueError` for zero amount, but no exception was raised."
        except ValueError:
            pass  # Expected behavior
        except Exception as e:
            return f"❌ Expected `ValueError` for zero amount, got {type(e).__name__}: {str(e)}"
        
        # 5) Test RegularCustomer discount (5%)
        regular = RegularCustomer(1000)
        regular_result = regular.final_amount()
        if not _approx_equal(regular_result, 950.0):
            return f"❌ RegularCustomer(1000).final_amount() expected 950.0, got {regular_result}"
        
        regular2 = RegularCustomer(200)
        regular2_result = regular2.final_amount()
        if not _approx_equal(regular2_result, 190.0):
            return f"❌ RegularCustomer(200).final_amount() expected 190.0, got {regular2_result}"
        
        # 6) Test PremiumCustomer discount (15%)
        premium = PremiumCustomer(1000)
        premium_result = premium.final_amount()
        if not _approx_equal(premium_result, 850.0):
            return f"❌ PremiumCustomer(1000).final_amount() expected 850.0, got {premium_result}"
        
        premium2 = PremiumCustomer(500)
        premium2_result = premium2.final_amount()
        if not _approx_equal(premium2_result, 425.0):
            return f"❌ PremiumCustomer(500).final_amount() expected 425.0, got {premium2_result}"
        
        return "✅ Correct! Well done."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"

def validate(user_module) -> str:
    try:
        if not hasattr(user_module, "calculate_final_price"):
            return "❌ Function calculate_final_price is not defined."

        func = user_module.calculate_final_price

        # Test Case 1
        result1 = func(1000, 50, 100, coupon=10, loyalty=5)
        if round(result1, 2) != 983.25:
            return "❌ Test case 1 failed."

        # Test Case 2
        result2 = func(500, 20, tax=10)
        # 500 + 20 = 520 → 10% discount → 468
        if round(result2, 2) != 468.0:
            return "❌ Test case 2 failed."

        # Test Case 3 (no discounts)
        result3 = func(300, 50, 25)
        if round(result3, 2) != 375.0:
            return "❌ Test case 3 failed."

        # Test Case 4 (only base price)
        result4 = func(1000)
        if round(result4, 2) != 1000.0:
            return "❌ Test case 4 failed."

        return "✅ Correct! Well done."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"

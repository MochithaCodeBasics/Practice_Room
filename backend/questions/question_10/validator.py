import sys
import os

def validate(module):
    try:
        if not hasattr(module, "calculate_final_price"):
            return "Function 'calculate_final_price' not found! make sure you wrap your function with that name"
        
        func = module.calculate_final_price
        
        # Test Case 1: Example from description
        # 1000 + 50 + 100 = 1150
        # coupon 10%: 1150 * 0.9 = 1035
        # loyalty 5%: 1035 * 0.95 = 983.25
        res1 = func(1000, 50, 100, coupon=10, loyalty=5)
        if not isinstance(res1, (int, float)):
             return f"Function should return a number, but returned {type(res1).__name__}"
             
        if abs(res1 - 983.25) > 0.01:
            return f"❌ Test Case 1 Failed.\nInput: base=1000, charges=(50, 100), discounts={{coupon:10, loyalty:5}}\nExpected: 983.25\nGot: {res1}"

        # Test Case 2: No extra charges, no discounts
        res2 = func(100)
        if abs(res2 - 100.0) > 0.01:
             return f"❌ Test Case 2 Failed.\nInput: base=100\nExpected: 100.0\nGot: {res2}"

        # Test Case 3: Just charges
        res3 = func(100, 50, 50)
        if abs(res3 - 200.0) > 0.01:
             return f"❌ Test Case 3 Failed.\nInput: base=100, charges=(50, 50)\nExpected: 200.0\nGot: {res3}"
             
        # Test Case 4: Multiple discounts (sequential application)
        # 100. Discount 50% -> 50. Discount 50% -> 25.
        res4 = func(100, discount1=50, discount2=50)
        # Order of kwargs is insertion order in Python 3.7+, but let's assume standard dict iteration order
        # If order matters for sequential discounts (it mathematically does: A*(1-d1)*(1-d2) == A*(1-d2)*(1-d1) IF multiplicative)
        # Wait, the problem says "sequentially on the running total".
        # Yes, multiplication is commutative so order doesn't matter for independent percentages applied to the *current* total.
        # Total = Base * (1-d1) * (1-d2) ...
        # So 100 * 0.5 * 0.5 = 25.
        if abs(res4 - 25.0) > 0.01:
             return f"❌ Test Case 4 Failed (Sequential Discounts).\nInput: base=100, discounts={{d1:50, d2:50}}\nExpected: 25.0\nGot: {res4}"

        return "✅ Correct! All test cases passed."
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Validation Logic Error: {str(e)}"

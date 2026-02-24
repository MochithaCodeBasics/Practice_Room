description = """### Task
An e-commerce platform needs a flexible pricing function that can handle different
types of charges and discounts during checkout.

The base price of an order is always known, but additional costs like taxes, shipping,
and packaging may vary. Optional discounts such as coupons or loyalty discounts may
also apply.

Your task is to build a reusable Python function that calculates the final payable
amount using *args, **kwargs, and a lambda function.

### Requirements
- Define a function named `calculate_final_price`
- Take a required argument `base_price`
- Accept a flexible number of additional charges
- Accept optional keyword-based percentage discounts
- Apply all discounts sequentially on the running total
- Return the final payable amount rounded to **2 decimal places**

### Example

Input:
calculate_final_price(
    1000,
    50, 100,
    coupon=10,
    loyalty=5
)

Explanation:
- Base price = 1000
- Extra charges = 50 + 100 → 1150
- Apply 10% discount → 1035
- Apply 5% discount → 983.25

Output:
983.25

### Function Signature
```python
def solution(...):
```

### Return
The function should return the result as specified in the task.

### Hint
Think about how Python functions can accept a flexible number of inputs.
Recall how *args and **kwargs behave inside a function.
Consider how percentage-based discounts should affect a running total.

"""

hint = """Think about how Python functions can accept a flexible number of inputs.
Recall how *args and **kwargs behave inside a function.
Consider how percentage-based discounts should affect a running total."""

initial_sample_code = """# Create a function named:
# calculate_final_price

# The function should return the final payable amount


# ============================================================
# Uncomment below to see the output
# ============================================================
# if __name__ == "__main__":
#     result = calculate_final_price(1000, 50, 100, coupon=10, loyalty=5)
#     print(result)"""

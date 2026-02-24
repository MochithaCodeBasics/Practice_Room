description = """### Task
A retail billing system applies discounts differently depending on the customer type.

All discount calculators share common validation rules, but each customer type has its own discount logic.

Your task is to implement this using inheritance and validate inputs using built-in exceptions.

### Requirements

Create a base class `DiscountCalculator` with:

- `__init__(self, amount)` to store the amount

- `validate(self)` method that:

  - raises `TypeError` if `amount` is not an `int` or `float`

  - raises `ValueError` if `amount <= 0`

- `final_amount(self)` method that raises `NotImplementedError`

Create two subclasses:

`RegularCustomer(DiscountCalculator)`

- `final_amount()` applies **5% discount**

`PremiumCustomer(DiscountCalculator)`

- `final_amount()` applies **15% discount**

Each subclass must call `self.validate()` before calculating.

Return the final payable amount rounded to **2 decimals**.

### Example

Input:

```python

regular = RegularCustomer(1000)

print(regular.final_amount())

premium = PremiumCustomer(1000)

print(premium.final_amount())

```

Output:

```

950.0

850.0

```

Explanation:

- RegularCustomer: 1000 - 5% = 950.0

- PremiumCustomer: 1000 - 15% = 850.0

### Required Classes
```python
class DiscountCalculator:
    ...

class RegularCustomer(DiscountCalculator):
    ...

class PremiumCustomer(DiscountCalculator):
    ...
```

### Return
The function should return the result as specified in the task.

"""

hint = """- Use `isinstance()` for type checking.

- Call `self.validate()` before calculations."""

initial_sample_code = """class DiscountCalculator:

    pass



class RegularCustomer(DiscountCalculator):

    pass



class PremiumCustomer(DiscountCalculator):

    pass





# ============================================================

# Uncomment below to see the output

# ============================================================

# if __name__ == "__main__":

#     regular = RegularCustomer(1000)

#     print("Regular:", regular.final_amount())

#     

#     premium = PremiumCustomer(1000)

#     print("Premium:", premium.final_amount())"""

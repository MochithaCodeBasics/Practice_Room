description = """
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
customer = RegularCustomer(1000)
customer.final_amount()

Output:
950.0

Input:
customer = PremiumCustomer(1000)
customer.final_amount()

Output:
850.0
"""

hint = """
- Use `isinstance()` for type checking.
- Call `self.validate()` before calculations.
"""


inital_sample_code = """# Write your solution here

class DiscountCalculator:
    pass

class RegularCustomer(DiscountCalculator):
    pass

class PremiumCustomer(DiscountCalculator):
    pass


"""


def get_description():
    return description

def get_hint():
    return hint

def get_inital_sample_code():
    return inital_sample_code
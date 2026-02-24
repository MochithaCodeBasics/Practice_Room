description = """### Task
A food delivery platform needs an API endpoint to calculate the final payable amount for a customer's order.

Each order contains multiple food items. The platform may optionally apply a service charge, 
and a coupon discount may be applied to the total bill.

Your task is to build a **FastAPI POST endpoint** that accepts order details, validates the request 
using **Pydantic BaseModel**, performs the necessary calculations, and returns a bill summary.

### Requirements

- Create a FastAPI POST endpoint at `/order/total`

- Define a Pydantic model `OrderItem` with:
  - `name` (string)
  - `quantity` (integer)
  - `price` (float)

- Define a Pydantic model `OrderRequest` with:
  - `items` (list of `OrderItem`)
  - `apply_service_charge` (boolean)
  - `coupon_discount` (float)

- Perform the following validations inside the API function:
  - `items` list must not be empty
  - `quantity` must be greater than `0`
  - `price` must be greater than `0`
  - `coupon_discount` must be between `0` and `100` (inclusive)

- If any validation fails, return: `{ "error": "Invalid input" }`

- Calculate:
  - `subtotal` as the sum of (quantity × price) for all items
  - `service_charge` as 5% of subtotal if `apply_service_charge` is true
  - `discount_amount` based on `coupon_discount` percentage
  - `total` payable amount

- Return all monetary values rounded to **2 decimal places**

### Example

Request:
```json
{
  "items": [
    {"name": "Pizza", "quantity": 2, "price": 12.50},
    {"name": "Coke", "quantity": 3, "price": 2.00}
  ],
  "apply_service_charge": true,
  "coupon_discount": 10
}
```

Response:
```json
{
  "subtotal": 31.00,
  "service_charge": 1.55,
  "discount_amount": 3.26,
  "total": 29.29
}
```

### API Contract
- FastAPI app instance named `app`
- POST endpoint at `/order/total`
- Pydantic models `OrderItem` and `OrderRequest`

### Return
The function should return the result as specified in the task.

"""

hint = """- Define Pydantic models before the endpoint.
- Final total = subtotal + service_charge - discount_amount"""

initial_sample_code = """from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

# ============================================================
# Uncomment below to see the output
# ============================================================
# if __name__ == "__main__":
#     from fastapi.testclient import TestClient
#     
#     client = TestClient(app)
#     
#     request = {
#         "items": [
#             {"name": "Pizza", "quantity": 2, "price": 12.50},
#             {"name": "Coke", "quantity": 3, "price": 2.00}
#         ],
#         "apply_service_charge": True,
#         "coupon_discount": 10
#     }
#     
#     response = client.post("/order/total", json=request)
#     print(f"Response: {response.json()}")"""

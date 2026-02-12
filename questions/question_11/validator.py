import math


def _approx_equal(a: float, b: float, tol: float = 0.01) -> bool:
    """Check if two floats are approximately equal within tolerance."""
    return math.isclose(float(a), float(b), abs_tol=tol, rel_tol=0.01)


def validate(user_module) -> str:
    try:
        # 1) Check if FastAPI app exists
        if not hasattr(user_module, "app"):
            return "❌ FastAPI `app` instance is not defined."
        
        app = user_module.app
        
        # 2) Check if Pydantic models exist
        if not hasattr(user_module, "OrderItem"):
            return "❌ Pydantic model `OrderItem` is not defined."
        
        if not hasattr(user_module, "OrderRequest"):
            return "❌ Pydantic model `OrderRequest` is not defined."
        
        # 3) Check if endpoint exists by testing with TestClient
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # 4) Test valid request
        valid_request = {
            "items": [
                {"name": "Pizza", "quantity": 2, "price": 12.50},
                {"name": "Coke", "quantity": 3, "price": 2.00}
            ],
            "apply_service_charge": True,
            "coupon_discount": 10
        }
        
        response = client.post("/order/total", json=valid_request)
        
        if response.status_code != 200:
            return f"❌ Endpoint returned status {response.status_code}, expected 200."
        
        data = response.json()
        
        # Check response keys
        required_keys = ["subtotal", "service_charge", "discount_amount", "total"]
        for key in required_keys:
            if key not in data:
                return f"❌ Response missing required key: `{key}`"
        
        # Verify calculations
        # subtotal = 2*12.50 + 3*2.00 = 25 + 6 = 31.00
        # service_charge = 31.00 * 0.05 = 1.55
        # discount_amount = (31.00 + 1.55) * 0.10 = 3.255 ≈ 3.26
        # total = 31.00 + 1.55 - 3.26 = 29.29
        
        if not _approx_equal(data["subtotal"], 31.00):
            return f"❌ Subtotal expected 31.00, got {data['subtotal']}"
        
        if not _approx_equal(data["service_charge"], 1.55):
            return f"❌ Service charge expected 1.55, got {data['service_charge']}"
        
        if not _approx_equal(data["discount_amount"], 3.26):
            return f"❌ Discount amount expected 3.26, got {data['discount_amount']}"
        
        if not _approx_equal(data["total"], 29.29):
            return f"❌ Total expected 29.29, got {data['total']}"
        
        # 5) Test with service charge disabled
        no_service_request = {
            "items": [
                {"name": "Burger", "quantity": 1, "price": 10.00}
            ],
            "apply_service_charge": False,
            "coupon_discount": 0
        }
        
        response2 = client.post("/order/total", json=no_service_request)
        data2 = response2.json()
        
        if not _approx_equal(data2["subtotal"], 10.00):
            return f"❌ Test 2: Subtotal expected 10.00, got {data2['subtotal']}"
        
        if not _approx_equal(data2["service_charge"], 0.0):
            return f"❌ Test 2: Service charge expected 0.0, got {data2['service_charge']}"
        
        if not _approx_equal(data2["total"], 10.00):
            return f"❌ Test 2: Total expected 10.00, got {data2['total']}"
        
        # 6) Test invalid input - empty items
        invalid_request1 = {
            "items": [],
            "apply_service_charge": True,
            "coupon_discount": 10
        }
        
        response3 = client.post("/order/total", json=invalid_request1)
        data3 = response3.json()
        
        if "error" not in data3 or data3["error"] != "Invalid input":
            return "❌ Empty items list should return {'error': 'Invalid input'}"
        
        # 7) Test invalid input - negative price
        invalid_request2 = {
            "items": [
                {"name": "Item", "quantity": 1, "price": -5.00}
            ],
            "apply_service_charge": False,
            "coupon_discount": 0
        }
        
        response4 = client.post("/order/total", json=invalid_request2)
        data4 = response4.json()
        
        if "error" not in data4 or data4["error"] != "Invalid input":
            return "❌ Negative price should return {'error': 'Invalid input'}"
        
        # 8) Test invalid input - coupon_discount > 100
        invalid_request3 = {
            "items": [
                {"name": "Item", "quantity": 1, "price": 10.00}
            ],
            "apply_service_charge": False,
            "coupon_discount": 150
        }
        
        response5 = client.post("/order/total", json=invalid_request3)
        data5 = response5.json()
        
        if "error" not in data5 or data5["error"] != "Invalid input":
            return "❌ Coupon discount > 100 should return {'error': 'Invalid input'}"
        
        return "✅ Correct! Well done."

    except ImportError as e:
        return f"⚠️ Import error: {str(e)}. Make sure FastAPI and httpx are installed."
    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"

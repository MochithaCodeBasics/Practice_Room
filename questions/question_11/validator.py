import math
import random


def _approx_equal(a: float, b: float, tol: float = 0.01) -> bool:
    """Check if two floats are approximately equal within tolerance."""
    return math.isclose(float(a), float(b), abs_tol=tol, rel_tol=0.01)


def _compute_expected(items, apply_service_charge, coupon_discount):
    """Mirror the expected calculation logic to generate hidden answers."""
    subtotal = round(sum(i["quantity"] * i["price"] for i in items), 2)
    service_charge = round(subtotal * 0.05, 2) if apply_service_charge else 0.0
    discount_amount = round((subtotal + service_charge) * coupon_discount / 100, 2)
    total = round(subtotal + service_charge - discount_amount, 2)
    return {
        "subtotal": subtotal,
        "service_charge": service_charge,
        "discount_amount": discount_amount,
        "total": total,
    }


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

        # 3) Set up test client
        from fastapi.testclient import TestClient
        client = TestClient(app)

        # ── Helper to run one happy-path test ──
        def _check_happy(request_body, label):
            response = client.post("/order/total", json=request_body)
            if response.status_code != 200:
                return f"❌ {label}: Expected status 200, got {response.status_code}."

            data = response.json()

            required_keys = ["subtotal", "service_charge", "discount_amount", "total"]
            for key in required_keys:
                if key not in data:
                    return f"❌ {label}: Response missing required key `{key}`."

            expected = _compute_expected(
                request_body["items"],
                request_body["apply_service_charge"],
                request_body["coupon_discount"],
            )

            for key in required_keys:
                if not _approx_equal(data[key], expected[key]):
                    return f"❌ {label}: `{key}` value is incorrect."
            return None

        # ── Helper to run one invalid-input test ──
        def _check_invalid(request_body, label):
            response = client.post("/order/total", json=request_body)
            data = response.json()
            if "error" not in data or data["error"] != "Invalid input":
                return f"❌ {label}: Should return {{'error': 'Invalid input'}}."
            return None

        # ── Test Case 1: valid – matches the example ──
        err = _check_happy({
            "items": [
                {"name": "Pizza", "quantity": 2, "price": 12.50},
                {"name": "Coke", "quantity": 3, "price": 2.00}
            ],
            "apply_service_charge": True,
            "coupon_discount": 10
        }, "Test case 1")
        if err:
            return err

        # ── Test Case 2: valid – no service charge, no coupon ──
        err = _check_happy({
            "items": [
                {"name": "Burger", "quantity": 1, "price": 10.00}
            ],
            "apply_service_charge": False,
            "coupon_discount": 0
        }, "Test case 2")
        if err:
            return err

        # ── Test Case 3: valid – boundary coupon_discount=100 ──
        err = _check_happy({
            "items": [
                {"name": "Salad", "quantity": 2, "price": 5.00}
            ],
            "apply_service_charge": True,
            "coupon_discount": 100
        }, "Test case 3")
        if err:
            return err

        # ── Test Case 4: hidden – dynamic random order ──
        random.seed(77)
        hidden_items = [
            {"name": f"Item{j}", "quantity": random.randint(1, 5), "price": round(random.uniform(1, 50), 2)}
            for j in range(random.randint(2, 5))
        ]
        err = _check_happy({
            "items": hidden_items,
            "apply_service_charge": True,
            "coupon_discount": round(random.uniform(0, 50), 2)
        }, "Hidden test 1")
        if err:
            return err

        # ── Test Case 5: hidden – another random order without service charge ──
        hidden_items2 = [
            {"name": f"Food{j}", "quantity": random.randint(1, 10), "price": round(random.uniform(5, 100), 2)}
            for j in range(random.randint(1, 3))
        ]
        err = _check_happy({
            "items": hidden_items2,
            "apply_service_charge": False,
            "coupon_discount": round(random.uniform(0, 30), 2)
        }, "Hidden test 2")
        if err:
            return err

        # ── Invalid Input Tests ──

        # Test 6: empty items
        err = _check_invalid({
            "items": [],
            "apply_service_charge": True,
            "coupon_discount": 10
        }, "Validation test 1 (empty items)")
        if err:
            return err

        # Test 7: negative price
        err = _check_invalid({
            "items": [{"name": "Item", "quantity": 1, "price": -5.00}],
            "apply_service_charge": False,
            "coupon_discount": 0
        }, "Validation test 2 (negative price)")
        if err:
            return err

        # Test 8: coupon > 100
        err = _check_invalid({
            "items": [{"name": "Item", "quantity": 1, "price": 10.00}],
            "apply_service_charge": False,
            "coupon_discount": 150
        }, "Validation test 3 (coupon > 100)")
        if err:
            return err

        # Test 9: zero quantity
        err = _check_invalid({
            "items": [{"name": "Item", "quantity": 0, "price": 10.00}],
            "apply_service_charge": False,
            "coupon_discount": 0
        }, "Validation test 4 (zero quantity)")
        if err:
            return err

        # Test 10: negative coupon
        err = _check_invalid({
            "items": [{"name": "Item", "quantity": 1, "price": 10.00}],
            "apply_service_charge": False,
            "coupon_discount": -5
        }, "Validation test 5 (negative coupon)")
        if err:
            return err

        return "✅ Correct! All test cases passed successfully."

    except ImportError as e:
        return f"⚠️ Import error: {str(e)}. Make sure FastAPI and httpx are installed."
    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"

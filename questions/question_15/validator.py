def validate(user_module):
    if not hasattr(user_module, "extract_financial_info"):
        return "❌ Function extract_financial_info is not defined."

    text = "John paid 4500 for office supplies"
    result = user_module.extract_financial_info(text)

    if not isinstance(result, dict):
        return "❌ Output must be a dictionary."

    required_keys = {"name", "amount", "category"}
    if set(result.keys()) != required_keys:
        return "❌ Output dictionary must contain name, amount, and category."

    if not isinstance(result["name"], str):
        return "❌ name must be a string."

    if not isinstance(result["amount"], int):
        return "❌ amount must be an integer."

    if not isinstance(result["category"], str):
        return "❌ category must be a string."

    return "✅ Correct! Structured information extracted successfully."
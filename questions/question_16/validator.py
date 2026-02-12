def validate(user_module) -> str:
    try:
        if not hasattr(user_module, "simple_tool_agent"):
            return "❌ Function simple_tool_agent is not defined."

        func = user_module.simple_tool_agent

        result = func("What is 3 + 5?")
        if not isinstance(result, str):
            return "❌ Output must be a string."

        if "8" not in result:
            return "❌ Agent did not correctly use the tool to compute 3 + 5."

        return "✅ Correct! Well done."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"
def validate(user_module, user_code=None, user_df=None):
    try:
        if not hasattr(user_module, 'sum_list'):
            return "❌ Function `sum_list` not found."
            
        test_cases = [
            ([1, 2, 3], 6),
            ([10, -5, 2], 7),
            ([], 0)
        ]
        
        for nums, expected in test_cases:
            result = user_module.sum_list(nums)
            if result != expected:
                return f"❌ Failed for {nums}. Expected {expected}, got {result}."
                
        return "✅ Success! All test cases passed."
    except Exception as e:
        return f"❌ Error: {str(e)}"

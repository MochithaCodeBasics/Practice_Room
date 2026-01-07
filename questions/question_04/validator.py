import math


def _approx_equal(a, b, tol=0.01):
    """Check if two values are approximately equal."""
    return math.isclose(float(a), float(b), abs_tol=tol, rel_tol=0.01)


def validate(user_module) -> str:
    """
    Validates the calculate_marketing_probabilities function.
    
    Checks:
    1. Function exists and is callable
    2. Output has required structure
    3. Values match expected to 2 decimal places
    """
    try:
        # Check if function exists
        if not hasattr(user_module, "calculate_marketing_probabilities"):
            return "❌ Function `calculate_marketing_probabilities` is not defined."

        func = user_module.calculate_marketing_probabilities

        # Check if it's callable
        if not callable(func):
            return "❌ `calculate_marketing_probabilities` is not callable."

        # Call the function
        result = func()

        # Check if result is a dictionary
        if not isinstance(result, dict):
            return f"❌ Expected dict, got {type(result).__name__}"

        # Check required keys
        required_keys = ['overall_conversion_prob', 'bayes_results', 'at_least_two_channels_prob']
        for key in required_keys:
            if key not in result:
                return f"❌ Missing required key: `{key}`"

        # Check bayes_results structure
        if not isinstance(result['bayes_results'], dict):
            return "❌ `bayes_results` should be a dictionary."

        bayes_keys = ['Email', 'Social', 'Website']
        for key in bayes_keys:
            if key not in result['bayes_results']:
                return f"❌ Missing key in bayes_results: `{key}`"

        # -------------------------------------------------
        # Compute expected values
        # -------------------------------------------------
        # Channel probabilities
        p_email = 0.40
        p_social = 0.35
        p_website = 0.25

        # Conversion rates given channel
        p_conv_email = 0.12
        p_conv_social = 0.08
        p_conv_website = 0.15

        # Overall conversion probability (law of total probability)
        p_convert = (p_email * p_conv_email + 
                     p_social * p_conv_social + 
                     p_website * p_conv_website)
        expected_overall = round(p_convert, 2)

        # Bayes' theorem: P(Channel | Converted)
        p_email_given_conv = round((p_email * p_conv_email) / p_convert, 2)
        p_social_given_conv = round((p_social * p_conv_social) / p_convert, 2)
        p_website_given_conv = round((p_website * p_conv_website) / p_convert, 2)

        # At least 2 channels (using independence)
        # P(at least 2) = P(E∩S∩W') + P(E∩S'∩W) + P(E'∩S∩W) + P(E∩S∩W)
        p_exactly_es = p_email * p_social * (1 - p_website)
        p_exactly_ew = p_email * (1 - p_social) * p_website
        p_exactly_sw = (1 - p_email) * p_social * p_website
        p_all_three = p_email * p_social * p_website
        p_at_least_two = p_exactly_es + p_exactly_ew + p_exactly_sw + p_all_three
        expected_at_least_two = round(p_at_least_two, 2)

        # -------------------------------------------------
        # Validate values
        # -------------------------------------------------
        if not _approx_equal(result['overall_conversion_prob'], expected_overall):
            return f"❌ `overall_conversion_prob` mismatch: expected {expected_overall}, got {result['overall_conversion_prob']}"

        if not _approx_equal(result['bayes_results']['Email'], p_email_given_conv):
            return f"❌ `bayes_results['Email']` mismatch: expected {p_email_given_conv}, got {result['bayes_results']['Email']}"

        if not _approx_equal(result['bayes_results']['Social'], p_social_given_conv):
            return f"❌ `bayes_results['Social']` mismatch: expected {p_social_given_conv}, got {result['bayes_results']['Social']}"

        if not _approx_equal(result['bayes_results']['Website'], p_website_given_conv):
            return f"❌ `bayes_results['Website']` mismatch: expected {p_website_given_conv}, got {result['bayes_results']['Website']}"

        if not _approx_equal(result['at_least_two_channels_prob'], expected_at_least_two):
            return f"❌ `at_least_two_channels_prob` mismatch: expected {expected_at_least_two}, got {result['at_least_two_channels_prob']}"

        return "✅ Correct! Marketing probability calculations are valid."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"

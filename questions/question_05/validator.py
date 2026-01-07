import math
from scipy import stats


def _approx_equal(a, b, tol=0.01):
    """Check if two values are approximately equal."""
    return math.isclose(float(a), float(b), abs_tol=tol, rel_tol=0.01)


def validate(user_module) -> str:
    """
    Validates the test_website_conversion function.
    
    Checks:
    1. Function exists and is callable
    2. Output has required structure
    3. Values match expected to appropriate decimal places
    """
    try:
        # Check if function exists
        if not hasattr(user_module, "test_website_conversion"):
            return "❌ Function `test_website_conversion` is not defined."

        func = user_module.test_website_conversion

        # Check if it's callable
        if not callable(func):
            return "❌ `test_website_conversion` is not callable."

        # Call the function
        result = func()

        # Check if result is a dictionary
        if not isinstance(result, dict):
            return f"❌ Expected dict, got {type(result).__name__}"

        # Check required keys
        required_keys = ['null_hypothesis', 'alternative_hypothesis', 'significance_level', 
                        'test_statistic', 'p_value', 'decision']
        for key in required_keys:
            if key not in result:
                return f"❌ Missing required key: `{key}`"

        # -------------------------------------------------
        # Compute expected values
        # -------------------------------------------------
        # Given data
        n1 = 5000  # Control group size
        x1 = 450   # Control conversions
        n2 = 5000  # Treatment group size
        x2 = 485   # Treatment conversions

        p1 = x1 / n1  # 0.09
        p2 = x2 / n2  # 0.097

        # Pooled proportion
        p_pooled = (x1 + x2) / (n1 + n2)

        # Standard error
        se = math.sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2))

        # Z-statistic
        z_stat = (p2 - p1) / se
        expected_z = round(z_stat, 2)

        # P-value (one-tailed, upper tail since we test if new > old)
        p_value = 1 - stats.norm.cdf(z_stat)
        expected_p = round(p_value, 4)

        # Significance level (common choice)
        expected_alpha = 0.05

        # Decision
        if p_value < expected_alpha:
            expected_decision = "Reject H0"
        else:
            expected_decision = "Fail to reject H0"

        # -------------------------------------------------
        # Validate values
        # -------------------------------------------------
        # Check significance level is reasonable (0.01 - 0.10)
        if not (0.01 <= result['significance_level'] <= 0.10):
            return f"❌ `significance_level` should be between 0.01 and 0.10, got {result['significance_level']}"

        # Validate test statistic
        if not _approx_equal(result['test_statistic'], expected_z, tol=0.1):
            return f"❌ `test_statistic` mismatch: expected ~{expected_z}, got {result['test_statistic']}"

        # Validate p-value
        if not _approx_equal(result['p_value'], expected_p, tol=0.01):
            return f"❌ `p_value` mismatch: expected ~{expected_p}, got {result['p_value']}"

        # Validate decision based on their significance level and p-value
        user_alpha = result['significance_level']
        user_p = result['p_value']
        
        if user_p < user_alpha:
            correct_decision = "Reject H0"
        else:
            correct_decision = "Fail to reject H0"

        # Check decision format (case-insensitive comparison)
        user_decision = result['decision'].strip().lower()
        if "reject" not in user_decision:
            return f"❌ `decision` should contain 'Reject' or 'Fail to reject', got '{result['decision']}'"

        # Check hypotheses are strings
        if not isinstance(result['null_hypothesis'], str) or len(result['null_hypothesis']) < 5:
            return "❌ `null_hypothesis` should be a descriptive string."

        if not isinstance(result['alternative_hypothesis'], str) or len(result['alternative_hypothesis']) < 5:
            return "❌ `alternative_hypothesis` should be a descriptive string."

        return "✅ Correct! Hypothesis testing is valid."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"

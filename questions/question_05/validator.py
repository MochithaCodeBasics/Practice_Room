import math
from scipy import stats


def _approx_equal(a, b, tol=0.01):
    """Check if two values are approximately equal."""
    return math.isclose(float(a), float(b), abs_tol=tol, rel_tol=0.01)


def _compute_expected(n1, x1, n2, x2, alpha):
    """Compute expected z-test results for given inputs."""
    p1 = x1 / n1
    p2 = x2 / n2
    p_pooled = (x1 + x2) / (n1 + n2)
    se = math.sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2))
    z_stat = (p2 - p1) / se
    p_value = 1 - stats.norm.cdf(z_stat)

    if p_value < alpha:
        decision = "reject h0"
    else:
        decision = "fail to reject h0"

    return {
        'z': round(z_stat, 2),
        'p': round(p_value, 4),
        'decision': decision
    }


def _validate_result(result, expected, alpha, label=""):
    """Validate a single result against expected values."""
    prefix = f"{label}: " if label else ""

    if not isinstance(result, dict):
        return f"❌ {prefix}Expected dict, got {type(result).__name__}"

    required_keys = ['null_hypothesis', 'alternative_hypothesis', 'significance_level',
                     'test_statistic', 'p_value', 'decision']
    for key in required_keys:
        if key not in result:
            return f"❌ {prefix}Missing required key: `{key}`"

    # Check significance level matches the alpha passed in
    if not _approx_equal(result['significance_level'], alpha):
        return (f"❌ {prefix}`significance_level` should be {alpha}, "
                f"got {result['significance_level']}")

    # Validate test statistic
    if not _approx_equal(result['test_statistic'], expected['z'], tol=0.1):
        return (f"❌ {prefix}`test_statistic` mismatch: "
                f"expected ~{expected['z']}, got {result['test_statistic']}")

    # Validate p-value
    if not _approx_equal(result['p_value'], expected['p'], tol=0.01):
        return (f"❌ {prefix}`p_value` mismatch: "
                f"expected ~{expected['p']}, got {result['p_value']}")

    # p_value must be in [0, 1]
    if not (0 <= result['p_value'] <= 1):
        return f"❌ {prefix}`p_value` must be between 0 and 1, got {result['p_value']}"

    # Verify z-score and p-value are mathematically consistent
    expected_p_from_z = 1 - stats.norm.cdf(result['test_statistic'])
    if not _approx_equal(result['p_value'], expected_p_from_z, tol=0.02):
        return (f"❌ {prefix}`p_value` and `test_statistic` are inconsistent. "
                f"For z={result['test_statistic']}, expected p_value ~{expected_p_from_z:.4f}, "
                f"got {result['p_value']}")

    # Check decision matches p-value vs alpha
    user_decision = result['decision'].strip().lower()

    if "reject" not in user_decision:
        return (f"❌ {prefix}`decision` should be 'Reject H0' or 'Fail to reject H0', "
                f"got '{result['decision']}'")

    if expected['decision'] == "reject h0" and "fail" in user_decision:
        return (f"❌ {prefix}With p_value={result['p_value']} < alpha={alpha}, "
                f"decision should be 'Reject H0', got '{result['decision']}'")
    if expected['decision'] == "fail to reject h0" and "fail" not in user_decision:
        return (f"❌ {prefix}With p_value={result['p_value']} >= alpha={alpha}, "
                f"decision should be 'Fail to reject H0', got '{result['decision']}'")

    # Check hypotheses are descriptive strings
    if not isinstance(result['null_hypothesis'], str) or len(result['null_hypothesis']) < 5:
        return f"❌ {prefix}`null_hypothesis` should be a descriptive string."

    if not isinstance(result['alternative_hypothesis'], str) or len(result['alternative_hypothesis']) < 5:
        return f"❌ {prefix}`alternative_hypothesis` should be a descriptive string."

    # Null hypothesis should reference equality/no difference
    h0_lower = result['null_hypothesis'].strip().lower()
    if not any(kw in h0_lower for kw in ['=', 'equal', 'no diff', 'same', '<=', 'less than or equal']):
        return f"❌ {prefix}`null_hypothesis` should state no difference or equality between conversion rates."

    return None  # No errors


def validate(user_module) -> str:
    """
    Validates the test_website_conversion function.

    Checks:
    1. Function exists and is callable
    2. Output has required structure
    3. Values match expected to appropriate decimal places
    4. Hidden test cases with different data
    """
    try:
        # Check if function exists
        if not hasattr(user_module, "test_website_conversion"):
            return "❌ Function `test_website_conversion` is not defined."

        func = user_module.test_website_conversion

        # Check if it's callable
        if not callable(func):
            return "❌ `test_website_conversion` is not callable."

        # -------------------------------------------------
        # Test Case 1: Original data (Fail to reject H0)
        # -------------------------------------------------
        n1, x1, n2, x2, alpha1 = 5000, 450, 5000, 485, 0.05
        result1 = func(n1, x1, n2, x2, alpha=alpha1)
        expected1 = _compute_expected(n1, x1, n2, x2, alpha1)

        err = _validate_result(result1, expected1, alpha1)
        if err:
            return err

        # -------------------------------------------------
        # Hidden Test Case 2: Clear significance (Reject H0)
        # -------------------------------------------------
        n1_h, x1_h, n2_h, x2_h, alpha2 = 1000, 50, 1000, 100, 0.05
        result2 = func(n1_h, x1_h, n2_h, x2_h, alpha=alpha2)
        expected2 = _compute_expected(n1_h, x1_h, n2_h, x2_h, alpha2)

        err = _validate_result(result2, expected2, alpha2, "Hidden test")
        if err:
            return err

        # -------------------------------------------------
        # Hidden Test Case 3: Different alpha changes decision
        # -------------------------------------------------
        n1_h2, x1_h2, n2_h2, x2_h2 = 2000, 180, 2000, 210
        # With alpha=0.05, this should fail to reject
        # With alpha=0.10, this should reject
        alpha3 = 0.10
        result3 = func(n1_h2, x1_h2, n2_h2, x2_h2, alpha=alpha3)
        expected3 = _compute_expected(n1_h2, x1_h2, n2_h2, x2_h2, alpha3)

        err = _validate_result(result3, expected3, alpha3, "Hidden test")
        if err:
            return err

        return "✅ Correct! All test cases passed successfully."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"

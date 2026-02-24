import math
from itertools import combinations


def _approx_equal(a, b, tol=0.01):
    """Check if two values are approximately equal."""
    return math.isclose(float(a), float(b), abs_tol=tol, rel_tol=0.01)


def _compute_expected(channel_probs, conversion_rates):
    """Compute expected results for given inputs."""
    channels = list(channel_probs.keys())

    # Overall conversion probability (law of total probability)
    p_convert = sum(channel_probs[c] * conversion_rates[c] for c in channels)

    # Bayes' theorem: P(Channel | Converted)
    bayes_results = {}
    for c in channels:
        bayes_results[c] = round((channel_probs[c] * conversion_rates[c]) / p_convert, 2)

    # At least 2 channels (using independence)
    probs = [channel_probs[c] for c in channels]

    # P(at least 2) = sum of exactly-2 combos + all-3
    p_at_least_two = 0.0
    # Exactly 2: for each pair, both in and the third out
    for i, j in combinations(range(len(channels)), 2):
        term = probs[i] * probs[j]
        for k in range(len(channels)):
            if k != i and k != j:
                term *= (1 - probs[k])
        p_at_least_two += term
    # All 3
    p_all = 1.0
    for p in probs:
        p_all *= p
    p_at_least_two += p_all

    return {
        'overall_conversion_prob': round(p_convert, 2),
        'bayes_results': bayes_results,
        'at_least_two_channels_prob': round(p_at_least_two, 2)
    }


def _validate_result(result, expected, channel_names, label=""):
    """Validate a single result against expected values."""
    prefix = f"{label}: " if label else ""

    if not isinstance(result, dict):
        return f"❌ {prefix}Expected dict, got {type(result).__name__}"

    required_keys = ['overall_conversion_prob', 'bayes_results', 'at_least_two_channels_prob']
    for key in required_keys:
        if key not in result:
            return f"❌ {prefix}Missing required key: `{key}`"

    if not isinstance(result['bayes_results'], dict):
        return f"❌ {prefix}`bayes_results` should be a dictionary."

    for key in channel_names:
        if key not in result['bayes_results']:
            return f"❌ {prefix}Missing key in bayes_results: `{key}`"

    if not _approx_equal(result['overall_conversion_prob'], expected['overall_conversion_prob']):
        return (f"❌ {prefix}`overall_conversion_prob` mismatch: "
                f"expected {expected['overall_conversion_prob']}, got {result['overall_conversion_prob']}")

    for key in channel_names:
        if not _approx_equal(result['bayes_results'][key], expected['bayes_results'][key]):
            return (f"❌ {prefix}`bayes_results['{key}']` mismatch: "
                    f"expected {expected['bayes_results'][key]}, got {result['bayes_results'][key]}")

    if not _approx_equal(result['at_least_two_channels_prob'], expected['at_least_two_channels_prob']):
        return (f"❌ {prefix}`at_least_two_channels_prob` mismatch: "
                f"expected {expected['at_least_two_channels_prob']}, got {result['at_least_two_channels_prob']}")

    # Consistency: Bayes results must sum to ~1.0
    bayes_sum = sum(result['bayes_results'][k] for k in channel_names)
    if not _approx_equal(bayes_sum, 1.0, tol=0.05):
        return f"❌ {prefix}Bayes posterior probabilities should sum to ~1.0, got {bayes_sum:.4f}"

    # All probabilities must be in [0, 1]
    if not (0 <= result['overall_conversion_prob'] <= 1):
        return f"❌ {prefix}`overall_conversion_prob` must be between 0 and 1"

    if not (0 <= result['at_least_two_channels_prob'] <= 1):
        return f"❌ {prefix}`at_least_two_channels_prob` must be between 0 and 1"

    for k in channel_names:
        if not (0 <= result['bayes_results'][k] <= 1):
            return f"❌ {prefix}`bayes_results['{k}']` must be between 0 and 1"

    return None  # No errors


def validate(user_module) -> str:
    """
    Validates the calculate_marketing_probabilities function.

    Checks:
    1. Function exists and is callable
    2. Output has required structure
    3. Values match expected to 2 decimal places
    4. Hidden test case with different probabilities
    """
    try:
        # Check if function exists
        if not hasattr(user_module, "calculate_marketing_probabilities"):
            return "❌ Function `calculate_marketing_probabilities` is not defined."

        func = user_module.calculate_marketing_probabilities

        # Check if it's callable
        if not callable(func):
            return "❌ `calculate_marketing_probabilities` is not callable."

        # -------------------------------------------------
        # Test Case 1: Original data from question
        # -------------------------------------------------
        channel_probs_1 = {'Email': 0.40, 'Social': 0.35, 'Website': 0.25}
        conversion_rates_1 = {'Email': 0.12, 'Social': 0.08, 'Website': 0.15}

        result1 = func(channel_probs_1, conversion_rates_1)
        expected1 = _compute_expected(channel_probs_1, conversion_rates_1)

        err = _validate_result(result1, expected1, ['Email', 'Social', 'Website'])
        if err:
            return err

        # -------------------------------------------------
        # Hidden Test Case 2: Different probabilities
        # -------------------------------------------------
        channel_probs_2 = {'Email': 0.50, 'Social': 0.30, 'Website': 0.20}
        conversion_rates_2 = {'Email': 0.10, 'Social': 0.15, 'Website': 0.05}

        result2 = func(channel_probs_2, conversion_rates_2)
        expected2 = _compute_expected(channel_probs_2, conversion_rates_2)

        err = _validate_result(result2, expected2, ['Email', 'Social', 'Website'], "Hidden test")
        if err:
            return err

        # -------------------------------------------------
        # Hidden Test Case 3: Extreme skew (one dominant channel)
        # -------------------------------------------------
        channel_probs_3 = {'Email': 0.80, 'Social': 0.10, 'Website': 0.10}
        conversion_rates_3 = {'Email': 0.05, 'Social': 0.20, 'Website': 0.30}

        result3 = func(channel_probs_3, conversion_rates_3)
        expected3 = _compute_expected(channel_probs_3, conversion_rates_3)

        err = _validate_result(result3, expected3, ['Email', 'Social', 'Website'], "Hidden test")
        if err:
            return err

        return "✅ Correct! All test cases passed successfully."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"

description = """
An e-commerce company tested a new website design. Data collected:

**Control Group (Old Design):**
- 5,000 visitors
- 450 conversions (9.0% conversion rate)

**Treatment Group (New Design):**
- 5,000 visitors  
- 485 conversions (9.7% conversion rate)

### Task
Test if the new website design **significantly improves** the conversion rate.

Implement a function:
```python
test_website_conversion(n_control, x_control, n_treatment, x_treatment, alpha=0.05) -> dict
```

### Requirements

1. **State Hypotheses Clearly:**
   - Null hypothesis (H0)
   - Alternative hypothesis (H1)

2. **Choose Significance Level:**
   - Select an appropriate a value (e.g., 0.05)
   - Justify your choice

3. **Calculate Test Statistic:**
   - Use a two-proportion z-test
   - Formula: z = (p_new - p_old) / sqrt(p_pooled * (1 - p_pooled) * (1/n_old + 1/n_new))
   - where p_pooled = (x_old + x_new) / (n_old + n_new)

4. **Calculate P-Value and Make Decision:**
   - Since we're testing if new design is BETTER (one-tailed test)
   - Compare p-value to significance level

### Return
A dictionary with the following structure:
```python
{
    'null_hypothesis': str,       # e.g., "p_new <= p_old"
    'alternative_hypothesis': str, # e.g., "p_new > p_old"
    'significance_level': float,   # e.g., 0.05
    'test_statistic': float,       # z-score, rounded to 2 decimals
    'p_value': float,              # rounded to 4 decimals
    'decision': str                # "Reject H0" or "Fail to reject H0"
}
```
"""

hint = """- One-tailed upper test: p-value = `1 - scipy.stats.norm.cdf(z)`"""

initial_sample_code = """from scipy import stats
import math

def test_website_conversion(n_control, x_control, n_treatment, x_treatment, alpha=0.05):
    '''
    Perform a two-proportion z-test for website conversion improvement.

    Parameters:
        n_control: int - number of visitors in control group
        x_control: int - number of conversions in control group
        n_treatment: int - number of visitors in treatment group
        x_treatment: int - number of conversions in treatment group
        alpha: float - significance level (default 0.05)

    Returns:
        dict with keys:
            - null_hypothesis: str describing H0
            - alternative_hypothesis: str describing H1
            - significance_level: float (alpha value)
            - test_statistic: float (z-score)
            - p_value: float
            - decision: str ("Reject H0" or "Fail to reject H0")
    '''
    # Your code here
    pass

# ==========================================================
# Uncomment below to see the output
# ==========================================================
# if __name__ == "__main__":
#     result = test_website_conversion(5000, 450, 5000, 485, alpha=0.05)
#     print(result)"""

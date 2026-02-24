description = """### Task
Analyze a customer churn dataset and return a compact metrics summary.

You are given a pandas DataFrame `df` with at least these columns:
- `customer_id`
- `churn` (0 = retained, 1 = churned)

### Function Signature
```python
def analyze_churn(df):
```

### Requirements
Return a pandas DataFrame with **exactly** these columns (in order):
- `metric`
- `value`

The output must contain exactly these metrics (one row each):
- `n_customers`
- `n_churned`
- `n_retained`
- `churn_rate_pct`

### Rules
- `n_customers` = total number of rows
- `n_churned` = count of rows where `churn == 1`
- `n_retained` = count of rows where `churn == 0`
- `churn_rate_pct` = `(n_churned / n_customers) * 100`, rounded to 2 decimals

### Return
Return the metrics DataFrame.

"""

hint = """Use `df["churn"].sum()` and build a `metric` / `value` DataFrame."""

initial_sample_code = """import pandas as pd

def analyze_churn(df):
    # Return a DataFrame with columns: metric, value
    # Required metrics: n_customers, n_churned, n_retained, churn_rate_pct
    pass
"""

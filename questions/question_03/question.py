description = """
Finance requires a compact but complete statistical snapshot of customer spending behavior.

### Task
Given a pandas Series named `monthly_spend`, implement a function:
```python
summarize_spend(series) -> dict
```

### Requirements
You must compute the following statistics and return them in a dictionary:
- `mean` - arithmetic mean
- `median` - median value
- `mode` - most frequent value (if multiple modes, return the smallest)
- `std` - standard deviation
- `variance` - variance
- `min` - minimum value
- `max` - maximum value
- `Q1` - first quartile (25th percentile)
- `Q3` - third quartile (75th percentile)
- `IQR` - interquartile range (Q3 - Q1)

**Important**: Ignore missing values (NaN) when computing statistics.

**Input Format**: A pandas Series like `pd.Series([1200, 1500, 1800, 2000, ...])`

**Sample Output**:
```python
{'mean': 1725.0, 'median': 1750.0, 'mode': 1500, 'std': 319.37, 
 'variance': 101999.99, 'min': 1200, 'max': 2200, 'Q1': 1550.0, 'Q3': 1925.0, 'IQR': 375.0}
```

### Return
- A dictionary with all 10 required keys and their computed values
"""

hint = """
- Quartiles: `.quantile(0.25)` and `.quantile(0.75)`
- Mode returns a Series; use `.iloc[0]` for single value
"""


inital_sample_code = """import pandas as pd

def summarize_spend(series):
    \"\"\"
    Compute comprehensive statistics for spending data.

    Parameters:
        series: pandas Series containing monthly spend values

    Returns:
        dict with keys: mean, median, mode, std, variance, min, max, Q1, Q3, IQR
    \"\"\"
    # Your code here
    pass
"""


def get_description():
    return description

def get_hint():
    return hint

def get_inital_sample_code():
    return inital_sample_code
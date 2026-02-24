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

hint = """- Use `series.dropna()` before computing metrics
- Use `quantile(0.25)` and `quantile(0.75)` for quartiles
- `mode()` may return multiple values; return a single mode value as required"""

initial_sample_code = """import pandas as pd
import numpy as np

def summarize_spend(spend_series):
    '''
    Return summary statistics for a pandas Series.

    Parameters:
        spend_series: pandas Series (may include NaN values)

    Returns:
        dict with keys: mean, median, mode, std, variance, min, max, Q1, Q3, IQR
    '''
    # Your code here
    pass
"""

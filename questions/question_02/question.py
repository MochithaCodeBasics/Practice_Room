description = """
A payments team at a fintech company monitors daily transaction volume to detect 
abnormal spikes that may be caused by fraud, system outages, or marketing campaigns. 
Early detection helps the operations team respond quickly.

### Dataset
You are given a pandas DataFrame with the following columns:
- `date` (string, format `YYYY-MM-DD`)
- `transaction_count` (integer)

### Task
Implement a function:
```python
plot_transactions_with_rolling_mean(df, window) -> matplotlib.figure.Figure
```

### Requirements
- Convert `date` column to datetime format
- Plot the raw `transaction_count` values as a line
- Calculate and plot the rolling mean using the specified `window` size
- Calculate the rolling standard deviation
- Highlight (scatter plot) points where the deviation from rolling mean exceeds 3× the rolling standard deviation
- Return the matplotlib Figure object

### Return
- A matplotlib Figure object containing:
  - Line plot of raw transaction counts
  - Line plot of rolling mean
  - Scatter plot highlighting anomaly points
"""

hint = """
- Rolling: `df['col'].rolling(window).mean()` and `.std()`
- Anomaly: `abs(value - rolling_mean) > 3 * rolling_std`
"""


initial_sample_code = """import pandas as pd
import matplotlib.pyplot as plt

def plot_transactions_with_rolling_mean(df, window):
    \"\"\"
    Plot transaction counts with rolling mean and highlight anomalies.

    Parameters:
        df: pandas DataFrame with 'date' and 'transaction_count' columns
        window: integer for rolling window size

    Returns:
        matplotlib.figure.Figure object with line plots and anomaly markers
    \"\"\"
    # Your code here
    pass

# ==========================================================
# Uncomment below to see the output
# ==========================================================
#if __name__ == "__main__":
#    result = plot_transactions_with_rolling_mean(data, window=5)

"""


def get_description():
    return description

def get_hint():
    return hint

def get_initial_sample_code():
    return initial_sample_code


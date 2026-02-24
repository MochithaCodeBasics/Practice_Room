description = """### Task
A retail company wants to understand its monthly revenue trends to track business performance over time.

You are provided with a pandas DataFrame named `data` containing order transactions.

**Columns**:
- `order_id` (string)
- `order_date` (string, format `YYYY-MM-DD`)
- `amount` (number)

Your task is to compute monthly revenue metrics and visualize the trend.

### Requirements
- Convert `order_date` to datetime
- Group the data by month (`YYYY-MM`)
- Compute:
  - `revenue` - total revenue per month
  - `mom_growth_pct` - month-over-month revenue growth percentage
- Round numeric values to **2 decimals**
- **Create a line chart** showing the monthly revenue trend
- Months should be sorted in ascending order

### Return
- A DataFrame named `monthly_revenue` with columns: `month`, `revenue`, `mom_growth_pct`
- A plot object named `plot` (matplotlib Axes) used to create the chart
- Assign the figure to `result` to display the graph

### Example

If data contains orders from Jan-Mar 2024:
- Jan total: 10000
- Feb total: 12000 (20% growth)
- Mar total: 15000 (25% growth)

Output DataFrame:
| month   | revenue | mom_growth_pct |
|---------|---------|----------------|
| 2024-01 | 10000.0 | NaN            |
| 2024-02 | 12000.0 | 20.0           |
| 2024-03 | 15000.0 | 25.0           |

### Expected Outputs (script-style)
- `monthly_revenue`: pandas DataFrame with columns `month`, `revenue`, `mom_growth_pct`
- `plot`: matplotlib Axes containing the line chart
- `result`: matplotlib Figure object (for display)

### Return
The function should return the result as specified in the task.

"""

hint = """- Use `.pct_change()` for growth calculation.
- The first month will have NaN for mom_growth_pct."""

initial_sample_code = """import pandas as pd
import matplotlib.pyplot as plt

# Data is available in the `data` DataFrame
df = data.copy()

monthly_revenue = None  # DataFrame with: month, revenue, mom_growth_pct

# Create plot (plot must be a matplotlib Axes)
fig, plot = plt.subplots()

plot.set_xlabel("month")
plot.set_ylabel("revenue")
plot.set_title("Monthly Revenue Trend")
plt.tight_layout()

# Assign fig to result to display the graph
result = fig"""

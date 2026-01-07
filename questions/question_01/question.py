description = """
A retail bank wants to quickly understand relationships between customer age, income, 
credit score, and monthly spend before building risk models.

You are given a pandas DataFrame containing numeric columns:
`age`, `annual_income`, `credit_score`, `monthly_spend`, and a categorical column `city_tier`.

### Task
Implement a function:
```python
create_pairplot(df, cols, hue=None) -> matplotlib.figure.Figure
```

### Requirements
- Drop rows with missing values in `cols` or `hue` (if provided)
- Use seaborn's `pairplot` function
- Plot only the specified columns in `cols`
- Return the matplotlib Figure object

### Return
- A matplotlib Figure object from the seaborn pairplot
"""

hint = """
- `sns.pairplot()` returns a PairGrid; access the figure via `.fig` attribute
"""


inital_sample_code = """import seaborn as sns
import matplotlib.pyplot as plt

def create_pairplot(df, cols, hue=None):
    \"\"\"
    Create a pairplot visualization for the specified columns.

    Parameters:
        df: pandas DataFrame with customer data
        cols: list of column names to include in pairplot
        hue: optional categorical column for color coding

    Returns:
        matplotlib.figure.Figure object
    \"\"\"
    # Your code here
    pass

# Call the function and store in result
result = create_pairplot(data, ['age', 'annual_income', 'credit_score', 'monthly_spend'], hue='city_tier')
"""


def get_description():
    return description

def get_hint():
    return hint

def get_inital_sample_code():
    return inital_sample_code

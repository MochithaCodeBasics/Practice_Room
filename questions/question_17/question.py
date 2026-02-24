description = """### Task
A retail business tracks sales across different **regions** and **sales channels**.

You are provided with a CSV file named `data.csv` containing both numerical and categorical features.

### **Columns:**
- `region` - Geographic region (categorical)
- `channel` - Sales channel (categorical)
- `ad_spend` - Advertising expenditure (numeric)
- `discount` - Discount percentage (numeric)
- `sales` - Sales revenue (target variable)

Your task is to build a **Multiple Linear Regression** model to predict sales using both categorical and numerical features. 

### Requirements

- Use `train_test_split(test_size=0.2, random_state=42)`
- One-hot encode categorical features (any correct method is allowed)
- Train a Linear Regression model and compute **MSE** and **R²**
- Return a DataFrame with `metric`, `value` containing:
  - `mse`
  - `r2`
  - `n_features` (final number of features after encoding)

### Example Output

| metric     | value  |
|------------|--------|
| mse        | 2500.0 |
| r2         | 0.85   |
| n_features | 10     |

- **Note:** The **Mean Squared Error (MSE)** may appear very large due to the high magnitude of sales values, but this does **not necessarily indicate poor model performance**.

### Function Signature
```python
def main():
```

### Return
The function should return the result as specified in the task.

"""

hint = """- Use `OneHotEncoder` for categorical columns
- Wrap everything in a `Pipeline` to ensure consistent preprocessing on train and test data"""

initial_sample_code = """# Import necessary libraries


def main():
    '''
    Train and evaluate the machine learning model.

    Returns
    -------
    model : object
        The trained model.
    result : pandas.DataFrame
        Evaluation results.
    '''
    # data available in this dataframe
    df = data.copy()

    # Code Here

    # Return trained model and results DataFrame
    return model, result

if __name__ == "__main__":
    model, result = main()
    print(result)"""

description = """### Task
A marketing team wants to estimate **sales revenue** based on **advertising spend**.

You are provided with a CSV file named `data.csv` containing historical campaign data.

### **Columns:**
- `ad_spend` - Amount spent on advertising
- `sales` - Sales revenue (target variable)

Your task is to train a **Simple Linear Regression** model to predict `sales` from `ad_spend`
and report evaluation metrics.

### Requirements

- Use `train_test_split(test_size=0.2, random_state=42)`
- Train a Linear Regression model using `ad_spend` as the only feature
- Compute **MSE** and **R²** on the test set
- Return a DataFrame with columns: `metric`, `value` containing rows: `mse`, `r2`

### Example Output

| metric | value  |
|--------|--------|
| mse    | 125.5  |
| r2     | 0.89   |

- The **Mean Squared Error (MSE)** may appear very large due to the high magnitude of sales values, but this does **not necessarily indicate poor model performance**.

### Function Signature
```python
def main():
```

### Return
The function should return the result as specified in the task.

"""

hint = """- Use `LinearRegression` from sklearn.linear_model
- Keep features as 2D array using double brackets `df[['ad_spend']]`
- Calculate metrics using `mean_squared_error` and `r2_score` from sklearn.metrics
- No feature scaling is needed for simple linear regression with a single feature"""

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

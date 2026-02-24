description = """### Task
An e-commerce company wants to predict whether a customer will make a **repeat purchase**
based on transaction behavior.

You are provided with a CSV file named `data.csv` containing customer transaction history.

### **Columns:**
- `recency_days` - Days since last purchase
- `txn_count` - Number of transactions
- `avg_basket_value` - Average order value
- `total_spend` - Total spending so far
- `returns_count` - Number of returns
- `repeat_purchase` - (0=No, 1=Yes) - target variable

Your task is to train a **Random Forest classifier** to predict repeat purchases.

### Requirements

- Use `train_test_split(test_size=0.2, random_state=42, stratify=y)`
- Train a **Random Forest classifier**
- Compute `accuracy` and `f1` (F1 score for the positive class, label=1)
- Return a DataFrame with `metric`, `value` containing: `accuracy`, `f1`

### Example Output

| metric   | value |
|----------|-------|
| accuracy | 0.85  |
| f1       | 0.82  |


### Function Signature
```python
def main():
```

### Return
The function should return the result as specified in the task.

"""

hint = """- Use `RandomForestClassifier(random_state=42)` from sklearn.ensemble
- Random Forest works well without feature scaling
- For F1, use `f1_score(y_true, y_pred, pos_label=1)` to get the score for repeat purchasers"""

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

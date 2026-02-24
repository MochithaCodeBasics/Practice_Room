description = """### Task
A fintech company wants to categorize customers into **risk levels**: `Low`, `Medium`, `High`.

You are provided with a CSV file named `data.csv` containing customer profile data.

### **Columns:**
- `age` - Customer age
- `income` - Annual income
- `txn_count` - Number of transactions
- `avg_txn_value` - Average transaction value
- `risk_level` - Risk category (target variable)

Your task is to build a **multi-class classification model** to predict customer risk levels.

### Requirements

- Use `train_test_split(test_size=0.2, random_state=42, stratify=y)`
- Train a multi-class classification model
- Compute `accuracy` and `macro_f1` on the test set
- Return a DataFrame with `metric`, `value` containing: `accuracy`, `macro_f1`

### Example Output

| metric   | value |
|----------|-------|
| accuracy | 0.82  |
| macro_f1 | 0.78  |

### Function Signature
```python
def main():
```

### Return
The function should return the result as specified in the task.

"""

hint = """- Use `stratify=y` in train_test_split to maintain class distribution in both sets
- For macro F1, use `f1_score(y_true, y_pred, average='macro')` which treats all classes equally"""

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

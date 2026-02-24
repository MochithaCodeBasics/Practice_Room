description = """### Task
A payments company wants to detect **fraudulent transactions**, where fraud cases are rare.

You are provided with a CSV file named `data.csv` containing transaction features.

### **Columns:**
- `amount` - Transaction amount
- `hour` - Hour of the day
- `transaction_count_24h` - Number of transactions in last 24 hours
- `avg_amount_30d` - Average transaction amount in last 30 days
- `account_age_days` - Age of account in days
- `failed_attempts_24h` - Failed login attempts in last 24 hours
- `is_fraud` - (0=Normal, 1=Fraud) - target variable

Your task is to build a **boosting-based classification model** that can effectively
identify fraudulent transactions.

### Requirements

- Use `train_test_split(test_size=0.2, random_state=42, stratify=y)`
- Train a boosting-based classifier
- Compute `roc_auc` and `f1` on the test set
- Return a DataFrame with `metric`, `value` containing: `roc_auc`, `f1`

### Example Output

| metric  | value |
|---------|-------|
| roc_auc | 0.94  |
| f1      | 0.68  |


### Function Signature
```python
def main():
```

### Return
The function should return the result as specified in the task.

"""

hint = """- Use `XGBClassifier(random_state=42, eval_metric='logloss')`
- Tune hyperparameters like `n_estimators`, `max_depth`, `learning_rate` for better results
- Use parameters like `scale_pos_weight` to handle class imbalance ( May or may not improve results)
- For computing ROC-AUC use probabilities and for F1 use labels"""

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

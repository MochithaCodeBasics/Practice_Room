description = """### Task
A manufacturing dataset contains very few **defective products**, making the target variable
highly imbalanced.

You are provided with a CSV file named `data.csv` containing sensor measurements.

### **Columns:**
- `temperature` - Temperature reading from sensor
- `pressure` - Pressure measurement
- `vibration` - Vibration level
- `humidity` - Humidity percentage
- `speed` - Operating speed
- `quality` - Product quality (0=OK, 1=Defective) - target variable

Your task is to build a **classification model** that correctly handles class imbalance
and predicts whether a product is defective.

### Requirements

- Use `train_test_split(test_size=0.2, random_state=42, stratify=y)`
- Apply an appropriate technique to handle class imbalance **on the training data only**
- Train an **SVM-based classifier**
- Return a DataFrame with `metric`, `value` containing:
  - `f1` - F1 score for the minority class (label=1)
  - `minority_ratio_after` - ratio of minority to majority class **after resampling** in training data

### Example Output

| metric               | value |
|----------------------|-------|
| f1                   | 0.72  |
| minority_ratio_after | 1.0   |


### Function Signature
```python
def main():
```

### Return
The function should return the result as specified in the task.

"""

hint = """- Use `SMOTE(random_state=42)` from imblearn to balance classes on training data only
- Calculate F1 for minority class using `f1_score(y_true, y_pred, pos_label=1)`
- Track minority_ratio after SMOTE
- Apply Scaling before SVM training for better performance
- Apply scaling after balancing the classes and splitting the data to prevent data leakage"""

initial_sample_code = """# Import necessary libraries


def main():
    '''
    Train and evaluate the machine learning model.

    Returns
    -------
    scaler : object or None
        The fitted scaler if preprocessing is applied, otherwise None.
    model : object
        The trained model.
    result : pandas.DataFrame
        Evaluation results.
    '''
    # data available in this dataframe
    df = data.copy()

    # Code Here

    # Return scaler (or None), trained model, and results DataFrame
    return scaler, model, result

if __name__ == "__main__":
    scaler, model, result = main()
    print(result)"""

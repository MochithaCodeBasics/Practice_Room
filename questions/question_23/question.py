description = """### Task
A healthcare company wants to predict whether a patient has a certain disease based on medical test results.

You are provided with a CSV file named `data.csv` containing patient medical data.

### **Columns:**
- `age` - Patient age (years)
- `blood_pressure` - Systolic blood pressure (mmHg)
- `cholesterol` - Cholesterol level (mg/dL)
- `glucose` - Blood glucose level (mg/dL)
- `bmi` - Body Mass Index
- `heart_rate` - Heart rate (bpm)
- `disease` - Disease indicator (0 = No, 1 = Yes) - **target variable**

Your task is to build a **fully connected neural network** using PyTorch to classify patients.

### Requirements

- Use `train_test_split(test_size=0.2, random_state=42, stratify=y)` to split the data
- Define the model using `torch.nn.Module` or `nn.Sequential`
- Implement a training loop with forward pass, loss computation, and backpropagation
- Train the model for a reasonable number of epochs
- Evaluate on the test set and compute:
  - `accuracy` - Classification accuracy
  - `f1` - F1 score for positive class (disease = 1)
- Return a pandas DataFrame with columns: `metric`, `value`

### Example Output

| metric   | value  |
|----------|--------|
| accuracy | 0.7583 |
| f1       | 0.7123 |

### Function Signature
```python
def main():
```

### Return
The function should return the result as specified in the task.

"""

hint = """- Use `stratify=y` in train_test_split for balanced class distribution
- If using `nn.Module`, then define layers in `__init__()` and implement `forward()` method
- Use `BCEWithLogitsLoss` for binary classification
- Set learning rate and number of epochs appropriately
- Zero gradients before each forward pass"""

initial_sample_code = """# Import necessary libraries

def main():
    '''
    Build and train a neural network using PyTorch.

    Returns
    -------
    result : pandas.DataFrame
        DataFrame with columns 'metric' and 'value' containing:
        - accuracy: test set accuracy
        - f1: F1 score for positive class
    '''
    # Data available in this dataframe
    df = data.copy()
    
    # Load, Split Data

    
    # Define Model, Loss, Optimizer

    
    # Training Loop

    
    # Evaluate on Test Set

    
    return result

if __name__ == "__main__":
    result = main() # Save return value into a variable named `result`
    print(result)"""

description = """### Task
A telecom company wants to predict **customer churn** to improve retention strategies. 
The dataset contains both numerical and categorical features.

You are provided with a CSV file named `data.csv` containing customer data.

### **Columns:**
- `tenure` - Number of months the customer has stayed
- `monthly_charges` - Monthly subscription amount
- `total_charges` - Total amount charged
- `contract_type` - Type of contract (Month-to-Month, One Year, Two Year)
- `payment_method` - Payment method used
- `internet_service` - Type of internet service
- `churn` - Whether the customer churned (target variable)

Your task is to build a **PyTorch neural network** with **dropout regularization** to prevent overfitting.

### Requirements

- Use `train_test_split(test_size=0.2, random_state=42, stratify=y)` to split the data
- **Encode categorical features** using any method (One-Hot, Label Encoding, etc.)
- Build a neural network using `torch.nn.Module` **with dropout layers**
- Use **BCELoss** or **BCEWithLogitsLoss**
- Track both training and test accuracy to monitor overfitting
- Compute:
  - `train_accuracy` - Accuracy on training set
  - `test_accuracy` - Accuracy on test set
- Return a pandas DataFrame with columns: `metric`, `value`

### Example Output

| metric           | value |
|------------------|-------|
| train_accuracy   | 0.79  |
| test_accuracy    | 0.76  |

**Note:** Dropout helps reduce overfitting. A smaller gap between train and test accuracy indicates better generalization.

### Function Signature
```python
def main():
```

### Return
The function should return the result as specified in the task.

"""

hint = """- Use `pd.get_dummies()` or `LabelEncoder` for categorical features (any method acceptable)
- Add dropout layers in model: `nn.Dropout(p=0.3)` between fully connected layers
- Set `model.eval()` before test evaluation to disable dropout
- Use `stratify=y` to maintain class balance in splits"""

initial_sample_code = """# Import necessary libraries

def main():
    '''
    Build and train a neural network with dropout regularization.

    Returns
    -------
    result : pandas.DataFrame
        DataFrame with columns 'metric' and 'value' containing:
        - train_accuracy: Accuracy on training set
        - test_accuracy: Accuracy on test set  
    '''
    # Data available in this dataframe
    df = data.copy()
    
    # Load and Split Data

    
    # Encode Categorical Features

    
    # Define Model with Dropout, Loss, Optimizer

    
    # Training Loop

    
    # Evaluate on Train and Test Sets


    
    return result

if __name__ == "__main__":
    result = main() # Save return value into a variable named `result`
    print(result)"""

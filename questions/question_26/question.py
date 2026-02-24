description = """### Task
A retail company wants to segment customers into **4 tiers** (Bronze, Silver, Gold, Platinum) 
based on their behavior. Finding the right hyperparameters is crucial for model performance.

You are provided with a CSV file named `data.csv` containing customer data.

### Columns:
- `age` - Customer age
- `annual_spend` - Total annual spending
- `visit_frequency` - Number of visits per year
- `avg_transaction` - Average transaction value
- `segment` - Customer tier (0=Bronze, 1=Silver, 2=Gold, 3=Platinum) - target variable

Your task is to build a **PyTorch multi-class classifier** and perform **manual hyperparameter tuning**
to find the best combination of learning rate and hidden layer size.

### Requirements

- Use `train_test_split(test_size=0.2, random_state=42, stratify=y)` to split the data
- Build a PyTorch neural network for **4-class classification**
- Test multiple combinations of:
  - `learning_rate`: Try at least 2 like [0.001, 0.01, 0.1]
  - `hidden_size`: Try at least  2 like [32, 64, 128]
  - Total combinations tested should be at least 6
- For each combination, train the model and evaluate on test set
- Track: `learning_rate`, `hidden_size`, `accuracy`, `macro_f1`, `is_best` (1 if best combo, 0 otherwise)
- Return a pandas DataFrame with these columns for ALL tested combinations

### Example Output

| learning_rate | hidden_size | accuracy | macro_f1 | is_best |
|---------------|-------------|----------|----------|---------|
| 0.001         | 32          | 0.72     | 0.70     | 0       |
| 0.001         | 64          | 0.74     | 0.72     | 0       |
| 0.001         | 128         | 0.76     | 0.74     | 1       |
| 0.01          | 32          | 0.73     | 0.71     | 0       |
| ...           | ...         | ...      | ...      | ...     |

**Note:** Each row represents one hyperparameter combination tested. 
Mark is_best=1 for the combination with highest macro_f1.

### Function Signature
```python
def main():
```

### Return
The function should return the result as specified in the task.

"""

hint = """- Use CrossEntropyLoss for multi-class classification  
- Use `stratify=y` to maintain class balance in train/test split
- Calculate macro F1 using `f1_score(y_true, y_pred, average='macro')`
- Loop through hyperparameter combinations and store results
- Keep number of epochs consistent across all experiments (e.g., 100 epochs)"""

initial_sample_code = """# Import necessary libraries

def main():
    '''
    Train models with different hyperparameters and find the best combination.

    Returns
    -------
    result : pandas.DataFrame
        DataFrame with columns:
        - learning_rate: Learning rate tested
        - hidden_size: Hidden layer size tested
        - accuracy: Test accuracy achieved
        - macro_f1: Test macro F1 score achieved
        - is_best: 1 if this is the best combination (highest macro_f1), 0 otherwise
    '''
    # Data available in this dataframe
    df = data.copy()
    
    # Load and Split Data

    
    # Define hyperparameter grid
    

    # Define Model, Loss, Optimizer for each hyperparameters in loop
            
            
    # Train and Evaluate for each combination

    
    # Mark best combination
    best_idx = result['macro_f1'].idxmax()
    result.loc[best_idx, 'is_best'] = 1
    
    return result

if __name__ == "__main__":
    # Save return value into a variable named `result`
    result = main()
    print(result)"""

description = """### Task
A real estate company wants to predict **house prices** based on various property features. 
Since features have different scales (e.g., area in sq ft vs number of bedrooms), 
normalization is essential for neural network training.

You are provided with a CSV file named `data.csv` containing property data.

### **Columns:**
- `area` - Property area in square feet
- `bedrooms` - Number of bedrooms
- `bathrooms` - Number of bathrooms
- `age` - Age of the property in years
- `distance_to_city` - Distance to city center in km
- `garage_size` - Number of car spaces in garage
- `price` - Property price (target variable)

Your task is to build a **neural network regression model** using PyTorch with proper feature normalization.

### Requirements

- Use `train_test_split(test_size=0.2, random_state=42)` to split the data
- **Normalize/Standardize** the features before training (e.g., using StandardScaler)
- Build a fully connected neural network using `torch.nn.Module` or `nn.Sequential`
- Use appropriate loss function for regression (e.g., MSELoss)
- Train the model and evaluate on test set
- Compute:
  - `mse` - Mean Squared Error
  - `r2` - R-squared score
- Return a pandas DataFrame with columns: `metric`, `value`

### Example Output

| metric | value        |
|--------|-------------|
| mse    | 2500000000.0 |
| r2     | 0.6543       |

**Note:** MSE values will be large due to house prices being in hundreds of thousands. 
Focus on R² score as the primary performance metric.

### Function Signature
```python
def main():
```

### Return
The function should return the result as specified in the task.

"""

hint = """- Normalize features for better result (fit on train, transform on train and test)
- Use MSELoss for regression tasks
- Use `torch.optim.Adam` or `SGD` for optimization
- Set learning rate and number of epochs appropriately
- Evaluate R² using `sklearn.metrics.r2_score(y_true, y_pred)`"""

initial_sample_code = """# Import necessary libraries

def main():
    '''
    Build and train a neural network for regression.

    Returns
    -------
    result : pandas.DataFrame
        DataFrame with columns 'metric' and 'value' containing:
        - mse: Mean Squared Error
        - r2: R-squared score
    '''
    # Data available in this dataframe
    df = data.copy()
    
    # Load, Split Data

    
    # Normalize Features

    
    # Define Model, Loss, Optimizer

    
    # Training Loop

    
    # Evaluate on Test Set


    return result

if __name__ == "__main__":
    result = main() # Save return value into a variable named `result`
    print(result)"""

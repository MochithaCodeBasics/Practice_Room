"""
Question 1: Build and train a neural network from scratch using NumPy
Customer Purchase Prediction
"""

description = """
A small e-commerce startup wants to understand neural networks before using frameworks. 
They need to predict if a customer will make a purchase based on simple website behavior.

You are provided with a CSV file named `data.csv` containing customer data.

### **Columns:**
- `time_on_site` - Minutes spent browsing
- `pages_viewed` - Number of pages visited
- `purchased` - Made purchase (0 = No, 1 = Yes)

Your task is to build a **simple neural network from scratch** using only NumPy.

### Requirements

- Use `train_test_split(test_size=0.2, random_state=42)` to split the data
- Implement a neural network with **at least 1 hidden layer** using only NumPy
- Implement **forward propagation** and **backpropagation**
- Calculate loss
- Train for multiple epochs and track the loss
- Compute final metrics on test set:
  - `accuracy` - Classification accuracy on test set
  - `final_loss` - Loss value after final epoch on training data
- Return a pandas DataFrame with columns: `metric`, `value`

### Example Output

| metric      | value  |
|-------------|--------|
| accuracy    | 0.78   |
| final_loss  | 0.42   |

"""

hint = """
- Normalize input features for better training
- Ensure weight shapes match for matrix multiplication
- Use log loss
- Add small epsilon (1e-8) in log to avoid log(0)
- If loss is NaN, reduce learning rate
"""

initial_sample_code = """# Import necessary libraries

def main():
    \"\"\"
    Build and train a neural network from scratch using NumPy.

    Returns
    -------
    result : pandas.DataFrame
        DataFrame with columns 'metric' and 'value' containing:
        - accuracy: test set accuracy
        - final_loss: final training loss
    \"\"\"
    # Data available in this dataframe
    df = data.copy()
    
    # Load, Split Data 

    
    # Normalize features (optional but recommended)

    
    # Initialize neural network, Train, Evaluate

    
    return result

if __name__ == "__main__":
    result = main() # Save return value into a variable named `result`
    print(result)
"""

def get_description():
    return description

def get_hint():
    return hint

def get_initial_sample_code():
    return initial_sample_code

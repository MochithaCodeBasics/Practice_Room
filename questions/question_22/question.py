description = """### Task
A retail company wants to segment customers based on **transaction behavior** to enable
targeted marketing strategies.

You are provided with a CSV file named `data.csv` containing customer transaction summary.

### **Columns:**
- `customer_id` - Unique customer identifier (should NOT be used as a feature)
- `total_spend` - Total amount spent by the customer
- `txn_count` - Number of transactions
- `recency_days` - Days since last transaction

Your task is to group customers into **k=3 clusters** using K-Means.

### Requirements

- Use features: `total_spend`, `txn_count`, `recency_days`
- Scale features using `StandardScaler()`
- Fit `KMeans(n_clusters=3, random_state=42)`
- Compute the **silhouette score**
- Return a DataFrame with `metric`, `value` containing: `silhouette_score`

### Example Output

| metric           | value |
|------------------|-------|
| silhouette_score | 0.45  |

### Function Signature
```python
def main():
```

### Return
The function should return the result as specified in the task.

"""

hint = """- Drop `customer_id` as it is not a feature
- Use Scaler before K-Means - distance-based algorithms need scaled features
- Silhouette score: `silhouette_score(X, labels)` measures how well points fit their clusters (-1 to 1)"""

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

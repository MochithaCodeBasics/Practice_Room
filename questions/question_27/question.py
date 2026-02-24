description = """
A customer support team receives messages that include key details like Order ID, 
Email, Phone Number, and Refund Amount. Your task is to extract these fields from 
each message using regular expressions.

### Dataset
You are provided with a pandas DataFrame named `data` containing:
- `message` (string)

### Task
Extract the following fields from each message:
- `order_id` (format like ORD-45892)
- `email`
- `phone`
- `amount` (format like ₹1,250.50, ₹500, ₹75, etc.)

### Requirements
- Use regex to extract the first match of each field from every message
- If a field is missing, return an empty string ""
- Implement `extract_order_details(message)` and use it to build the final output
- Return a DataFrame named `result` with columns:
  - `order_id`
  - `email`
  - `phone`
  - `amount`

### Evaluation
- Output format validation (required columns)
- Exact match with expected extracted values (after minor normalization like trimming spaces)

### Function Signature
```python
def extract_order_details(message):
```
"""

hint = """
- Use `re.search(pattern, text).group()` to extract first match
"""

initial_sample_code = '''import pandas as pd
import re

# Data Available in this Dataframe:
df = data.copy()

def extract_order_details(message):
    """
    Extract order_id, email, phone, and amount from a message.
    
    Parameters:
        message: string containing customer support message
    
    Returns:
        dict with keys: order_id, email, phone, amount
    """
    # Your regex patterns here
    pass

# Apply extraction to each message
# result = df['message'].apply(extract_order_details).apply(pd.Series)
result = None  # Replace with your DataFrame'''

def get_input_data():
    import pandas as pd
    import os
    # Return dataframe from data.csv in the same directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, 'data.csv')
    return pd.read_csv(data_path)

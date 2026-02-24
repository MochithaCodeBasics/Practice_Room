description = """### Task
A support analytics team wants to convert raw customer messages into token IDs 
before sending them to a transformer model. Your task is to tokenize text using 
the DistilBERT tokenizer.

### Dataset
You are provided with a pandas DataFrame named `data` containing support messages:
- `text` - customer message (string)

### Requirements
1. Load the DistilBERT tokenizer (`distilbert-base-uncased`)
2. Tokenize each sentence in `data["text"]`
3. Return a DataFrame named `result` with the following columns:
   - `input_ids`
   - `attention_mask`

### Note
Tokenization must be done using the DistilBERT tokenizer.

### Evaluation
- Output format validation (input_ids, attention_mask)
- Both columns must contain lists
- attention_mask must contain only 0s and 1s
- Length of input_ids must match length of attention_mask

### Expected Outputs (script-style)
- Define `tokenizer = DistilBertTokenizer.from_pretrained(...)`
- Create DataFrame variable `result` with columns: `input_ids`, `attention_mask`

### Return
The function should return the result as specified in the task.

"""

hint = """
- `tokenizer(text)` returns dict with 'input_ids' and 'attention_mask'
"""

initial_sample_code = """import pandas as pd
from transformers import DistilBertTokenizer

# Data Available in this Dataframe:
df = data.copy()

# Load DistilBERT tokenizer
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

# Tokenize each text in df
# Your code here

# Create result DataFrame with columns: input_ids, attention_mask
result = None  # Replace with your DataFrame"""

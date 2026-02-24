description = """
A SaaS company receives a large number of customer support tickets every day.
To reduce manual effort and improve response time, they want to automatically 
classify each ticket into the correct category.

### Dataset
You are provided with a pandas DataFrame named `data` containing historical support tickets:
- `text` - customer support message (string)
- `category` - ticket category (Billing, Technical, Account)

### Task
Build a text classification pipeline that converts raw text into numerical features 
using TF-IDF and predicts the ticket category.

### Requirements
1. Split the data using:
   `train_test_split(test_size=0.2, random_state=42, stratify=y)`
2. Convert text into numerical features using TF-IDF
3. Train a suitable classification model
4. Generate predictions on the test set
5. Compute the following metrics:
   - `accuracy` on the test set
   - `macro_f1` on the test set
   - `n_features` — number of features produced by the TF-IDF vectorizer
   - `avg_tfidf` — average value of non-zero TF-IDF weights in the feature matrix

### Output
Return a DataFrame named `result` with columns:
- `metric`
- `value`

Containing rows for: accuracy, macro_f1, n_features, avg_tfidf

### Expected Outputs (script-style)
- Create a pandas DataFrame variable named `result`
- Columns must be `metric`, `value`
- Include rows: `accuracy`, `macro_f1`, `n_features`, `avg_tfidf`

### Note
You may use any classification model. The focus is on feature extraction using TF-IDF.
"""

hint = """
- Use `TfidfVectorizer` and `f1_score(..., average='macro')`
"""

initial_sample_code = """import pandas as pd
# data is provided
# Build TF-IDF classification pipeline and compute evaluation metrics
result = None  # pandas DataFrame with columns: metric, value
"""

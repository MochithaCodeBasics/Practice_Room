description = """
An e-commerce company wants to monitor customer sentiment from product reviews 
to detect dissatisfaction early and improve customer experience.

### Dataset
You are provided with a pandas DataFrame named `data` containing customer reviews:
- `review` - customer review text (string)

### Task
Use a Hugging Face transformers pipeline for sentiment analysis to classify each 
review as POSITIVE or NEGATIVE, along with a confidence score.

### Requirements
1. Use `transformers.pipeline("sentiment-analysis", ...)`
2. Predict sentiment for each row in `data["review"]`
3. Return a DataFrame named `result` with the following columns:
   - `review` (original review text)
   - `label` (POSITIVE / NEGATIVE)
   - `score` (confidence score as a float)

### Note
Use any suitable pretrained sentiment model from Hugging Face.

### Evaluation
- Output format validation: result must contain: review, label, score
- label must be one of POSITIVE or NEGATIVE

### Expected Outputs (script-style)
- Define `classifier` using `pipeline("sentiment-analysis", ...)`
- Create a pandas DataFrame variable named `result` with columns `review`, `label`, `score`
"""

hint = """
- `pipeline("sentiment-analysis")` returns dicts with 'label' and 'score'
"""

initial_sample_code = """import pandas as pd
from transformers import pipeline

# Data Available in this Dataframe:
df = data.copy()

# Create sentiment analysis pipeline with specific model to avoid warnings
classifier = pipeline(
    "sentiment-analysis", 
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

# Process each review (use truncation=True to avoid long text warnings)
# Your code here

# Create result DataFrame with columns: review, label, score
result = None  # Replace with your DataFrame"""

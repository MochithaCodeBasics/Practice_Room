description = """### Task
Build and return a fitted linear regression model for stock-price prediction.

### Function Signature
```python
def predict_stock(X, y):
```

### Requirements
- Train a `sklearn.linear_model.LinearRegression` model using inputs `X` and target `y`
- Return the fitted model object

### Input Format
- `X`: array-like feature matrix (shape `(n_samples, n_features)`)
- `y`: array-like target vector (shape `(n_samples,)`)

### Return
Return a fitted model object that exposes `.predict(...)`.

"""

hint = """Train and return a fitted `LinearRegression` model."""

initial_sample_code = """from sklearn.linear_model import LinearRegression
import numpy as np

def predict_stock(X, y):
    # return a fitted LinearRegression model
    pass
"""

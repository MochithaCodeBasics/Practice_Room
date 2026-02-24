"""
Question 7: Build a CNN for Geometric Shape Classification
Computer Vision - CNN Basics
"""

description = """
An educational technology company is building an interactive learning app for children that needs 
to recognize hand-drawn geometric shapes. The app will provide instant feedback when kids draw 
shapes on a tablet. They want to understand CNN architecture basics before deploying the system.

You are provided with a tensor dataset containing grayscale shape images.

### Input:
- `images` - 32x32 grayscale images
- `labels` - Shape labels:
  - 0 = Circle
  - 1 = Square
  - 2 = Triangle
  - 3 = Rectangle
  - 4 = Pentagon

Your task is to build a **Convolutional Neural Network (CNN)** to classify these shapes.

### Requirements

- Load data from `"data.pt"` using `torch.load`
- The loaded data is a dictionary with keys: `images` and `labels`
- Use `train_test_split(test_size=0.2, random_state=42, stratify=y)`
- Create `TensorDataset` and `DataLoader` for training and testing
- Build a CNN with:
  - At least 2 convolutional layers (`nn.Conv2d`)
  - Activation functions (ReLU)
  - At least 1 pooling layer (`nn.MaxPool2d` or `nn.AvgPool2d`)
  - Fully connected layers for classification
- Train for appropriate number of epochs
- Calculate on test set:
  - `accuracy` - Classification accuracy
  - `macro_f1` - Macro F1 score across all 5 classes
- Return a pandas DataFrame with columns: `metric`, `value`

### Function Signature
```python
def main():
```

### Return
- A pandas DataFrame with columns `metric`, `value`

### Example Output

| metric      | value  |
|-------------|--------|
| accuracy    | 0.92   |
| macro_f1    | 0.91   |
"""

hint = """
- Input images have shape `(batch_size, 1, 32, 32)` (single-channel grayscale)
- Apply transforms like ToTensor() and Normalize((0.5,), (0.5,)) for preprocessing
- Flatten convolution outputs before passing to `nn.Linear` layers
- Final output layer must have 5 units (one per shape class)
- Use `nn.CrossEntropyLoss()` for multi-class classification
- Use `f1_score(y_true, y_pred, average='macro')` for macro F1 computation

**Example of Model:**
Input (1, 32, 32) → Conv → ReLU → Pool → Conv → ReLU → Pool → Flatten → FC → Output (5)
"""

initial_sample_code = """# Import necessary libraries

def main():
    \"\"\"
    Build CNN to classify geometric shapes.

    Returns
    -------
    result : pandas.DataFrame
        DataFrame with 'metric' and 'value' columns
    \"\"\"
    # get_dataset_path is a utility function to get full path of dataset(already imported)
    dataset_path = get_dataset_path("data.pt")
    
    # Load dataset
    data = torch.load(dataset_path)
    X = data['images']
    y = data['labels']

    # Convert to TensorDataset (remember to check if they are already tensors)
    # If using transforms, you might need a custom Dataset class or apply them manually
    
    # Split data and define DataLoaders
    
    # Build CNN model
    
    # Train
    
    # Evaluate on test set and create results DataFrame
    
    return result

if __name__ == "__main__":
    result = main() # Save return value into a variable named `result`
    print(result)
"""

def get_description():
    return description

def get_hint():
    return hint


def get_dataset_path(filename):
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, filename)

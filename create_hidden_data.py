
import torch
import os

def create_hidden_data():
    base_dir = "c:/Users/User/Practice_Room/questions/question_51"
    data_path = os.path.join(base_dir, "data.pt")
    
    # Load original data
    data = torch.load(data_path)
    X = data['images']
    y = data['labels']
    
    # Create a smaller hidden dataset (e.g., 20% sample) for validation
    # This ensures the model must generalize to unseen data
    num_samples = len(y)
    hidden_size = int(num_samples * 0.2)
    
    # Use different indices or random subset
    indices = torch.randperm(num_samples)[:hidden_size]
    
    hidden_X = X[indices]
    hidden_y = y[indices]
    
    hidden_data = {
        'images': hidden_X,
        'labels': hidden_y
    }
    
    hidden_path = os.path.join(base_dir, "hidden_data.pt")
    torch.save(hidden_data, hidden_path)
    print(f"Created hidden_data.pt at {hidden_path} with {hidden_size} samples")
    
    # Also create the marker file
    marker_path = os.path.join(base_dir, "hidden_test_case.csv")
    with open(marker_path, "w") as f:
        f.write("marker")

if __name__ == "__main__":
    create_hidden_data()

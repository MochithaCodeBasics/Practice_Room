"""
Data generation script for Question 7: K-Means Clustering
Generates customer segmentation data
"""
import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

def generate_dataset(n_rows, seed):
    """Generate customer segmentation dataset with 3 natural clusters"""
    np.random.seed(seed)
    
    data = []
    n_per_cluster = n_rows // 3
    
    # Cluster 1: High-value customers (frequent, high spend, recent)
    for _ in range(n_per_cluster):
        data.append({
            'customer_id': f'C{len(data)+1:05d}',
            'total_spend': round(np.random.normal(5000, 1000), 2),
            'txn_count': int(np.random.poisson(30) + 20),
            'recency_days': int(np.random.exponential(10) + 1)
        })
    
    # Cluster 2: Medium-value customers (moderate frequency and spend)
    for _ in range(n_per_cluster):
        data.append({
            'customer_id': f'C{len(data)+1:05d}',
            'total_spend': round(np.random.normal(2000, 500), 2),
            'txn_count': int(np.random.poisson(12) + 5),
            'recency_days': int(np.random.exponential(30) + 10)
        })
    
    # Cluster 3: Low-value customers (infrequent, low spend, old)
    for _ in range(n_rows - 2*n_per_cluster):
        data.append({
            'customer_id': f'C{len(data)+1:05d}',
            'total_spend': round(np.random.normal(500, 200), 2),
            'txn_count': int(np.random.poisson(3) + 1),
            'recency_days': int(np.random.exponential(60) + 30)
        })
    
    df = pd.DataFrame(data)
    # Shuffle
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    
    # Ensure positive values
    df['total_spend'] = df['total_spend'].clip(lower=50).round(2)
    df['recency_days'] = df['recency_days'].clip(lower=0).astype(int)
    
    return df

# Generate dataset (1000 rows - no train/test split for clustering)
data_df = generate_dataset(1000, seed=42)
data_df.to_csv('data.csv', index=False)
print(f"✅ Generated data.csv with {len(data_df)} rows")
print(f"   Columns: {list(data_df.columns)}")
print(f"   Note: customer_id should NOT be used as a feature")
print(f"\n   Feature statistics:")
print(f"     total_spend: ${data_df['total_spend'].min():.2f} - ${data_df['total_spend'].max():.2f}")
print(f"     txn_count: {data_df['txn_count'].min()} - {data_df['txn_count'].max()}")
print(f"     recency_days: {data_df['recency_days'].min():.1f} - {data_df['recency_days'].max():.1f}")

print("\n📊 Dataset characteristics:")
print("   Type: Unsupervised clustering")
print("   Natural clusters: 3 (high/medium/low value customers)")
print("   Expected silhouette score: >0.35")
print("\n   Note: No hidden test data for clustering - evaluation on same dataset")

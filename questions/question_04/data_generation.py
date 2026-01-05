import pandas as pd
import numpy as np

np.random.seed(42)

# Base word sets (some anagram families)
anagram_groups = [
    ["listen", "silent", "enlist"],
    ["bat", "tab"],
    ["tap", "pat", "apt"],
    ["dusty", "study"],
    ["evil", "vile", "veil", "live"],
    ["rat", "tar", "art"],
    ["night", "thing"],
    ["god", "dog"]
]

# Flatten the list and randomly sample to create a larger dataset
all_words = [w for group in anagram_groups for w in group]
words = np.random.choice(all_words, size=200, replace=True)

df = pd.DataFrame({'word': words})


df.to_csv('questions/question_04/data.csv', index=False)
print("✅ dataset.csv generated successfully")

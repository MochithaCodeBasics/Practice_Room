import pandas as pd
import random
from faker import Faker

# Initialize Faker for generating realistic user data
fake = Faker()

# Generate the dataset with a more realistic movie list and more users
user_ids = list(range(1, 101))  # 100 unique users
movie_titles = [
    'The Shawshank Redemption', 'The Dark Knight', 'Inception', 'Fight Club', 'Pulp Fiction', 
    'The Matrix', 'Forrest Gump', 'The Godfather', 'The Lord of the Rings', 'The Avengers',
    'Titanic', 'Star Wars: Episode V', 'The Lion King', 'Gladiator', 'Schindler\'s List',
    'The Wolf of Wall Street', 'Interstellar', 'Parasite', 'The Departed', 'The Prestige'
]

n_rows = 500  # Number of rows to simulate

# Duplicates of user_id are allowed, so we can use the user_ids list repeatedly
user_ids_list = [random.choice(user_ids) for _ in range(n_rows)]

data = {
    'user_id': user_ids_list,
    'title': [random.choice(movie_titles) for _ in range(n_rows)],
    'seconds': [random.randint(60, 1800) for _ in range(n_rows)],  # Random watch time between 1 min and 30 mins
    'ts': pd.date_range(start="2025-10-21", periods=n_rows, freq='10T')  # Data at 10-minute intervals
}

# Adding realistic user data using Faker for names
data['user_name'] = [fake.name() for _ in range(n_rows)]

df = pd.DataFrame(data)

# Save the generated dataset to CSV
df.to_csv('questions/question_01/data.csv', index=False)

# Show a preview of the dataset to confirm
print(df.head())

import pandas as pd

data = pd.read_csv('questions/question_01/data.csv')

# Data Available in this Dataframe:
df = data.copy()

# Convert 'ts' column to datetime
df['ts'] = pd.to_datetime(df['ts'])

# Extract 'date' and 'hour' from 'ts'
df['date'] = df['ts'].dt.date
df['hour'] = df['ts'].dt.hour

# Debugging step: Check unique values in the 'date' column
print("Unique dates in the dataset:", df['date'].unique())

# Filter for October 21st, 2025
specific_date = '2025-10-21'
df_filtered = df[df['date'] == pd.to_datetime(specific_date).date()]

# Check if any data was filtered
if df_filtered.empty:
    print(f"No data available for {specific_date}.")
else:
    # Compute total seconds watched per hour
    result = df_filtered.groupby(['date', 'hour'])['seconds'].sum().reset_index()

    # Sort by total seconds in descending order and get the top 5 hours
    top_5_hours = result.sort_values(by='seconds', ascending=False).head(5)

    top_5_hours.to_csv('questions/question_01/expected.csv', index=False)
    # Output the result
    print(top_5_hours)

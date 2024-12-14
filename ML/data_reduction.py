"""
This script performs data reduction and preprocessing for cryptocurrency trading data, aiming to optimize
the dataset for training machine learning models. The steps include:
1. Extracting recent data based on a timestamp threshold to focus on the latest trends.
2. Performing batch sampling with progressively larger intervals to capture long-term patterns efficiently.
3. Including significant data points with high volatility to account for crucial market movements.
4. Merging and deduplicating the data, followed by timestamp-based sorting for a consistent time series.
5. Saving the final processed dataset for further model training.
"""

import pandas as pd
import argparse

# Argument parser setup
parser = argparse.ArgumentParser(description="Data reduction script")
parser.add_argument("--date", required=True, help="Date in YYYYMMDD format")
args = parser.parse_args()

# Use the date argument
date = args.date
print(f"Running data reduction for date: {date}")

file_path = '/home/fairy/ml/crypto_maniac'

# Define thresholds and parameters
recent_days_threshold = 24 * 60 * 60 * 10  # Last 5 days (0.5-second intervals)
volatility_threshold = 0.05  # Volatility threshold for significant price changes (5%)
batch_size = 1000  # Data size per batch for sampling

# Load data
data = pd.read_csv(f'{file_path}/processed_data_{date}_train.csv')

# 1. Sort data by timestamp
data = data.sort_values(by="timestamp")

# Extract recent data based on the threshold
recent_data_index = len(data) - 1  # Index of the most recent data point
recent_data_start_index = recent_data_index - (recent_days_threshold // 1)  # Extract 5 days of data
recent_data = data.iloc[max(recent_data_start_index, 0):]  # Ensure the index does not go below 0

# Print the length of the recent data
print(f"Recent data length: {len(recent_data)}")

# 2. Perform batch sampling with increasing intervals
def batch_sampling(data, batch_size):
    """
    Sample data with progressively increasing intervals.
    
    Args:
        data (DataFrame): DataFrame to sample from.
        batch_size (int): Size of each batch.
    
    Returns:
        DataFrame: Sampled data as a DataFrame.
    """
    sampled_batches = []  # List to store sampled batches
    total_length = len(data)  # Total number of data points

    # Initialize
    start_index = total_length - batch_size  # Start from the most recent data
    skip_step = batch_size  # Initial interval (equal to batch_size)

    while start_index >= 0:
        # Add the current batch to the sampled data
        sampled_batches.append(data.iloc[start_index : start_index + batch_size])
        # Increment the interval logarithmically
        skip_step = int(skip_step + 1000)  # Increase interval logarithmically
        start_index -= skip_step  # Move to the next batch
        print(start_index)

    # Combine all sampled batches into a single DataFrame
    return pd.concat(sampled_batches, ignore_index=True)

sparse_batches = batch_sampling(data.iloc[:-len(recent_data)], batch_size)

# 3. Include high-volatility data
important_data = data[data["price_change_rate"] >= volatility_threshold]

# 4. Merge recent data, sparse batches, and high-volatility data, then remove duplicates
final_data = pd.concat([recent_data, sparse_batches, important_data]).drop_duplicates()

# Sort the final data by timestamp
final_data = final_data.sort_values(by="timestamp").reset_index(drop=True)

# Save the final processed dataset
output_file = f'processed_data_{date}_final.csv'
final_data.to_csv(output_file, index=False)

print(f"Final data has been saved to {output_file}")
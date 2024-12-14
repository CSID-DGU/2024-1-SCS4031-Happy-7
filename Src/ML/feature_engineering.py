"""
This script performs feature engineering for cryptocurrency orderbook and ticks data. The workflow includes:
1. Preprocessing orderbook data to extract features such as price spread, mid-price, and orderbook imbalance.
2. Preprocessing ticks data to extract features such as price volatility, buy/sell ratio, and price change rate.
3. Batch processing large datasets to manage memory usage and improve performance.
4. Merging orderbook and ticks data by timestamp to create a unified dataset.
5. Saving the final processed datasets for training, validation, and testing purposes.
6. Cleaning up intermediate files to maintain storage efficiency.
"""

import pandas as pd
import json
import glob
import os
import argparse

# Argument parser setup
parser = argparse.ArgumentParser(description="Feature engineering script")
parser.add_argument("--date", required=True, help="Date in YYYYMMDD format")
args = parser.parse_args()

# Use the date argument
date = args.date
print(f"Running feature engineering for date: {date}")

file_path = '/home/fairy/ml/crypto_maniac'

# Dataset paths configuration
dataset_paths = {
    'train': {'orderbook': f'{file_path}/orderbooks/train/*.txt', 'ticks': f'{file_path}/ticks/train/*.txt'},
    'val': {'orderbook': f'{file_path}/orderbooks/validation/*.txt', 'ticks': f'{file_path}/ticks/validation/*.txt'},
    'test': {'orderbook': f'{file_path}/orderbooks/test/*.txt', 'ticks': f'{file_path}/ticks/test/*.txt'}
}

# Extract necessary features from orderbook data
def preprocess_orderbook(orderbook_df):
    orderbook_df['spread'] = orderbook_df['orderbook_units'].apply(lambda x: x[0]['ask_price'] - x[0]['bid_price'])
    orderbook_df['mid_price'] = orderbook_df['orderbook_units'].apply(lambda x: (x[0]['ask_price'] + x[0]['bid_price']) / 2)
    orderbook_df['obi'] = (orderbook_df['total_bid_size'] - orderbook_df['total_ask_size']) / \
                          (orderbook_df['total_bid_size'] + orderbook_df['total_ask_size'])
    return orderbook_df[['timestamp', 'spread', 'mid_price', 'obi']]

# Extract features from ticks data
def preprocess_ticks(ticks_df):
    ticks_df['price_volatility'] = ticks_df['trade_price'].rolling(window=30).std()
    ticks_df['buy_sell_ratio'] = (
        ticks_df['ask_bid']
        .apply(lambda x: 1 if x == 'BID' else 0)
        .rolling(window=30)
        .mean()
    )
    ticks_df['price_change_rate'] = (
        ticks_df['trade_price']
        .rolling(window=30)
        .apply(lambda x: (x.max() - x.min()) / x.max() if x.max() > 0 else 0, raw=True)
    )
    return ticks_df[['timestamp', 'trade_price', 'price_volatility', 'buy_sell_ratio', 'price_change_rate']]

# Merge batch files into a single dataset
def merge_batches(batch_prefix, output_file):
    batch_files = glob.glob(f'{file_path}/{batch_prefix}_batch_*.csv')
    merged_df = pd.concat([pd.read_csv(file) for file in batch_files])
    merged_df.dropna(inplace=True)
    merged_df.to_csv(output_file, index=False)

# Delete intermediate files
def delete_files(file_pattern):
    files = glob.glob(file_pattern)
    for file in files:
        try:
            os.remove(file)
            print(f"Deleted file: {file}")
        except OSError as e:
            print(f"Error deleting file {file}: {e}")

# Process data for a given orderbook and ticks path
def process_data(orderbook_path, ticks_path, dataset_type):
    orderbook_files = glob.glob(orderbook_path)
    ticks_files = glob.glob(ticks_path)

    orderbook_data = []
    ticks_data = []
    batch_size = 4

    # Process orderbook data in batches
    for batch_start in range(0, len(orderbook_files), batch_size):
        batch_files = orderbook_files[batch_start:batch_start + batch_size]
        for file_idx, file in enumerate(batch_files):
            print(f"Processing orderbook file {file_idx + 1}/{len(batch_files)} in batch: {file}")
            with open(file, 'r') as f:
                for line in f:
                    line = line.replace("'", '"')
                    try:
                        data = json.loads(line)
                        orderbook_data.append(data)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON in file {file}: {e}")
        
        orderbook_df = pd.DataFrame(orderbook_data)
        if not orderbook_df.empty:
            orderbook_df.drop_duplicates(subset=['timestamp'], inplace=True)
            orderbook_df.sort_values(by='timestamp', inplace=True)
            orderbook_processed = preprocess_orderbook(orderbook_df)
            orderbook_data.clear()
            orderbook_processed.to_csv(f'{file_path}/orderbook_batch_{batch_start}.csv', index=False)

    # Process ticks data in batches
    for batch_start in range(0, len(ticks_files), batch_size):
        batch_files = ticks_files[batch_start:batch_start + batch_size]
        for file_idx, file in enumerate(batch_files):
            print(f"Processing ticks file {file_idx + 1}/{len(batch_files)} in batch: {file}")
            with open(file, 'r') as f:
                for line in f:
                    line = line.replace("'", '"')
                    try:
                        data = json.loads(line)
                        ticks_data.append(data)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON in file {file}: {e}")
        
        ticks_df = pd.DataFrame(ticks_data)
        if not ticks_df.empty:
            ticks_df.drop_duplicates(subset=['timestamp'], inplace=True)
            ticks_df.sort_values(by='timestamp', inplace=True)
            ticks_processed = preprocess_ticks(ticks_df)
            ticks_data.clear()
            ticks_processed.to_csv(f'{file_path}/ticks_batch_{batch_start}.csv', index=False)

    # Merge and align orderbook and ticks data
    merge_batches('orderbook', f'{file_path}/final_orderbook_data.csv')
    merge_batches('ticks', f'{file_path}/final_ticks_data.csv')

    final_orderbook_df = pd.read_csv(f'{file_path}/final_orderbook_data.csv')
    final_ticks_df = pd.read_csv(f'{file_path}/final_ticks_data.csv')

    final_orderbook_df.sort_values(by='timestamp', inplace=True)
    final_ticks_df.sort_values(by='timestamp', inplace=True)

    merged_data = pd.merge_asof(final_orderbook_df, final_ticks_df, on='timestamp', direction='nearest')
    merged_data.to_csv(f'{file_path}/processed_data_{date}_{dataset_type}.csv', index=False)

    delete_files(f'{file_path}/orderbook_batch_*.csv')
    delete_files(f'{file_path}/ticks_batch_*.csv')
    delete_files(f'{file_path}/final_orderbook_data.csv')
    delete_files(f'{file_path}/final_ticks_data.csv')

# Process datasets
for dataset_type, paths in dataset_paths.items():
    print(f"Processing {dataset_type} data...")
    process_data(paths['orderbook'], paths['ticks'], dataset_type)
    print(f"{dataset_type} data processing finished.")

print("All dataset processing completed successfully!")

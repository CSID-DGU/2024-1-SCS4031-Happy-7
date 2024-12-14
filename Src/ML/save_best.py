"""
This script identifies and saves the best-performing model and associated scalers based on the lowest test loss
from the training results. The steps include:
1. Reading the test loss CSV file to find the model configuration with the minimum loss.
2. Deleting existing files in the `best` directory to ensure it contains only the latest best files.
3. Copying the model and scalers corresponding to the best configuration into the `best` directory.
4. Verifying the existence of all required files before copying and warning if any files are missing.
"""

import os
import pandas as pd
import shutil
import argparse

# Argument parser setup
parser = argparse.ArgumentParser(description="Save best model and scalers")
parser.add_argument("--date", required=True, help="Date in YYYYMMDD format")
args = parser.parse_args()

# Use the date argument
date = args.date
print(f"Running save best for date: {date}")

# Set paths
file_path = '/home/fairy/ml/crypto_maniac'
results_dir = f"{file_path}/training_results_{date}"  # Directory for training results
best_dir = f"{file_path}/best"  # Directory to save the best model

# Path to the CSV file
csv_path = os.path.join(results_dir, "test_losses.csv")

# Read the CSV file
try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    print(f"Error: {csv_path} file not found.")
    exit(1)

# Check if necessary columns exist
if 'test_loss' not in df.columns or 'file_suffix' not in df.columns:
    print(f"Error: 'test_loss' or 'file_suffix' column is missing in {csv_path}.")
    exit(1)

# Get the file_suffix of the row with the minimum test_loss
min_loss_row = df.loc[df['test_loss'].idxmin()]
best_file_suffix = min_loss_row['file_suffix']

# Generate filenames
model_name = f"lstm_model_{best_file_suffix}.pth"
scaler_x_name = f"scaler_X_{best_file_suffix}.pkl"
scaler_y_name = f"scaler_y_{best_file_suffix}.pkl"

# Files to copy
files_to_copy = {
    "model": model_name,
    "scaler_X": scaler_x_name,
    "scaler_y": scaler_y_name
}

# Ensure the best directory exists
os.makedirs(best_dir, exist_ok=True)

# Delete existing files in the /best/ directory
print("Deleting existing files in /best/...")
for file in os.listdir(best_dir):
    file_path = os.path.join(best_dir, file)
    try:
        os.remove(file_path)
        print(f"Deleted: {file_path}")
    except OSError as e:
        print(f"Error deleting file {file_path}: {e}")

# Copy new files to the /best/ directory
for file_type, file_name in files_to_copy.items():
    source = os.path.join(results_dir, file_type, file_name)  # Subdirectories: model, scaler_X, scaler_y
    destination = os.path.join(best_dir, file_name)
    
    if os.path.exists(source):
        shutil.copy(source, destination)
        print(f"Copied {file_type}: {source} -> {destination}")
    else:
        print(f"Warning: {source} file does not exist.")

print("Best model and scalers have been successfully saved.")

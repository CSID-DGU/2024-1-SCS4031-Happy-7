"""
This script performs hyperparameter tuning and training of an LSTM model for cryptocurrency price prediction.
It includes the following steps:
1. Accepts a date argument to specify the dataset for processing.
2. Loads and preprocesses training, validation, and test datasets, normalizing the features and target.
3. Generates sequences for time series data, ensuring continuity of timestamps.
4. Performs hyperparameter tuning by testing various configurations of epochs, hidden layers, learning rates, etc.
5. Implements early stopping based on validation loss to avoid overfitting.
6. Saves the trained model, scalers, and results (e.g., loss curves, prediction plots) for each hyperparameter combination.
7. Logs test performance for future reference and analysis.
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import RobustScaler
import matplotlib.pyplot as plt
import joblib
import os
import argparse

# Argument parser setup
parser = argparse.ArgumentParser(description="Model training script")
parser.add_argument("--date", required=True, help="Date in YYYYMMDD format")
args = parser.parse_args()

# Use the date argument
date = args.date
print(f"Running model training for date: {date}")

file_path = '/home/fairy/ml/crypto_maniac'

# Set the Matplotlib backend to 'Agg' to avoid Tkinter-related issues
import matplotlib
matplotlib.use('Agg')

torch.backends.cudnn.benchmark = True
torch.backends.cudnn.fastest = True

from torch.utils.data import DataLoader
from torch.amp import autocast, GradScaler

def generate_all_sequences(data, target, sequence_length, target_step, timestamp_gap):
    """
    Pre-generate all sequences based on the given data.

    Args:
        data (ndarray): Input data (first column must be timestamps).
        target (ndarray): Target data.
        sequence_length (int): Length of each sequence.
        target_step (int): Step for the target prediction.
        timestamp_gap (int): Maximum allowable gap between consecutive timestamps.

    Returns:
        sequences (ndarray): Generated sequence data (N, sequence_length, feature_size).
        targets (ndarray): Generated target data (N,).
        timestamps_out (ndarray): Timestamps corresponding to the targets.
    """
    sequences = []
    targets = []
    timestamps_out = []  # Store the last timestamp of each sequence
    data_len = len(data)

    # Separate timestamps and features
    timestamps = data[:, 0]
    features = data[:, 1:]

    for start_index in range(data_len - sequence_length - target_step):
        current_timestamps = timestamps[start_index:start_index + sequence_length]

        # Check for timestamp continuity
        if np.any(np.diff(current_timestamps) > timestamp_gap):
            continue

        # Add sequence and target
        sequences.append(features[start_index:start_index + sequence_length])
        targets.append(target[start_index + sequence_length + target_step])
        timestamps_out.append(timestamps[start_index + sequence_length + target_step])  # Add target timestamp

    return np.array(sequences), np.array(targets), np.array(timestamps_out)

class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(LSTMModel, self).__init__()
        self.num_layers = num_layers
        # Apply dropout only if num_layers > 1
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
        
    def forward(self, x):
        h_0 = torch.zeros(self.num_layers, x.size(0), hidden_size).to(device)  # Initial hidden state
        c_0 = torch.zeros(self.num_layers, x.size(0), hidden_size).to(device)  # Initial cell state
        out, _ = self.lstm(x, (h_0, c_0))
        out = out[:, -1, :]
        out = self.fc(out)  # Output from the last time step
        return out

# Load data
train_data = pd.read_csv(f'{file_path}/processed_data_{date}_final.csv')
val_data = pd.read_csv(f'{file_path}/processed_data_{date}_val.csv')
test_data = pd.read_csv(f'{file_path}/processed_data_{date}_test.csv')

features = ['spread', 'mid_price', 'obi', 'price_volatility', 'buy_sell_ratio', 'price_change_rate']
target = 'trade_price'

X_train = train_data[features].values
y_train = train_data[target].values

# Create and normalize data using RobustScaler
scaler_X = RobustScaler()
scaler_y = RobustScaler()

# Include timestamp in the data
X_train = train_data[['timestamp'] + features].values  # Add timestamp
X_train[:, 1:] = scaler_X.fit_transform(X_train[:, 1:])  # Normalize excluding timestamp
y_train = scaler_y.fit_transform(train_data[[target]].values)

X_val = val_data[['timestamp'] + features].values  # Add timestamp
X_val[:, 1:] = scaler_X.transform(X_val[:, 1:])  # Normalize excluding timestamp
y_val = scaler_y.transform(val_data[[target]].values)

X_test = test_data[['timestamp'] + features].values  # Add timestamp
X_test[:, 1:] = scaler_X.transform(X_test[:, 1:])  # Normalize excluding timestamp
y_test = scaler_y.transform(test_data[[target]].values)

# Function to create directories
def create_directories(base_path, subdirectories):
    for subdir in subdirectories:
        path = os.path.join(base_path, subdir)
        if not os.path.exists(path):
            os.makedirs(path)

# Set base path and subdirectories
base_path = f'{file_path}/training_results_{date}'
subdirectories = ['model', 'loss_curve', 'scaler_X', 'scaler_y', 'test_results']

# Create directories
create_directories(base_path, subdirectories)

# Initialize CSV file for logging results
csv_file_path = f"{base_path}/test_losses.csv"
if not os.path.exists(csv_file_path):
    with open(csv_file_path, 'w') as f:
        f.write('file_suffix,test_loss,image\n')

# Set the device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Hyperparameter tuning ranges
epoch_range = [100]
hidden_size_range = [100, 150, 200]
num_layers_range = [1]
sequence_length_range = range(90, 181, 30)
learning_rates = [0.003, 0.005, 0.01, 0.03]

# Define PyTorch Dataset
class SequenceDataset(torch.utils.data.Dataset):
    def __init__(self, sequences, targets):
        self.sequences = torch.tensor(sequences, dtype=torch.float32)
        self.targets = torch.tensor(targets, dtype=torch.float32)

    def __len__(self):
        return len(self.sequences)

    def __getitem__(self, idx):
        return self.sequences[idx], self.targets[idx]

# Hyperparameter tuning loop
for num_epochs in epoch_range:
    for hidden_size in hidden_size_range:
        for num_layers in num_layers_range:
            for sequence_length in sequence_length_range:
                for lr in learning_rates:
                    
                    target_step = 60
                    timestamp_gap = 1000   
                    batch_size = 1000

                    # Generate sequences for training, validation, and testing
                    X_train_seq, y_train_seq, _ = generate_all_sequences(X_train, y_train, sequence_length, target_step, timestamp_gap)
                    X_val_seq, y_val_seq, _ = generate_all_sequences(X_val, y_val, sequence_length, target_step, timestamp_gap)
                    X_test_seq, y_test_seq, test_timestamps = generate_all_sequences(X_test, y_test, sequence_length, target_step, timestamp_gap)
                    
                    # Create Datasets and DataLoaders
                    train_dataset = SequenceDataset(X_train_seq, y_train_seq)
                    val_dataset = SequenceDataset(X_val_seq, y_val_seq)
                    test_dataset = SequenceDataset(X_test_seq, y_test_seq)

                    train_loader = DataLoader(train_dataset, batch_size, shuffle=False, num_workers=4)
                    val_loader = DataLoader(val_dataset, batch_size, shuffle=False, num_workers=4)
                    test_loader = DataLoader(test_dataset, batch_size, shuffle=False, num_workers=4)

                    file_suffix = f"e{num_epochs}_s{sequence_length}_h{hidden_size}_l{num_layers}_lr{lr}_{date}"                
                    model_path = f'{base_path}/model/lstm_model_{file_suffix}.pth'

                    # Skip already tested configurations
                    if os.path.exists(model_path):
                        print(f"Skipping already tested configuration: {file_suffix}")
                        continue

                    model = LSTMModel(len(features), hidden_size, num_layers, 1).to(device)
                    optimizer = optim.Adamax(model.parameters(), lr=lr)
                    criterion = nn.MSELoss()
                    scaler = GradScaler('cuda')

                    # Early stopping setup
                    patience = 5
                    min_delta = 0.00001

                    best_val_loss = float('inf')
                    no_improvement_count = 0
                    train_losses, val_losses = [], []

                    # Training loop
                    for epoch in range(num_epochs):
                        model.train()
                        train_loss = 0

                        # Training step
                        for batch_X, batch_y in train_loader:
                            batch_X, batch_y = batch_X.to(device), batch_y.to(device)

                            optimizer.zero_grad()
                            with autocast(device_type='cuda'):
                                outputs = model(batch_X)
                                loss = criterion(outputs.squeeze(), batch_y.squeeze())
                            scaler.scale(loss).backward()
                            scaler.step(optimizer)
                            scaler.update()

                            train_loss += loss.item()

                        train_loss /= len(train_loader)
                        train_losses.append(train_loss)

                        # Validation step
                        model.eval()
                        val_loss = 0
                        with torch.no_grad():
                            for batch_X, batch_y in val_loader:
                                batch_X, batch_y = batch_X.to(device), batch_y.to(device)
                                with autocast(device_type='cuda'):
                                    val_outputs = model(batch_X)
                                    loss = criterion(val_outputs.squeeze(), batch_y.squeeze())
                                val_loss += loss.item()

                        val_loss /= len(val_loader)
                        val_losses.append(val_loss)
                        print(f"Epoch {epoch+1}, Train Loss: {train_loss:.4f}, Validation Loss: {val_loss:.4f}")

                        # Early stopping logic
                        if val_loss < best_val_loss - min_delta:
                            best_val_loss = val_loss
                            no_improvement_count = 0
                        else:
                            no_improvement_count += 1
                            print(f"No improvement in validation loss. Count: {no_improvement_count}/{patience}")

                        if no_improvement_count >= patience:
                            print("Early stopping triggered. Training stopped.")
                            break

                    # Test evaluation
                    model.eval()
                    test_loss = 0
                    predictions = []
                    actuals = []

                    # Evaluate on the test set
                    with torch.no_grad():
                        for batch_X, batch_y in test_loader:
                            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
                            with autocast(device_type='cuda'):
                                test_outputs = model(batch_X)
                                loss = criterion(test_outputs.squeeze(), batch_y.squeeze())
                            test_loss += loss.item()

                            predictions.append(test_outputs.cpu().numpy())
                            actuals.append(batch_y.cpu().numpy())

                    # Sort predictions and actuals by timestamp
                    predictions = np.concatenate(predictions)
                    actuals = np.concatenate(actuals)
                    sorted_indices = np.argsort(test_timestamps)
                    test_timestamps = test_timestamps[sorted_indices]
                    predictions = predictions[sorted_indices]
                    actuals = actuals[sorted_indices]

                    # Calculate average test loss
                    test_loss_avg = test_loss / len(test_loader)
                    print(f'Test Loss for {file_suffix}: {test_loss_avg:.6f}')

                    # Log test loss in CSV
                    with open(csv_file_path, 'a') as f:
                        f.write(f'{file_suffix},{test_loss_avg},"=hyperlink(""./test_results/test_results_{file_suffix}.png"")"\n')

                    # Save the model and scalers
                    torch.save(model.state_dict(), model_path)
                    joblib.dump(scaler_X, f'{base_path}/scaler_X/scaler_X_{file_suffix}.pkl')
                    joblib.dump(scaler_y, f'{base_path}/scaler_y/scaler_y_{file_suffix}.pkl')

                    # Save loss curves
                    plt.figure(figsize=(10, 5))
                    plt.plot(train_losses, label='Train Loss')
                    plt.plot(val_losses, label='Validation Loss')
                    plt.legend()
                    plt.title(f"Train vs Validation Loss\nEpochs: {num_epochs}, Hidden: {hidden_size}, Layers: {num_layers}, LR: {lr}")
                    plt.savefig(f"{base_path}/loss_curve/loss_curve_{file_suffix}.png")
                    plt.close()

                    # Save predictions vs actuals
                    plt.figure(figsize=(12, 6))
                    plt.plot(test_timestamps, actuals, label='Actual Price', alpha=0.8)
                    plt.plot(test_timestamps, predictions, label='Predicted Price', alpha=0.8)
                    plt.legend()
                    plt.title(f"Actual vs Predicted Price\nTest Loss: {test_loss_avg:.6f}")
                    plt.xlabel('Timestamp')
                    plt.ylabel('Price')
                    plt.savefig(f"{base_path}/test_results/test_results_{file_suffix}.png")
                    plt.close()

                    # Clear GPU memory
                    torch.cuda.empty_cache()

                    print(f"Model saved and test evaluation completed for {file_suffix}")

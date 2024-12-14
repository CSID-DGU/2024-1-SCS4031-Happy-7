"""
This script is designed for a cryptocurrency trading system that predicts price movements using an LSTM model
and sends trading commands based on the predictions. It involves the following steps:
1. Load the best model and corresponding scalers from the `./best` directory.
2. Establish persistent socket connections with data and command servers.
3. Continuously fetch data from the data server, preprocess it, and predict price movements using the LSTM model.
4. Generate trading commands (BUY or SELL) based on the predictions and send them to the command server.
5. Handle socket communication and data processing errors gracefully.
"""

import pandas as pd
import numpy as np
import json
import torch
import torch.nn as nn
import joblib
import socket
import time
import os
import glob
from datetime import datetime, timedelta, timezone

# Setup best model's directory
BEST_DIR = "./best"

# Search for the best model and scalers
model_files = glob.glob(os.path.join(BEST_DIR, "lstm_model_*.pth"))
scaler_x_files = glob.glob(os.path.join(BEST_DIR, "scaler_X_*.pkl"))
scaler_y_files = glob.glob(os.path.join(BEST_DIR, "scaler_y_*.pkl"))

# Check if all required files exist
if not model_files:
    raise FileNotFoundError("No model file found in the /best directory.")
if not scaler_x_files:
    raise FileNotFoundError("No scaler_X file found in the /best directory.")
if not scaler_y_files:
    raise FileNotFoundError("No scaler_Y file found in the /best directory.")

# Retrieve filenames (assuming the first file is used)
MODEL_FILENAME = model_files[0]
SCALER_X_PATH = scaler_x_files[0]
SCALER_Y_PATH = scaler_y_files[0]

# Define the LSTM model
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(LSTMModel, self).__init__()
        self.num_layers = num_layers
        self.hidden_size = hidden_size
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        h_0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device)
        c_0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device)
        out, _ = self.lstm(x, (h_0, c_0))
        return self.fc(out[:, -1, :])

# Load the model and extract sequence length
def load_model(filename, input_size=6, output_size=1):
    import re
    match = re.search(r"e\d+_s(\d+)_h(\d+)_", filename)
    if not match:
        raise ValueError("Filename does not match the expected pattern.")
    sequence_length = int(match.group(1))
    hidden_size = int(match.group(2))
    model = LSTMModel(input_size, hidden_size, num_layers=1, output_size=output_size).to(device)
    model.load_state_dict(torch.load(filename))
    model.eval()
    return model, sequence_length

# Fetch data and process for predictions
def fetch_and_process_data(persistent_socket, model, scaler_X, scaler_y):
    try:
        buffer = b""  # Buffer to store received data
        while True:
            chunk = persistent_socket.recv(4096)
            if not chunk:
                print("No data received. Retrying...")
                return None, None, None, None, None  # Data fetch failure

            buffer += chunk
            while b"END" in buffer:  # Split data by "END"
                json_data, buffer = buffer.split(b"END", 1)
                try:
                    # Process JSON data
                    json_object = json.loads(json_data.decode())
                    
                    dataframe = pd.DataFrame(json_object)

                    # Extract threshold and userID values
                    threshold = dataframe["threshold"].iloc[0] if "threshold" in dataframe.columns else None
                    user_id = dataframe["userID"].iloc[0] if "userID" in dataframe.columns else None

                    # Preprocess data and make predictions
                    features = ["spread", "mid_price", "obi", "price_volatility", "buy_sell_ratio", "price_change_rate"]
                    data = dataframe[features]
                    normalized_data = scaler_X.transform(data.values)

                    if len(normalized_data.shape) == 2:
                        normalized_data = normalized_data[np.newaxis, :, :]

                    input_tensor = torch.tensor(normalized_data, dtype=torch.float32).to(device)
                    with torch.no_grad():
                        predictions = model(input_tensor)
                    predictions_np = predictions.cpu().numpy()
                    restored_predictions = scaler_y.inverse_transform(predictions_np)

                    # Calculate predicted timestamp (30 seconds after the current time in UTC)
                    recent_timestamp = dataframe["timestamp"].iloc[-1]
                    predicted_timestamp_utc = datetime.fromtimestamp(recent_timestamp, tz=timezone.utc) + timedelta(seconds=30)

                    return dataframe, restored_predictions, user_id, threshold, predicted_timestamp_utc

                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    continue  # Process the next buffer data
    except Exception as e:
        print(f"Failed to fetch and process data: {e}")
        return None, None, None, None, None

# Generate trade commands with timestamp
def generate_trade_command(predictions, dataframe, predicted_timestamp_utc, user_id=2, threshold=0.0006):
    """
    Generate a trade command based on the predicted price and the recent mid price from the data.

    Args:
        predictions (ndarray): Predicted price values.
        dataframe (DataFrame): Data containing recent mid prices and timestamps.
        predicted_timestamp_utc (datetime): Predicted timestamp in UTC.
        user_id (int): User ID for the trade command.
        threshold (float): Threshold for price difference to trigger a trade.

    Returns:
        dict: Trade command containing user ID, action, amount, predicted price, and predicted timestamp, or None if no action is needed.
    """
    threshold += 0.0005
    recent_row = dataframe.loc[dataframe["timestamp"].idxmax()]
    recent_mid_price = recent_row["mid_price"]

    predicted_price = predictions[0, 0]
    price_diff = (predicted_price - recent_mid_price) / recent_mid_price

    print(f'UserID: {user_id}, Current threshold: {threshold:.4f}, Price Difference: {price_diff:.6f}')

    if price_diff > threshold:
        return {
            "userId": int(user_id),
            "action": "BUY",
            "amount": 5000,
            "predicted_price": float(predicted_price),
            "predicted_timestamp": predicted_timestamp_utc.isoformat()
        }
    elif price_diff < -threshold:
        return {
            "userId": int(user_id),
            "action": "SELL",
            "amount": 0.0001,
            "predicted_price": float(predicted_price),
            "predicted_timestamp": predicted_timestamp_utc.isoformat()
        }
    else:
        return {
            "predicted_price": float(predicted_price),
            "predicted_timestamp": predicted_timestamp_utc.isoformat()
        }

# Send trade commands to the server
def send_trade_command(persistent_socket, command):
    if command is None:
        print("No trade command to send.")
        return

    try:
        # Convert to JSON and send
        json_data = json.dumps(command)
        message = json_data + "\nEND\n"
        persistent_socket.sendall(message.encode('utf-8'))
        print("Trade command sent.")

        # Receive server response
        response = persistent_socket.recv(4096)
        print(f"Server response: {response.decode()}")
    except Exception as e:
        print(f"Failed to send trade command: {e}")
        raise

if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using device:", device)

    try:
        scaler_X = joblib.load(SCALER_X_PATH)
        scaler_y = joblib.load(SCALER_Y_PATH)
        model, sequence_length = load_model(MODEL_FILENAME)
        print("Model and scalers loaded successfully.")
    except Exception as e:
        print(f"Initialization error: {e}")
        exit(1)

    # Server information
    data_server_ip = "15.165.154.150"
    data_server_port = 9000
    command_server_ip = "15.165.154.150"
    command_server_port = 9001

    # Connect to the data server
    try:
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_socket.connect((data_server_ip, data_server_port))
        print("Connected to data server.")
    except Exception as e:
        print(f"Failed to connect to data server: {e}")
        time.sleep(1)  # Retry delay

    # Connect to the command server
    try:
        command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        command_socket.connect((command_server_ip, command_server_port))
        print("Connected to command server.")
    except Exception as e:
        print(f"Failed to connect to command server: {e}")
        time.sleep(1)  # Retry delay
        
    try:
        while True:
            start_time = time.time()

            # Fetch and process data
            dataframe, predictions, user_id, threshold, predicted_timestamp_utc = fetch_and_process_data(
                data_socket, model, scaler_X, scaler_y
            )
            if dataframe is None or predictions is None:
                print("Error in data processing. Retrying...")
                time.sleep(1)
                continue

            # Generate and send trade commands
            trade_command = generate_trade_command(predictions, dataframe, predicted_timestamp_utc, user_id, threshold)
            if "action" in trade_command:
                # Trade command contains an action (BUY or SELL)
                print("Generated Trade Command with Action:", json.dumps(trade_command, indent=4))
            else:
                # No significant prediction change, only prediction data is included
                print("No significant prediction change. Only Prediction Data:", json.dumps(trade_command, indent=4))
            send_trade_command(command_socket, trade_command)

            elapsed_time = time.time() - start_time
            time.sleep(max(1 - elapsed_time, 0))

    except KeyboardInterrupt:
        print("Process interrupted by user.")
    finally:
        # Close sockets
        data_socket.close()
        command_socket.close()
        print("Sockets closed.")

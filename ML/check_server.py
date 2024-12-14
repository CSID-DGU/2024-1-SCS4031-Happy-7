# Description:
# This script connects to a remote server using a socket, sends a JSON-formatted string, and receives a response.
# It measures the time taken to complete the data transfer and prints the server's response along with the transfer duration.

import socket
import time

server_ip = "15.165.154.150"  # Public IP of the EC2 server
server_port = 9000            # Server port

# JSON string data
json_data = '{"userId": 1, "action": "buy", "amount": "5000", "execute_time": "18:30:00.500"}'

# Establish a socket connection
start_time = time.time()  # Start measuring the transfer time
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))

# Send data
client_socket.sendall(json_data.encode())  # Convert JSON string to binary and send
client_socket.shutdown(socket.SHUT_WR)  # Indicate that data transfer is complete

# Receive server response
response = client_socket.recv(4096)
print("Received from server:", response.decode())

client_socket.close()
end_time = time.time()  # Stop measuring the transfer time

print(f"Data transfer completed in {end_time - start_time:.2f} seconds")

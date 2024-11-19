import socket
import time
import sys
import cv2

from data_protocol import sender, receiver

# Configuration
host = '127.0.0.1'  # Server address
port = 50000        # Server port
retry_interval = 5  # Seconds to wait before retrying

def connect_to_server():
    while True:
        try:
            print(f"Attempting to connect to {host}:{port}...")
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            print("Connected to the server!")
            return client_socket
        except (socket.error, ConnectionRefusedError):
            print(f"Connection failed. Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)

def client():
    client_socket = connect_to_server()

    while True:
        try:
            sender(client_socket)
        except (socket.error, ConnectionResetError):
            print("Connection lost. Reconnecting...")
            client_socket.close()
            client_socket = connect_to_server() # Restart the connection
        except KeyboardInterrupt:
            break

    client_socket.close()
    print("Connection closed. Client shutdown.")

def start_server():
    while True:
        try:
            # Create and bind the socket
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(("", port))
            server_socket.listen(1)  # Accept up to 5 queued connections
            print(f"Server listening on port {port}")
            return server_socket
        except socket.error as e:
            print(f"Error starting server: {e}. Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)

def wait_connection(server_socket: socket.socket):
    # Accept an incoming connection
    print("Waiting for a connection...")
    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")
    return client_socket, client_address

def server():
    server_socket = start_server()
    client_socket, client_address = wait_connection(server_socket)

    while True:
        try:
            frame, img_time = receiver(client_socket)
            # coloca aqui o publisher do dbtime ou usa esse valor direto para buscar os
            # dados da imu compatíveis
            cv2.imshow("frame", frame)
            cv2.waitKey(1)
            print(img_time)

        except (socket.error, ConnectionResetError) as e:
            print(f"Connection error: {e}. Continuing to listen...")
        except KeyboardInterrupt:
            print("Server shutting down...")
            break

        if client_socket.fileno() == -1:
            print("Socket closed. Restarting server...")
            server_socket = start_server()  # Restart server on failure
            client_socket, client_address = wait_connection(server_socket)

    server_socket.close()
    client_socket.close()
    print(f"Connections closed. Server shutdown.")

if __name__ == "__main__":
    args = sys.argv[1]
    
    if args == "client":
        client()
    elif args == "server":
        server()
    else:
        print("Unsupported option")
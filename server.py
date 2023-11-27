import os
import socket
import threading

def handle_client(conn, addr, database_folder):
    with conn:
        # Receive request type (list, download, or upload)
        request_type = conn.recv(1024).decode()

        if request_type == "list":
            # Send list of files in the database folder
            file_list = "\n".join(os.listdir(database_folder))
            conn.sendall(file_list.encode())
            print(f"File list sent successfully to {addr}")

        elif request_type == "download":
            # Receive file name
            file_name = conn.recv(1024).decode()
            print(f"Receiving file {file_name} from {addr}")

            # Construct the file path
            file_path = os.path.join(database_folder, file_name)

            # Check if the file exists
            if os.path.exists(file_path):
                # Send file existence confirmation
                conn.sendall("EXISTS".encode())

                # Open the file and send its content
                with open(file_path, 'rb') as file:
                    data = file.read(1024)
                    while data:
                        conn.sendall(data)
                        data = file.read(1024)

                print(f"File {file_name} sent successfully to {addr}")

            else:
                # Send file not found notification
                conn.sendall("NOT_FOUND".encode())
                print(f"File {file_name} not found for {addr}")

        elif request_type == "upload":
            # Receive file name
            file_name = conn.recv(1024).decode()
            print(f"Receiving file {file_name} from {addr}")

            # Construct the file path
            file_path = os.path.join(database_folder, file_name)

            # Receive and save file content
            with open(file_path, 'wb') as file:
                data = conn.recv(1024)
                while data:
                    file.write(data)
                    data = conn.recv(1024)

            print(f"File {file_name} received successfully from {addr}")

        else:
            print(f"Invalid request type from {addr}")

def start_server():
    host = "192.168.18.109"
    port = 12345
    database_folder = "./Database"

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Server listening on {host}:{port}")

    while True:
        conn, addr = server_socket.accept()
        print(f"Connection from {addr}")

        # Create a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(conn, addr, database_folder))
        client_thread.start()

if __name__ == "__main__":
    start_server()
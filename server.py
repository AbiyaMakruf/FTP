import os
import socket
import threading
import time
import json

def save_database(database):
    with open('database.json', 'w') as file:
        json.dump(database, file, indent=2)

def handle_client(conn, addr, database_folder):
    with conn:
        # Receive request type (list, download, or upload)
        request_type = conn.recv(1024).decode()
        print(request_type)

        if request_type == "login":
            # Receive username and password
            username = conn.recv(1024).decode()
            password = conn.recv(1024).decode()
            print(f"Login request from {addr} with username {username} and password {password}")

            # Check if the user exists
            user_exists = False
            try:
                with open('database.json', 'r') as file:
                    database = json.load(file)
            except FileNotFoundError:
                print("File database.json tidak ditemukan.")
            
            user_exists = False

            if username in database and database[username]['password'] == password:
                print("Login berhasil!")
                database[username]['jumlah_login'] += 1
                save_database(database)
                user_exists = True
            else:
                print("Login gagal. Periksa kembali username dan password.")

            # Send user existence confirmation
            if user_exists:
                conn.sendall("EXISTS".encode())
                print(f"User {username} exists")
            else:
                conn.sendall("NOT_FOUND".encode())
                print(f"User {username} not found")

        elif request_type == "list":
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
                time.sleep(0.1)
                conn.sendall(str(os.path.getsize(file_path)).encode())
                time.sleep(0.1)

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

def create_folder_if_not_exists(folder_path):
    # Periksa apakah folder sudah ada
    if not os.path.exists(folder_path):
        # Jika belum ada, buat folder
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' berhasil dibuat.")
    else:
        print(f"Folder '{folder_path}' sudah ada.")

def get_local_ip():
    # Dapatkan nama host
    host_name = socket.gethostname()
    # Dapatkan alamat IP lokal
    local_ip = socket.gethostbyname(host_name)
    return local_ip

def start_server():
    host = get_local_ip()
    port = 12345

    create_folder_if_not_exists("Upload")
    database_folder = "./Upload"

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
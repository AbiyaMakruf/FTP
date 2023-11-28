import os
import socket
import threading
import time
import json

def save_database(database):
    with open('./Json/database.json', 'w') as file:
        json.dump(database, file, indent=2)

def openJson(opsi):
        pathFile = "./Json/database.json" if opsi == "database" else "./Json/server.json"
        try:
            with open(pathFile, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print("File database.json tidak ditemukan.")

def update_statistics():
    while True:
        time.sleep(10)  # Update setiap 1 menit

        database = openJson("database")

        user_aktif = [username for username, info in database.items() if info['isLogin'] == 'True']
        most_downloads_user = max(database, key=lambda x: database[x]['jumlah_download'])
        most_uploads_user = max(database, key=lambda x: database[x]['jumlah_upload'])

        print("=============================================")
        print("Server statistics:")
        print(f"Users aktif({len(user_aktif)}): {user_aktif}")

        print(f"Mos active user for download\t: {most_downloads_user} (total download: {database[most_downloads_user]['jumlah_download']})")
        print(f"Mos active user for upload\t: {most_uploads_user} (total upload: {database[most_uploads_user]['jumlah_download']})")

def handle_client(conn, addr, database_folder, download_folder, upload_folder):
    with conn:
        # Receive request type (list, download, or upload)
        request_type = conn.recv(maxrecv).decode()

        if request_type == "login":
            # Receive username and password

            username = conn.recv(maxrecv).decode()
            password = conn.recv(maxrecv).decode()
            print(f"Login request from {addr} with username {username}")

            # Check if the user exists
            database = openJson("database")
            user_exists = False

            if (username in database) and (database[username]['password'] == password) and (database[username]['isLogin'] == "false"):
                print(f"User {username} berhasil login!")
                database[username]['jumlah_login'] += 1
                database[username]['isLogin'] = "True"
                save_database(database)
                user_exists = True

                global userAktif
                userAktif = username

            # Send user existence confirmation
            conn.sendall("EXISTS".encode()) if user_exists else conn.sendall("NOT_FOUND".encode())

        elif request_type == "logout":
            database = openJson("database")
            database[userAktif]['isLogin'] = "false"
            save_database(database)
            print(f"User {userAktif} berhasil logout!")

        elif request_type == "list":
            # Send list of files in the database folder
            file_list = "\n".join(os.listdir(database_folder))
            conn.sendall(file_list.encode())
            print(f"File list sent successfully to {addr}")

        elif request_type == "download":
            # Receive file name
            file_name = conn.recv(maxrecv).decode()
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
                    data = file.read(maxrecv)
                    while data:
                        conn.sendall(data)
                        data = file.read(maxrecv)

                print(f"File {file_name} sent successfully to {addr}")
                database = openJson("database")
                database[userAktif]['jumlah_download'] += 1
                save_database(database)

            else:
                # Send file not found notification
                conn.sendall("NOT_FOUND".encode())
                print(f"File {file_name} not found for {addr}")

        elif request_type == "upload":
            # Receive file name
            file_name = conn.recv(maxrecv).decode()
            print(f"Receiving file {file_name} from {addr}")

            # Construct the file path
            file_path = os.path.join(upload_folder, file_name)

            # Receive and save file content
            with open(file_path, 'wb') as file:
                data = conn.recv(maxrecv)
                while data:
                    file.write(data)
                    data = conn.recv(maxrecv)

            print(f"File {file_name} received successfully from {addr}")
            database = openJson("database")
            database[userAktif]['jumlah_upload'] += 1
            save_database(database)
        else:
            print(f"Invalid request type from {addr}")

def create_folder_if_not_exists(folder_path):
    # Periksa apakah folder sudah ada
    if not os.path.exists(folder_path):
        # Jika belum ada, buat folder
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' berhasil dibuat.")

def get_local_ip():
    # Dapatkan nama host
    host_name = socket.gethostname()

    # Dapatkan alamat IP lokal
    local_ip = socket.gethostbyname(host_name)
    return local_ip

def start_server():
    host = get_local_ip()
    port = 12345

    global maxrecv
    maxrecv = 8192

    create_folder_if_not_exists("Upload")
    database_folder = "./Database"
    download_folder = "./Download"
    upload_folder =  "./Upload"

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Server listening on {host}:{port}")

    update_thread = threading.Thread(target=update_statistics, args=())
    update_thread.start()

    while True:
        conn, addr = server_socket.accept()
        print(f"Connection from {addr}")

        # Create a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(conn, addr, database_folder,download_folder,upload_folder))
        client_thread.start()

if __name__ == "__main__":
    start_server()
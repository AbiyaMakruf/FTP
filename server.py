# import modul yang dibutuhkan
import os
import socket
import threading
import time
import json
from datetime import datetime

#Mengembalikan waktu saat ini
def timeStamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Menyimpan data yang baru ke dalam database
def save_database(database):
    with open('./Json/database.json', 'w') as file:
        json.dump(database, file, indent=2)

# Membuka file json berdasarkan opsi yang diinginkan
def openJson(opsi):
        pathFile = "./Json/database.json" if opsi == "database" else "./Json/server.json"
        try:
            with open(pathFile, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"{timeStamp()} File database.json tidak ditemukan.")

def update_statistics():
    # Automation statis most active user
    while True:
        time.sleep(10)  # Update setiap 1 menit

        database = openJson("database")

        # Inisiasi user aktif, most download, most upload user
        user_aktif = [username for username, info in database.items() if info['isLogin'] == 'True']
        most_downloads_user = max(database, key=lambda x: database[x]['jumlah_download'])
        most_uploads_user = max(database, key=lambda x: database[x]['jumlah_upload'])

        print("=============================================")
        print(f"Server statistics {timeStamp()}: ")
        print(f"Active Users({len(user_aktif)})\t\t\t: {user_aktif}")

        print(f"Most active user for download\t: {most_downloads_user} (total download: {database[most_downloads_user]['jumlah_download']})")
        print(f"Most active user for upload\t: {most_uploads_user} (total upload: {database[most_uploads_user]['jumlah_upload']})")
        print("=============================================")

def handle_client(conn, addr, database_folder, download_folder, upload_folder,userAktif):
    with conn:
        # Menerima request type (list, download, atau upload)
        request_type = conn.recv(maxrecv).decode()

        # pengecekan request type
        if request_type == "login":

            # Menerima username and password
            username = conn.recv(maxrecv).decode()
            password = conn.recv(maxrecv).decode()
            print(f"{timeStamp()} Login request from {addr} with username {username}")

            # Check if the user exists
            database = openJson("database")
            user_exists = False

            if (username in database) and (database[username]['password'] == password) and (database[username]['isLogin'] == "false"):

                # Update status isLogin user menjadi True
                print(f"{timeStamp()} User {username} berhasil login!")
                database[username]['jumlah_login'] += 1
                database[username]['isLogin'] = "True"
                save_database(database)
                user_exists = True

                # 
                userAktif[addr[0]] = username

            # Mengirim status login user apakah berhasil atau gagal login
            conn.sendall("EXISTS".encode()) if user_exists else conn.sendall("NOT_FOUND".encode())

        # Update status isLogin user menjadi False ketika logout
        elif request_type == "logout":
            database = openJson("database")
            database[userAktif[addr[0]]]['isLogin'] = "false"
            save_database(database)
            print(f"{timeStamp()} User {userAktif[addr[0]]} berhasil logout!")

        # Mengirim semua nama file yang terdapat di server ke client jika request type == "list"
        elif request_type == "list":
            # Send list of files in the database folder
            file_list = "\n".join(os.listdir(database_folder))
            conn.sendall(file_list.encode())
            print(f"{timeStamp()} File list sent successfully to {addr}")

        # Mengirim file jika request type nya adalah "download"
        elif request_type == "download":
            # Menerima file name dari klien
            file_name = conn.recv(maxrecv).decode()
            print(f"{timeStamp()} Receiving file {file_name} from {addr}")

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

                # Update jumlah_download user
                print(f"{timeStamp()} File {file_name} sent successfully to {addr}")
                database = openJson("database")
                database[userAktif[addr[0]]]['jumlah_download'] += 1
                save_database(database)

            else:
                # Send file not found notification
                conn.sendall("NOT_FOUND".encode())
                print(f"{timeStamp()} File {file_name} not found for {addr}")

        # Menerima file jika request type nya adalah "upload"
        elif request_type == "upload":
            # Receive file name
            file_name = conn.recv(maxrecv).decode()
            print(f"{timeStamp()} Receiving file {file_name} from {addr}")

            # Construct the file path
            file_path = os.path.join(upload_folder, file_name)

            # Receive and save file content
            with open(file_path, 'wb') as file:
                data = conn.recv(maxrecv)
                while data:
                    file.write(data)
                    data = conn.recv(maxrecv)

            # Update jumlah_upload user
            print(f"{timeStamp()} File {file_name} received successfully from {addr}")
            database = openJson("database")
            database[userAktif[addr[0]]]['jumlah_upload'] += 1
            save_database(database)
        else:
            print(f"{timeStamp()} Invalid request type from {addr}")

def create_folder_if_not_exists(folder_path):
    # Periksa apakah folder sudah ada
    if not os.path.exists(folder_path):
        # Jika belum ada, buat folder
        os.makedirs(folder_path)
        print(f"{timeStamp()} Folder '{folder_path}' berhasil dibuat.")

# Inisiasi alamat IP dan port server
def get_local_ip():
    # Dapatkan nama host
    host_name = socket.gethostname()

    # Dapatkan alamat IP lokal
    local_ip = socket.gethostbyname(host_name)
    return local_ip

def start_server():
    # inisiasi host dan port server
    host = get_local_ip()
    port = 12345

    # inisiasi maxreceive byte yang bisa diterima
    global maxrecv
    maxrecv = 8192

    # inisiasi folder yang dibutuhkan
    create_folder_if_not_exists("Upload")
    database_folder = "./Database"
    download_folder = "./Download"
    upload_folder =  "./Upload"

    # membuat koneksi TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)


    print(f"Server listening on {host}:{port}")

    # Membuat thread untuk update statistic server
    update_thread = threading.Thread(target=update_statistics, args=())
    update_thread.start()

    global userAktif
    userAktif = {} # Membuat dictionary untuk menyimpan userAktif untuk setiap thread

    # Listening menunggu koneksi dari client
    while True:
        conn, addr = server_socket.accept()
        print(f"{timeStamp()} Connection from {addr}")

        # Create a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(conn, addr, database_folder,download_folder,upload_folder,userAktif))
        client_thread.start()

if __name__ == "__main__":
    # Memulai server
    start_server()
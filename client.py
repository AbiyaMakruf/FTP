import socket
import json
import os
import time
import sys

def save_database(database):
    with open('./Json/server.json', 'w') as file:
        json.dump(database, file, indent=2)

def connect():
    #Ubah host dan port sesuai dengan host dan port server
    host = ip
    port = 12345

    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    global maxrecv
    maxrecv = 8192

def progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█'):
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix))
    sys.stdout.flush()

def unggah(file_path):
    connect()
    with client_socket:
        # Send request type (list, download, or upload)
        request_type = "upload"
        client_socket.send(request_type.encode())
        time.sleep(1)

        # Send file name
        file_name = file_path.split("/")[-1]
        client_socket.send(file_name.encode())

        # Send file content with progress bar
        file_size = os.path.getsize(file_path)
        with open(file_path, 'rb') as file:
            data = file.read(maxrecv)
            sent_bytes = 0
            while data:
                client_socket.send(data)
                sent_bytes += len(data)
                progress_bar(sent_bytes, file_size, prefix='Uploading:', suffix='Complete', length=50)
                data = file.read(maxrecv)

        print("\nFile sent successfully")

def download():
    connect()
    with client_socket:
        # Ask user for request type (list or download)
        request_type = input("Enter request type (list/download): ")
        client_socket.send(request_type.encode())

        if request_type == "list":
            # Receive and print the list of files
            file_list = client_socket.recv(maxrecv).decode()
            print("List of files in the database:")
            file_list = file_list.split("\n")
            for i in range(len(file_list)):
                print(f"[{i+1}]. {file_list[i]}")
            print()

        elif request_type == "download":
            # Send file name
            file_name = input("Enter file name: ")
            client_socket.send(file_name.encode())

            # Receive file existence confirmation
            response = client_socket.recv(maxrecv).decode()

            if response == "EXISTS":
                # Build the path to the "Download" folder
                download_folder = "./Download"

                # Receive file size
                file_size = int(client_socket.recv(maxrecv).decode())
                
                # Open a new file for writing in the "Download" folder
                with open(os.path.join(download_folder, file_name), 'wb') as file:
                    received_bytes = 0
                    while received_bytes < file_size:
                        data = client_socket.recv(maxrecv)
                        file.write(data)
                        received_bytes += len(data)
                        progress_bar(received_bytes, file_size, prefix='Downloading:', suffix='Complete', length=50)

                print("\nFile received successfully")

            elif response == "NOT_FOUND":
                print("File not found")

        else:
            print("Invalid request type. Please enter 'list' or 'download'.")

def login():
    print("="*20,"Selamat Datang","="*20)
    username = input("Username: ")
    password = input("Password: ")

    #Cek kondisi server1
    connect()
    request_type = "status"
    client_socket.send(request_type.encode())
    time.sleep(1)
    response = client_socket.recv(maxrecv).decode()
    print(response)

    #Jika server1 penuh, pindah server2
    try:
        with open('./Json/server.json', 'r') as file:
            server = json.load(file)
    except FileNotFoundError:
        print("File server.json tidak ditemukan.")
    if response == "FULL":
        print("Masuk sini")
        response = client_socket.recv(maxrecv).decode()
        server['server2']['host'] = response
        save_database(server)
        global ip
        ip = server['server2']['host']

    
    connect()
    
    with client_socket:
        # Send request type (list, download, or upload)
        request_type = "login"
        client_socket.send(request_type.encode())
        time.sleep(1)

        # Send user name
        client_socket.send(username.encode())

        # Send password
        client_socket.send(password.encode())

        response = client_socket.recv(maxrecv).decode()

        return response == "EXISTS"

def logout():
        connect()
        request_type = "logout"
        client_socket.send(request_type.encode())
        time.sleep(1)

def menu():
        print("\nLogin berhasil")
        print("="*20,"     Menu     ","="*20)

        menu = "0"
        try:
            while menu != "3":
                print("1. Upload")
                print("2. Download")
                print("3. Exit")
                menu = input("Pilih menu: ")
                if menu == "1":
                    file_path = str(input("Masukkan path file: "))
                    unggah(file_path)
                elif menu == "2":
                    download()
                elif menu == "3":
                    logout()
                    print("\nLogout berhasil")
                else:
                    print("Menu tidak tersedia\n")
        except KeyboardInterrupt:
            logout()
            print("\nProgram dihentikan")

def create_folder_if_not_exists(folder_path):
    # Periksa apakah folder sudah ada
    if not os.path.exists(folder_path):
        # Jika belum ada, buat folder
        os.makedirs(folder_path)

def chooseServer():
    print("="*20,"     Server     ","="*20)
    print("1. Localhost")
    print("2. Server")
    server = input("Pilih server: ")

    global ip
    ip = "localhost" if server == "1" else (updateServer() if server == "2" else exit())

def updateServer():
    print("="*20,"     Alamat Host     ","="*20)
    print("1. Default server")
    print("2. Update server")
    inputUser = str(input("Pilih server: "))

    try:
        with open('./Json/server.json', 'r') as file:
            server = json.load(file)
    except FileNotFoundError:
        print("File server.json tidak ditemukan.")

    if inputUser == "1":
        pass
    elif inputUser == "2":
        inputHost = input("Masukkan alamat host: ")
        server['server1']['host'] = inputHost
        save_database(server)
    else:
        print("Menu tidak tersedia")
        exit()

    return server['server1']['host']

def main():
    create_folder_if_not_exists("Database")
    create_folder_if_not_exists("Download")
    create_folder_if_not_exists("Upload")

    chooseServer()
    menu() if login() else print("Login gagal")

if __name__ == "__main__":
    main()


import socket
import os
import time
import sys

def progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█'):
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix))
    sys.stdout.flush()

def unggah(file_path):
    host = "192.168.18.109"
    port = 12345

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    with client_socket:
        # Send request type (list, download, or upload)
        request_type = "upload"
        client_socket.send(request_type.encode())
        time.sleep(0.1)

        # Send file name
        file_name = file_path.split("/")[-1]
        client_socket.send(file_name.encode())

        # Send file content with progress bar
        file_size = os.path.getsize(file_path)
        with open(file_path, 'rb') as file:
            data = file.read(1024)
            sent_bytes = 0
            while data:
                client_socket.send(data)
                sent_bytes += len(data)
                progress_bar(sent_bytes, file_size, prefix='Uploading:', suffix='Complete', length=50)
                data = file.read(1024)

        print("\nFile sent successfully")

def download():
    host = "192.168.18.109"
    port = 12345

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    with client_socket:
        # Ask user for request type (list or download)
        request_type = input("Enter request type (list/download): ")
        client_socket.send(request_type.encode())

        if request_type == "list":
            # Receive and print the list of files
            file_list = client_socket.recv(1024).decode()
            print("List of files in the database:")
            print(file_list)

        elif request_type == "download":
            # Send file name
            file_name = input("Enter file name: ")
            client_socket.send(file_name.encode())

            # Receive file existence confirmation
            response = client_socket.recv(1024).decode()

            if response == "EXISTS":
                # Build the path to the "Download" folder
                download_folder = "./Download"

                # Receive file size
                file_size = int(client_socket.recv(1024).decode())
                
                # Open a new file for writing in the "Download" folder
                with open(os.path.join(download_folder, file_name), 'wb') as file:
                    received_bytes = 0
                    while received_bytes < file_size:
                        data = client_socket.recv(1024)
                        file.write(data)
                        received_bytes += len(data)
                        progress_bar(received_bytes, file_size, prefix='Downloading:', suffix='Complete', length=50)

                print("\nFile received successfully")

            elif response == "NOT_FOUND":
                print("File not found")

        else:
            print("Invalid request type. Please enter 'list' or 'download'.")


def login():
    username = input("Username: ")
    password = input("Password: ")
    return username == "admin" and password == "admin"

def menu():
        print("Login berhasil")
        print("="*20,"Menu","="*20)

        menu = "0"
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
                exit()
            else:
                print("Menu tidak tersedia\n")

def main():
    print("="*20,"Selamat Datang","="*20)
    if login():
        menu()
    else:
        print("Login gagal")

if __name__ == "__main__":
    main()

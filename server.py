import os
import socket

def start_server():
    host = "192.168.18.109"
    port = 12345
    database_folder = "./Database"

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    print(f"Server listening on {host}:{port}")

    while True:
        conn, addr = server_socket.accept()
        print(f"Connection from {addr}")

        with conn:
            # Receive request type (list or download)
            request_type = conn.recv(1024).decode()

            if request_type == "list":
                # Send list of files in the database folder
                file_list = "\n".join(os.listdir(database_folder))
                conn.sendall(file_list.encode())
                print("File list sent successfully")

            elif request_type == "download":
                # Receive file name
                file_name = conn.recv(1024).decode()
                print(f"Receiving file: {file_name}")

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

                    print("File sent successfully")

                else:
                    # Send file not found notification
                    conn.sendall("NOT_FOUND".encode())
                    print("File not found")

if __name__ == "__main__":
    start_server()



# import socket

# def start_server():
#     host = "127.0.0.1"
#     port = 12345

#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server_socket.bind((host, port))
#     server_socket.listen(1)

#     print(f"Server listening on {host}:{port}")

#     while True:
#         conn, addr = server_socket.accept()
#         print(f"Connection from {addr}")

#         with conn:
#             # Receive file name
#             file_name = conn.recv(1024).decode()
#             print(f"Receiving file: {file_name}")

#             # Open a new file for writing
#             with open(file_name, 'wb') as file:
#                 # Receive file content
#                 data = conn.recv(1024)
#                 while data:
#                     file.write(data)
#                     data = conn.recv(1024)

#             print("File received successfully")

# if __name__ == "__main__":
#     start_server()

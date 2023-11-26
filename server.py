import socket

def start_server():
    host = "127.0.0.1"
    port = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    print(f"Server listening on {host}:{port}")

    conn, addr = server_socket.accept()
    print(f"Connection from {addr}")

    with conn:
        # Receive file name
        file_name = conn.recv(1024).decode()
        print(f"Receiving file: {file_name}")

        # Open a new file for writing
        with open(file_name, 'wb') as file:
            # Receive file content
            data = conn.recv(1024)
            while data:
                file.write(data)
                data = conn.recv(1024)

        print("File received successfully")

if __name__ == "__main__":
    start_server()

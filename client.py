import socket

def send_file(file_path):
    host = "127.0.0.1"
    port = 12345

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    with client_socket:
        # Send file name
        file_name = file_path.split("/")[-1]
        client_socket.send(file_name.encode())

        # Send file content
        with open(file_path, 'rb') as file:
            data = file.read(1024)
            while data:
                client_socket.send(data)
                data = file.read(1024)

        print("File sent successfully")

if __name__ == "__main__":
    file_path = "./Database/file.txt"  # Replace with the path to your file
    send_file(file_path)

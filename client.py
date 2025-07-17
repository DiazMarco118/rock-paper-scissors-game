import socket

HOST = 'localhost'
PORT = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

try:
    while True:
        data = client.recv(1024).decode()
        if not data:
            break
        print(data)

        if "Choose" in data:
            choice = input(">>> ").strip().lower()
            client.send(choice.encode())
except:
    print("Connection closed.")
finally:
    client.close()

import socket

HOST = 'localhost'
PORT = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((HOST, PORT))

    while True:
        data = client.recv(1024).decode()
        if not data:
            break

        print(data.strip())

        # Nếu server yêu cầu nhập (hỏi số ván, hoặc hỏi chơi tiếp, hoặc chọn kéo búa bao)
        if "Choose" in data or "Play again?" in data or "bao nhieu van" in data.lower():
            choice = input(">>> ").strip().lower()
            client.send(choice.encode())

        if "Game over" in data or "Tro choi ket thuc" in data:
            break

except ConnectionRefusedError:
    print("Khong the ket noi den server. Dam bao server dang chay.")
except Exception as e:
    print("Loi:", e)
finally:
    print("Ban da thoat khoi tro choi.")
    client.close()

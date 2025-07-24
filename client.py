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

        # Nhận diện các câu hỏi cần nhập
        if any(kw in data.lower() for kw in ["choose", "play again", "bao nhieu van", "choi tiep"]):
            choice = input(">>> ").strip().lower()
            client.send(choice.encode())

        if "game over" in data.lower() or "tro choi ket thuc" in data.lower():
            break

except ConnectionRefusedError:
    print("Khong the ket noi den server. Dam bao server dang chay.")
except Exception as e:
    print("Loi:", e)
finally:
    print("Ban da thoat khoi tro choi.")
    client.close()

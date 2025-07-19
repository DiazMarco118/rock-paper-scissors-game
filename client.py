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

        print(data)

        # Nếu server thông báo kết thúc thì thoát
        if "Game over" in data or "disconnected" in data:
            break

        # Nếu được yêu cầu nhập lựa chọn
        if "Choose" in data:
            try:
                choice = input(">>> ").strip().lower()
                client.send(choice.encode())
            except:
                print("Lỗi khi gửi dữ liệu tới server.")
                break

except ConnectionRefusedError:
    print("Không thể kết nối tới server. Đảm bảo server đang chạy.")
except Exception as e:
    print("Lỗi:", e)
finally:
    print("Bạn đã thoát khỏi trò chơi.")
    client.close()

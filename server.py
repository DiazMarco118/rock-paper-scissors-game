import socket
import threading

HOST = 'localhost'
PORT = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

valid_choices = ["rock", "paper", "scissors"]
waiting_clients = []

def determine_winner(choice1, choice2):
    if choice1 == choice2:
        return "draw"
    elif (choice1 == "rock" and choice2 == "scissors") or \
         (choice1 == "paper" and choice2 == "rock") or \
         (choice1 == "scissors" and choice2 == "paper"):
        return "player1"
    else:
        return "player2"

def handle_game(client1, client2, total_rounds):
    try:
        while True:
            client1.send(b"\nDa bat cap thanh cong. Tro choi bat dau!\n")
            client2.send(b"\nDa bat cap thanh cong. Tro choi bat dau!\n")

            win_needed = total_rounds // 2 + 1
            score1, score2 = 0, 0
            round_num = 1

            while round_num <= total_rounds:
                title = f"\n--- Van {round_num}/{total_rounds} ---\n"
                client1.send(title.encode())
                client2.send(title.encode())

                client1.send(b"Choose rock, paper, or scissors: ")
                client2.send(b"Choose rock, paper, or scissors: ")

                try:
                    client1.settimeout(30)
                    client2.settimeout(30)
                    choice1 = client1.recv(1024).decode().strip().lower()
                    choice2 = client2.recv(1024).decode().strip().lower()
                except:
                    client1.send(b"Khong nhan duoc lua chon. Ket thuc game.\n")
                    client2.send(b"Khong nhan duoc lua chon. Ket thuc game.\n")
                    return

                if choice1 not in valid_choices or choice2 not in valid_choices:
                    client1.send(b"Lua chon khong hop le. Vui long thu lai.\n")
                    client2.send(b"Lua chon khong hop le. Vui long thu lai.\n")
                    continue

                result = determine_winner(choice1, choice2)

                if result == "draw":
                    msg = f"Ca hai chon {choice1}. Hoa nhau!\n"
                elif result == "player1":
                    score1 += 1
                    msg = f"{choice1} thang {choice2} → Player 1 thang van nay!\n"
                else:
                    score2 += 1
                    msg = f"{choice2} thang {choice1} → Player 2 thang van nay!\n"

                client1.send(msg.encode())
                client2.send(msg.encode())

                print(f"[LOG] Round {round_num}: {choice1} vs {choice2} => {result}")
                round_num += 1

                if score1 == win_needed or score2 == win_needed:
                    break

            summary = f"\nTONG KET:\nPlayer 1: {score1} - Player 2: {score2}\n"
            if score1 > score2:
                summary += "Player 1 chien thang chung cuoc!\n"
            elif score2 > score1:
                summary += "Player 2 chien thang chung cuoc!\n"
            else:
                summary += "Ket qua hoa!\n"

            client1.send(summary.encode())
            client2.send(summary.encode())

            # Hỏi cả hai chơi tiếp không
            client1.send(b"\nChoi tiep? (yes/no): ")
            client2.send(b"\nChoi tiep? (yes/no): ")

            try:
                again1 = client1.recv(1024).decode().strip().lower()
                again2 = client2.recv(1024).decode().strip().lower()
            except:
                again1 = again2 = "no"

            if again1 != "yes" or again2 != "yes":
                client1.send(b"Tro choi ket thuc. Cam on da choi!\n")
                client2.send(b"Tro choi ket thuc. Cam on da choi!\n")
                break

            # Cả hai đồng ý chơi tiếp, chọn lại số ván
            client1.send(b"\nBan muon choi bao nhieu van? (1,3,5,7): ")
            client2.send(b"\nBan muon choi bao nhieu van? (1,3,5,7): ")

            try:
                round_choice1 = client1.recv(1024).decode().strip()
                round_choice2 = client2.recv(1024).decode().strip()
            except:
                break

            if round_choice1 == round_choice2 and round_choice1 in ["1", "3", "5", "7"]:
                total_rounds = int(round_choice1)
                continue
            else:
                client1.send(b"So van khong trung hoac khong hop le. Ket thuc.\n")
                client2.send(b"So van khong trung hoac khong hop le. Ket thuc.\n")
                break
    finally:
        try: client1.close()
        except: pass
        try: client2.close()
        except: pass

def wait_for_players():
    while True:
        try:
            client, addr = server.accept()
            print(f"[INFO] Client connected from {addr}")
            client.send(b"Da ket noi may chu.\n")
            client.send(b"Ban muon choi bao nhieu van? (1,3,5,7): ")

            round_choice = client.recv(1024).decode().strip()
            if round_choice not in ["1", "3", "5", "7"]:
                client.send(b"Lua chon khong hop le. Ngat ket noi.\n")
                client.close()
                continue

            client.send(f"Dang doi nguoi choi khac muon choi {round_choice} van...\n".encode())

            # Kiểm tra nếu có người chơi khác đợi sẵn
            for waiting in waiting_clients:
                if waiting[1] == round_choice:
                    other_client = waiting[0]
                    waiting_clients.remove(waiting)
                    threading.Thread(target=handle_game, args=(client, other_client, int(round_choice))).start()
                    break
            else:
                waiting_clients.append((client, round_choice))

        except Exception as e:
            print(f"[ERROR] {e}")

print(f"Server listening on {HOST}:{PORT}")

try:
    wait_for_players()
except Exception as e:
    print(f"[FATAL ERROR] {e}")

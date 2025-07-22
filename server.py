import socket
import threading

HOST = 'localhost'
PORT = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()


clients = []
valid_choices = ["rock", "paper", "scissors"]

# Danh sách chờ theo từng chế độ số ván
waiting_clients = {
    "1": [],
    "3": [],
    "5": [],
    "7": []
}

def determine_winner(choice1, choice2):
    if choice1 == choice2:
        return "draw"
    elif (choice1 == "rock" and choice2 == "scissors") or \
         (choice1 == "paper" and choice2 == "rock") or \
         (choice1 == "scissors" and choice2 == "paper"):
        return "player1"
    else:
        return "player2"

def get_choice(client, prompt, valid_list=None):
    while True:
        try:
            client.send(prompt.encode())
            choice = client.recv(1024).decode().strip().lower()
            if not valid_list or choice in valid_list:
                return choice
            else:
                client.send(b"Invalid input. Please try again.\n")
        except:
            return None

def get_round_choice(client):
    valid_rounds = ["1", "3", "5", "7"]
    return get_choice(client, "Ban muon choi bao nhieu van? (1,3,5,7): ", valid_rounds)

def handle_game(client1, client2, total_rounds):
    try:
        client1.send(b"Da bat cap thanh cong. Tro choi bat dau!\n")
        client2.send(b"Da bat cap thanh cong. Tro choi bat dau!\n")

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
                break

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

        # Tổng kết
        summary = f"\nTONG KET:\nPlayer 1: {score1} - Player 2: {score2}\n"
        if score1 > score2:
            summary += "Player 1 chien thang chung cuoc!\n"
        elif score2 > score1:
            summary += "Player 2 chien thang chung cuoc!\n"
        else:
            summary += "Ket qua hoa!\n"

        client1.send(summary.encode())
        client2.send(summary.encode())

        # Hỏi chơi tiếp không
        again1 = get_choice(client1, "\nChoi tiep? (yes/no): ", ["yes", "no"])
        again2 = get_choice(client2, "\nChoi tiep? (yes/no): ", ["yes", "no"])

        if again1 == "yes" and again2 == "yes":
            wait_for_players_single(client1)
            wait_for_players_single(client2)
        else:
            client1.send(b"Tro choi ket thuc. Cam on da choi!\n")
            client2.send(b"Tro choi ket thuc. Cam on da choi!\n")

    finally:
        try: client1.close()
        except: pass
        try: client2.close()
        except: pass

def wait_for_players_single(client):
    try:
        round_choice = get_round_choice(client)
        if not round_choice:
            client.send(b"Khong nhan duoc lua chon. Ngat ket noi.\n")
            client.close()
            return

        client.send(f"Dang doi nguoi choi khac muon choi {round_choice} van...\n".encode())

        waiting_list = waiting_clients[round_choice]
        if waiting_list:
            other_client = waiting_list.pop(0)
            threading.Thread(target=handle_game, args=(client, other_client, int(round_choice))).start()
        else:
            waiting_clients[round_choice].append(client)
    except Exception as e:
        print(f"[ERROR] {e}")
        try: client.close()
        except: pass

def wait_for_players():
    while True:
        try:
            client, addr = server.accept()
            print(f"[INFO] Client connected from {addr}")
            client.send(b"Da ket noi may chu.\n")
            threading.Thread(target=wait_for_players_single, args=(client,)).start()
        except Exception as e:
            print(f"[ERROR] {e}")
print(f"Server listening on {HOST}:{PORT}")

try:
    wait_for_players()
except Exception as e:
    print(f"[FATAL ERROR] {e}")

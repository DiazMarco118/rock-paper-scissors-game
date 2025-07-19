import socket
import threading

HOST = 'localhost'
PORT = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
valid_choices = ["rock", "paper", "scissors"]

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

def handle_game(client1, client2):
    try:
        client1.send(b"Da bat cap thanh cong. Tro choi bat dau!\n")
        client2.send(b"Da bat cap thanh cong. Tro choi bat dau!\n")

        while True:
            choice1 = get_choice(client1, "Choose rock, paper, or scissors: ", valid_choices)
            choice2 = get_choice(client2, "Choose rock, paper, or scissors: ", valid_choices)

            if not choice1 or not choice2:
                try: client1.send(b"Opponent disconnected. Game over.\n")
                except: pass
                try: client2.send(b"Opponent disconnected. Game over.\n")
                except: pass
                break

            result = determine_winner(choice1, choice2)

            if result == "draw":
                msg = f"Both chose {choice1}. It's a draw!"
                client1.send(msg.encode())
                client2.send(msg.encode())
            elif result == "player1":
                client1.send(f"You win! {choice1} beats {choice2}".encode())
                client2.send(f"You lose! {choice1} beats {choice2}".encode())
            else:
                client1.send(f"You lose! {choice2} beats {choice1}".encode())
                client2.send(f"You win! {choice2} beats {choice1}".encode())

            print(f"[LOG] Game result: {choice1} vs {choice2} => {result} wins")

            # Hỏi chơi tiếp không
            again1 = get_choice(client1, "\nPlay again? (yes/no): ", ["yes", "no"])
            again2 = get_choice(client2, "\nPlay again? (yes/no): ", ["yes", "no"])

            if again1 != "yes" or again2 != "yes":
                client1.send(b"Tro choi ket thuc. Cam on da choi!\n")
                client2.send(b"Tro choi ket thuc. Cam on da choi!\n")
                break

    finally:
        client1.close()
        client2.close()

def wait_for_players():
    while True:
        try:
            client, addr = server.accept()
            print(f"[INFO] Client connected from {addr}")
            client.send(b"Da ket noi may chu. Dang tim doi thu...\n")
            clients.append(client)

            if len(clients) >= 2:
                c1 = clients.pop(0)
                c2 = clients.pop(0)
                threading.Thread(target=handle_game, args=(c1, c2)).start()

        except Exception as e:
            print(f"[ERROR] {e}")

print(f"Server listening on {HOST}:{PORT}")
wait_for_players()

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

def get_valid_choice(client):
    while True:
        try:
            client.send(b"Your turn! Choose rock, paper, or scissors: ")
            choice = client.recv(1024).decode().strip().lower()
            if choice in valid_choices:
                return choice
            else:
                client.send(b"Invalid choice. Please try again.\n")
        except ConnectionResetError:
            print("Client disconnected during input.")
            return None

def handle_game(client1, client2):
    try:
        choice1 = get_valid_choice(client1)
        choice2 = get_valid_choice(client2)

        # Nếu 1 trong 2 người thoát giữa chừng
        if choice1 is None or choice2 is None:
            try:
                client1.send(b"Opponent disconnected. Game over.\n")
            except:
                pass
            try:
                client2.send(b"Opponent disconnected. Game over.\n")
            except:
                pass
            return

        result = determine_winner(choice1, choice2)

        # Gửi kết quả đến 2 client
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

        # In log kết quả ra terminal
        print(f"[LOG] Game result: {choice1} vs {choice2} => {result} won")

    finally:
        client1.close()
        client2.close()

def wait_for_players():
    while True:
        try:
            client, addr = server.accept()
            print(f"[INFO] Client connected from {addr}")
            clients.append(client)

            if len(clients) >= 2:
                c1 = clients.pop(0)
                c2 = clients.pop(0)
                threading.Thread(target=handle_game, args=(c1, c2)).start()
        except Exception as e:
            print(f"[ERROR] {e}")

print(f"Server listening on {HOST}:{PORT}")
wait_for_players()

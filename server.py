import socket
import threading

HOST = 'localhost'
PORT = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []

def determine_winner(choice1, choice2):
    if choice1 == choice2:
        return "draw"
    elif (choice1 == "rock" and choice2 == "scissors") or \
         (choice1 == "paper" and choice2 == "rock") or \
         (choice1 == "scissors" and choice2 == "paper"):
        return "player1"
    else:
        return "player2"

def handle_game(client1, client2):
    try:
        client1.send(b"Your turn! Choose rock, paper, or scissors: ")
        choice1 = client1.recv(1024).decode().strip().lower()

        client2.send(b"Your turn! Choose rock, paper, or scissors: ")
        choice2 = client2.recv(1024).decode().strip().lower()

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
    finally:
        client1.close()
        client2.close()

def wait_for_players():
    while True:
        client, addr = server.accept()
        print(f"Client connected from {addr}")
        clients.append(client)

        if len(clients) >= 2:
            c1 = clients.pop(0)
            c2 = clients.pop(0)
            threading.Thread(target=handle_game, args=(c1, c2)).start()

print(f"Server listening on {HOST}:{PORT}")
wait_for_players()

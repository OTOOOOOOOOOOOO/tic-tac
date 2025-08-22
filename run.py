import random
import string
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

rooms = {}

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def check_winner(board):
    win_patterns = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  
        [0, 4, 8], [2, 4, 6]              
    ]
    for pattern in win_patterns:
        a, b, c = pattern
        if board[a] != "" and board[a] == board[b] == board[c]:
            return board[a]
    if "" not in board:
        return "Draw"
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    message = None
    if request.method == "POST":
        action = request.form.get("action")
        if action == "create":
            name = request.form.get("name")
            code = generate_code()
            rooms[code] = {"board": [""]*9, "turn": "X", "players": [name], "winner": None}
            return redirect(url_for("room", code=code))
        elif action == "join":
            code = request.form.get("code")
            name = request.form.get("name")
            if code in rooms:
                if len(rooms[code]["players"]) < 2:
                    rooms[code]["players"].append(name)
                    return redirect(url_for("room", code=code))
                else:
                    message = "Room sudah penuh!"
            else:
                message = "Room tidak ditemukan!"
        elif action == "reset":
            rooms.clear()
            message = "Semua room berhasil direset!"
    return render_template("index.html",
                           message=message,
                           code=None,
                           board=None,
                           players=None,
                           turn=None,
                           winner=None,
                           all_rooms=rooms)

@app.route("/room/<code>", methods=["GET", "POST"])
def room(code):
    if code not in rooms:
        return redirect(url_for("index"))

    room = rooms[code]

    if request.method == "POST":
        action = request.form.get("action")

        if action == "reset_game":
            room["board"] = [""] * 9
            room["turn"] = "X"
            room["winner"] = None
            return redirect(url_for("room", code=code))

        if action == "delete_room":
            rooms.pop(code, None)
            return redirect(url_for("index"))

        if room["winner"] is None and action == "move":
            move = request.form.get("move")
            if move is not None:
                move = int(move)
                if room["board"][move] == "":
                    room["board"][move] = room["turn"]
                    winner = check_winner(room["board"])
                    if winner:
                        room["winner"] = winner
                    else:
                        room["turn"] = "O" if room["turn"] == "X" else "X"

                    if len(room["players"]) == 1 and room["turn"] == "O" and room["winner"] is None:
                        available = [i for i, v in enumerate(room["board"]) if v == ""]
                        if available:
                            comp_move = random.choice(available)
                            room["board"][comp_move] = "O"
                            winner = check_winner(room["board"])
                            if winner:
                                room["winner"] = winner
                            else:
                                room["turn"] = "X"

    return render_template("index.html",
                           message=None,
                           code=code,
                           board=room["board"],
                           turn=room["turn"],
                           players=room["players"],
                           winner=room["winner"],
                           all_rooms=rooms)

if __name__ == "__main__":
    app.run(debug=True)

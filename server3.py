from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Oyun durumu
secret_number = random.randint(1, 100)
players = {}  # { sid: {"name": "Yiğit", "score": 0} }

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def on_connect():
    sid = request.sid
    print(f"Bir kullanıcı bağlandı: {sid}")
    emit('message', "🟢 Yeni bir oyuncu katıldı!", broadcast=True)

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    if sid in players:
        player_name = players[sid]["name"]
        emit('message', f"🔴 {player_name} ayrıldı!", broadcast=True)
        players.pop(sid)

@socketio.on('set_name')
def set_name(name):
    sid = request.sid
    players[sid] = {"name": name, "score": 0}
    emit('message', f"👋 {name} oyuna katıldı!", broadcast=True)
    emit('update_scores', {p["name"]: p["score"] for p in players.values()}, broadcast=True)

@socketio.on('guess')
def handle_guess(guess):
    global secret_number
    sid = request.sid
    if sid not in players:
        emit('message', "⚠️ İsmini belirlemeden tahmin yapamazsın!")
        return

    player = players[sid]
    name = player["name"]

    try:
        guess = int(guess)
    except ValueError:
        emit('message', "⚠️ Lütfen geçerli bir sayı gir.")
        return

    if guess == secret_number:
        player["score"] += 1
        emit('message', f"🎉 {name} doğru tahmin etti! Sayı {secret_number} idi!", broadcast=True)
        secret_number = random.randint(1, 100)
        emit('message', "🔢 Yeni bir sayı seçildi! Tahmin etmeye devam edin!", broadcast=True)
    elif guess < secret_number:
        emit('message', f"{name}: 🔼 Daha büyük!")
    else:
        emit('message', f"{name}: 🔽 Daha küçük!")

    players[sid] = player
    emit('update_scores', {p["name"]: p["score"] for p in players.values()}, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)

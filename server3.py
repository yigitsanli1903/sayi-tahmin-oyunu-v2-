from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random
import eventlet

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
    print("Bir kullanıcı bağlandı:", request.sid)
    emit('message', "🟢 Yeni bir oyuncu katıldı!")

@socketio.on('disconnect')
def on_disconnect():
    print("Bir kullanıcı ayrıldı")
    emit('message', "🔴 Bir oyuncu ayrıldı!", broadcast=True)

@socketio.on('set_name')
def set_name(name):
    players[request.sid] = {"name": name, "score": 0}
    emit('message', f"👋 {name} oyuna katıldı!", broadcast=True)
    emit('update_scores', players, broadcast=True)

@socketio.on('guess')
def handle_guess(guess):
    global secret_number
    sid = request.sid
    player = players.get(sid, {"name": "Bilinmeyen", "score": 0})
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
    emit('update_scores', players, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=10000)

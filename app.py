from flask import Flask, render_template
from flask_socketio import SocketIO
from routes import bp as routes_bp
from realtime import init_realtime
from train_simulation import init_train_simulation

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

app.register_blueprint(routes_bp)

@app.route('/')
def index():
    return render_template('index.html')

init_realtime(socketio)
init_train_simulation(socketio)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5001)
from flask import Flask, render_template
from flask_socketio import SocketIO
from routes import bp as routes_bp
from realtime import init_realtime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Register REST routes
app.register_blueprint(routes_bp)

# Home route for frontend
@app.route('/')
def index():
    return render_template('index.html')

# Register real-time handlers
init_realtime(socketio)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)
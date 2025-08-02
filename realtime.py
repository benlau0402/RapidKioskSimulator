from flask_socketio import emit
from flask import Blueprint

realtime_bp = Blueprint('realtime', __name__)

def init_realtime(socketio):

    @socketio.on('train_update')
    def handle_train_update(data):
        emit('train_update', data, broadcast=True)
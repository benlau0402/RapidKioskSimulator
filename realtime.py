from flask_socketio import emit
import sqlite3

def init_realtime(socketio):
    @socketio.on('train_update')
    def handle_train_update(data):
        emit('train_update', data, broadcast=True)
        # Insert or update in arrivals table
        update_arrivals(data)

def update_arrivals(data):
    conn = sqlite3.connect('metro.db')
    c = conn.cursor()
    # Clear past arrivals for this train at this platform
    c.execute("DELETE FROM arrivals WHERE train_id=? AND station_id=?", (data['train_id'], data['origin_id']))
    # Insert new arrival (simulate arrival in X mins, here 3-15 random mins)
    c.execute(
        "INSERT INTO arrivals (station_id, train_id, minutes, destination_id) VALUES (?, ?, ?, ?)",
        (data['origin_id'], data['train_id'], int((data.get('minutes') or 3)), data['destination_id'])
    )
    conn.commit()
    conn.close()
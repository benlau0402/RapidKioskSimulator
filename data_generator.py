import time
import random
import socketio

# If server is on another host, change the URL accordingly
sio = socketio.Client()
sio.connect('http://localhost:5000')

# Example: station IDs from your DB (replace with your actual list)
station_ids = [1, 2, 3, 4, 5]  # Update after inspecting your station list

def simulate_train(train_id):
    while True:
        station_id = random.choice(station_ids)
        data = {
            'train_id': train_id,
            'station_id': station_id,
            'timestamp': time.time()
        }
        sio.emit('train_update', data)
        time.sleep(random.randint(2, 5))

if __name__ == "__main__":
    for train_id in range(1, 5):  # Four trains for the FF theme!
        simulate_train(train_id)
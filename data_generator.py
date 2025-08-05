import time
import random
import socketio
import pandas as pd

# Read station list for random selection
fare_df = pd.read_csv('data/Fare.csv')
stations = fare_df['Unnamed: 0'].tolist()
station_id_map = {name: idx+1 for idx, name in enumerate(stations)}

sio = socketio.Client()
sio.connect('http://localhost:5001', transports=['websocket'])

def simulate_train(train_id):
    while True:
        # Randomly pick origin and destination (not same)
        origin_name, dest_name = random.sample(stations, 2)
        data = {
            'train_id': train_id,
            'origin_id': station_id_map[origin_name],
            'destination_id': station_id_map[dest_name],
            'origin_name': origin_name,
            'destination_name': dest_name,
            'timestamp': time.time()
        }
        sio.emit('train_update', data)
        time.sleep(random.randint(2, 5))

if __name__ == "__main__":
    for train_id in range(1, 5):
        simulate_train(train_id)
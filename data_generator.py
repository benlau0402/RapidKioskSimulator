import time
import random
import socketio
import pandas as pd
import threading

fare_df = pd.read_csv('data/Fare.csv')
stations = fare_df[fare_df.columns[0]].tolist()
station_id_map = {name: idx+1 for idx, name in enumerate(stations)}

sio = socketio.Client()
sio.connect('http://localhost:5001', transports=['websocket'])

def simulate_train(train_id):
    while True:
        origin_name, dest_name = random.sample(stations, 2)
        minutes = random.choice([3, 7, 12, 15])
        data = {
            'train_id': train_id,
            'origin_id': station_id_map[origin_name],
            'destination_id': station_id_map[dest_name],
            'origin_name': origin_name,
            'destination_name': dest_name,
            'timestamp': time.time(),
            'minutes': minutes
        }
        sio.emit('train_update', data)
        time.sleep(random.randint(3, 7))

if __name__ == "__main__":
    threads = []
    for train_id in range(1, 5):
        t = threading.Thread(target=simulate_train, args=(train_id,))
        t.daemon = True
        t.start()
        threads.append(t)
    while True:
        time.sleep(100)
import sqlite3
import pandas as pd

def build_station_list(matrix_file):
    df = pd.read_csv(matrix_file)
    row_index_col = df.columns[0]  # Always use the first column as station name
    stations = df[row_index_col].tolist()
    return stations

def init_db():
    fare_csv = 'data/Fare.csv'
    time_csv = 'data/Time.csv'
    route_csv = 'data/Route.csv'

    # Get station list and assign IDs
    stations = build_station_list(fare_csv)
    station_id_map = {name: idx+1 for idx, name in enumerate(stations)}

    conn = sqlite3.connect('metro.db')
    c = conn.cursor()

    # Drop and create tables
    c.execute('DROP TABLE IF EXISTS stations')
    c.execute('DROP TABLE IF EXISTS fares')
    c.execute('DROP TABLE IF EXISTS times')
    c.execute('DROP TABLE IF EXISTS routes')

    c.execute('''
        CREATE TABLE stations (
            station_id INTEGER PRIMARY KEY,
            name TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE fares (
            origin_id INTEGER,
            destination_id INTEGER,
            price REAL
        )
    ''')
    c.execute('''
        CREATE TABLE times (
            origin_id INTEGER,
            destination_id INTEGER,
            minutes INTEGER
        )
    ''')
    c.execute('''
        CREATE TABLE routes (
            origin_id INTEGER,
            destination_id INTEGER,
            route_code TEXT
        )
    ''')

    # Insert stations
    for name, id_ in station_id_map.items():
        c.execute('INSERT INTO stations (station_id, name) VALUES (?, ?)', (id_, name))

    # Insert fares
    fare_df = pd.read_csv(fare_csv)
    fare_values = fare_df.values
    for i, row in enumerate(fare_values):
        origin = row[0]
        for j, price in enumerate(row[1:], start=1):
            dest = fare_df.columns[j]
            c.execute('INSERT INTO fares (origin_id, destination_id, price) VALUES (?, ?, ?)',
                      (station_id_map[origin], station_id_map[dest], price))

    # Insert times
    time_df = pd.read_csv(time_csv)
    time_values = time_df.values
    for i, row in enumerate(time_values):
        origin = row[0]
        for j, minutes in enumerate(row[1:], start=1):
            dest = time_df.columns[j]
            c.execute('INSERT INTO times (origin_id, destination_id, minutes) VALUES (?, ?, ?)',
                      (station_id_map[origin], station_id_map[dest], minutes))

    # Insert routes
    route_df = pd.read_csv(route_csv)
    route_values = route_df.values
    for i, row in enumerate(route_values):
        origin = row[0]
        for j, code in enumerate(row[1:], start=1):
            dest = route_df.columns[j]
            c.execute('INSERT INTO routes (origin_id, destination_id, route_code) VALUES (?, ?, ?)',
                      (station_id_map[origin], station_id_map[dest], code))

    conn.commit()
    conn.close()
    print("Database initialized!")

if __name__ == '__main__':
    init_db()
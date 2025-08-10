import sqlite3
import pandas as pd

def build_station_list(matrix_file):
    df = pd.read_csv(matrix_file)
    row_index_col = df.columns[0]
    stations = df[row_index_col].tolist()
    return stations

def init_db():
    fare_csv = 'data/Fare.csv'
    time_csv = 'data/Time.csv'
    route_csv = 'data/Route.csv'

    stations = build_station_list(fare_csv)
    station_id_map = {name: idx+1 for idx, name in enumerate(stations)}

    conn = sqlite3.connect('metro.db')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS stations')
    c.execute('DROP TABLE IF EXISTS fares')
    c.execute('DROP TABLE IF EXISTS times')
    c.execute('DROP TABLE IF EXISTS routes')
    c.execute('DROP TABLE IF EXISTS arrivals')
    c.execute('DROP TABLE IF EXISTS trains')
    c.execute('''
        CREATE TABLE stations (station_id INTEGER PRIMARY KEY, name TEXT)
    ''')
    c.execute('''
        CREATE TABLE fares (origin_id INTEGER, destination_id INTEGER, price REAL)
    ''')
    c.execute('''
        CREATE TABLE times (origin_id INTEGER, destination_id INTEGER, minutes INTEGER)
    ''')
    c.execute('''
        CREATE TABLE routes (origin_id INTEGER, destination_id INTEGER, route_code TEXT)
    ''')
    c.execute('''
        CREATE TABLE arrivals (
            station_id INTEGER,
            train_id INTEGER,
            minutes INTEGER,
            destination_id INTEGER,
            arrival_timestamp REAL
        )
    ''')
    c.execute('''
        CREATE TABLE trains (
            train_id INTEGER PRIMARY KEY,
            line TEXT,
            direction TEXT,
            current_station_id INTEGER,
            next_station_id INTEGER
        )
    ''')

    for name, id_ in station_id_map.items():
        c.execute('INSERT INTO stations (station_id, name) VALUES (?, ?)', (id_, name))

    # For fares, times, routes
    for df_file, tbl, col in [
        (fare_csv, 'fares', 'price'),
        (time_csv, 'times', 'minutes'),
        (route_csv, 'routes', 'route_code')
    ]:
        df = pd.read_csv(df_file)
        row_index_col = df.columns[0]
        for i, row in enumerate(df.values):
            origin = row[0]  # The first column is always the origin name
            for j, value in enumerate(row[1:], start=1):  # Skip the first column (origin), start from dest columns
                dest = df.columns[j]
                c.execute(
                    f'INSERT INTO {tbl} (origin_id, destination_id, {col}) VALUES (?, ?, ?)',
                    (station_id_map[origin], station_id_map[dest], value)
                )

    conn.commit()
    conn.close()
    print("Database initialized!")

if __name__ == '__main__':
    init_db()
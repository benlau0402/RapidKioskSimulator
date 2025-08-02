import sqlite3
import pandas as pd

def init_db():
    # Update these to match your CSV file paths
    station_csv = 'Route.csv'
    fare_csv = 'Fare.csv'

    conn = sqlite3.connect('metro.db')
    c = conn.cursor()

    c.execute('DROP TABLE IF EXISTS stations')
    c.execute('DROP TABLE IF EXISTS fares')

    c.execute('''
        CREATE TABLE stations (
            station_id INTEGER PRIMARY KEY,
            name TEXT,
            latitude REAL,
            longitude REAL
        )
    ''')

    c.execute('''
        CREATE TABLE fares (
            origin_id INTEGER,
            destination_id INTEGER,
            price REAL,
            PRIMARY KEY(origin_id, destination_id)
        )
    ''')

    # Load stations
    stations = pd.read_csv(station_csv)
    stations = stations.rename(columns={'id': 'station_id'})  # If your file uses 'id'
    stations[['station_id', 'name', 'latitude', 'longitude']].to_sql('stations', conn, if_exists='append', index=False)

    # Load fares
    fares = pd.read_csv(fare_csv)
    fares[['origin_id', 'destination_id', 'price']].to_sql('fares', conn, if_exists='append', index=False)

    c.execute('CREATE INDEX IF NOT EXISTS idx_origin ON fares (origin_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_dest ON fares (destination_id)')

    conn.commit()
    conn.close()
    print("Database initialized!")

if __name__ == "__main__":
    init_db()
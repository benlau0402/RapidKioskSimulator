from flask import Blueprint, jsonify, request
import sqlite3

bp = Blueprint('routes', __name__)

def get_db():
    return sqlite3.connect('metro.db')

@bp.route('/stations')
def get_stations():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT station_id, name FROM stations ORDER BY station_id")
        stations = [{'station_id': row[0], 'name': row[1]} for row in c.fetchall()]
    return jsonify(stations)

@bp.route('/fare')
def get_fare():
    origin = request.args.get('from')
    dest = request.args.get('to')
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT price FROM fares WHERE origin_id=? AND destination_id=?", (origin, dest))
        row = c.fetchone()
    if row:
        return jsonify({'price': row[0]})
    else:
        return jsonify({'error': 'No fare found'}), 404

@bp.route('/time')
def get_time():
    origin = request.args.get('from')
    dest = request.args.get('to')
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT minutes FROM times WHERE origin_id=? AND destination_id=?", (origin, dest))
        row = c.fetchone()
    if row:
        return jsonify({'minutes': row[0]})
    else:
        return jsonify({'error': 'No time found'}), 404

@bp.route('/routecode')
def get_routecode():
    origin = request.args.get('from')
    dest = request.args.get('to')
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT route_code FROM routes WHERE origin_id=? AND destination_id=?", (origin, dest))
        row = c.fetchone()
    if row:
        return jsonify({'route_code': row[0]})
    else:
        return jsonify({'error': 'No route found'}), 404

@bp.route('/arrivals')
def get_arrivals():
    import time
    station_id = request.args.get('station_id')
    current_time = time.time()
    
    with get_db() as conn:
        c = conn.cursor()
        
        # Get arrivals with destination station names and timestamps
        c.execute(
            """SELECT arrivals.arrival_timestamp, stations.name as destination, arrivals.train_id
               FROM arrivals 
               JOIN stations ON arrivals.destination_id = stations.station_id 
               WHERE arrivals.station_id=? AND arrivals.arrival_timestamp > ?
               ORDER BY arrivals.arrival_timestamp""", (station_id, current_time))
        
        arrivals_data = []
        for row in c.fetchall():
            arrival_timestamp, destination, train_id = row
            # Calculate remaining time in real-time
            remaining_seconds = arrival_timestamp - current_time
            
            # Only include trains arriving in the future (more than 5 seconds away)
            if remaining_seconds > 5:
                # Convert to integer seconds to avoid decimals
                total_seconds_int = int(remaining_seconds)
                total_minutes = total_seconds_int // 60
                seconds_part = total_seconds_int % 60
                
                arrivals_data.append({
                    'minutes': total_minutes,
                    'seconds': seconds_part,
                    'total_seconds': total_seconds_int,  # Use integer seconds
                    'destination': destination,
                    'train_id': train_id
                })
    
    return jsonify(arrivals_data)

@bp.route('/station_info')
def get_station_info():
    station_id = int(request.args.get('station_id'))
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT name FROM stations WHERE station_id=?", (station_id,))
        result = c.fetchone()
        
        if result:
            station_name = result[0]
            # Determine station type based on station ID ranges
            # LRT: stations 1-37 (Gombak to Putra Heights)
            # MRT: stations 38-68 (Sungai Buloh to Kajang)
            is_lrt = 1 <= station_id <= 37
            is_mrt = 38 <= station_id <= 68
            
            return jsonify({
                'name': station_name,
                'is_lrt': is_lrt,
                'is_mrt': is_mrt
            })
        else:
            return jsonify({'error': 'Station not found'}), 404
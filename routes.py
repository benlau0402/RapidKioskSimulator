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
    station_id = request.args.get('station_id')
    with get_db() as conn:
        c = conn.cursor()
        c.execute(
            "SELECT minutes, stations.name FROM arrivals "
            "JOIN stations ON arrivals.destination_id = stations.station_id "
            "WHERE arrivals.station_id=? ORDER BY minutes", (station_id,))
        arrivals = [{'minutes': row[0], 'destination': row[1]} for row in c.fetchall()]
    return jsonify(arrivals)
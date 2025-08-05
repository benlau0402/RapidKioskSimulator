from flask import Blueprint, jsonify, request
import sqlite3

bp = Blueprint('routes', __name__)

@bp.route('/stations')
def get_stations():
    with sqlite3.connect('metro.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM stations")
        stations = [dict(zip([column[0] for column in c.description], row)) for row in c.fetchall()]
    return jsonify(stations)

@bp.route('/fare')
def get_fare():
    origin = int(request.args.get('from'))
    dest = int(request.args.get('to'))
    with sqlite3.connect('metro.db') as conn:
        c = conn.cursor()
        c.execute("SELECT price FROM fares WHERE origin_id=? AND destination_id=?", (origin, dest))
        row = c.fetchone()
    if row:
        return jsonify({'price': row[0]})
    else:
        return jsonify({'error': 'No fare found'}), 404

@bp.route('/time')
def get_time():
    origin = int(request.args.get('from'))
    dest = int(request.args.get('to'))
    with sqlite3.connect('metro.db') as conn:
        c = conn.cursor()
        c.execute("SELECT minutes FROM times WHERE origin_id=? AND destination_id=?", (origin, dest))
        row = c.fetchone()
    if row:
        return jsonify({'minutes': row[0]})
    else:
        return jsonify({'error': 'No time found'}), 404

@bp.route('/routecode')
def get_routecode():
    origin = int(request.args.get('from'))
    dest = int(request.args.get('to'))
    with sqlite3.connect('metro.db') as conn:
        c = conn.cursor()
        c.execute("SELECT route_code FROM routes WHERE origin_id=? AND destination_id=?", (origin, dest))
        row = c.fetchone()
    if row:
        return jsonify({'route_code': row[0]})
    else:
        return jsonify({'error': 'No route found'}), 404
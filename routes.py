from flask import Blueprint, jsonify, request
import sqlite3
import networkx as nx
import pandas as pd

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
    origin = request.args.get('from')
    dest = request.args.get('to')
    with sqlite3.connect('metro.db') as conn:
        c = conn.cursor()
        c.execute("SELECT price FROM fares WHERE origin_id=? AND destination_id=?", (origin, dest))
        row = c.fetchone()
    if row:
        return jsonify({'price': row[0]})
    else:
        return jsonify({'error': 'No fare found'}), 404

@bp.route('/route')
def get_route():
    origin = int(request.args.get('from'))
    dest = int(request.args.get('to'))
    with sqlite3.connect('metro.db') as conn:
        fares = pd.read_sql("SELECT * FROM fares", conn)
    G = nx.DiGraph()
    for _, row in fares.iterrows():
        G.add_edge(row['origin_id'], row['destination_id'], weight=row['price'])
    try:
        path = nx.shortest_path(G, source=origin, target=dest, weight='weight')
        price = nx.shortest_path_length(G, source=origin, target=dest, weight='weight')
        return jsonify({'route': path, 'total_price': price})
    except nx.NetworkXNoPath:
        return jsonify({'error': 'No route found'}), 404
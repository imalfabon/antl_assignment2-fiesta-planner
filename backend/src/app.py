import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request, g
from flask_cors import CORS
from db import (
    init_db,
    get_clients, get_client, add_client, update_client, delete_client,
    get_catalog_items, get_catalog_item, add_catalog_item, update_catalog_item, delete_catalog_item,
    get_catering_packages, get_catering_package, add_catering_package, update_catering_package, delete_catering_package,
    get_events, get_event, add_event, update_event, delete_event,
    get_event_line_items, add_line_item, delete_line_item,
    analytics_top_items, analytics_revenue_by_type, analytics_seasonal_demand, analytics_margins,
)

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# DB path
db_path = os.path.join(os.path.dirname(__file__), '..', 'events.db')

# Create schema + seed on startup
_startup_db = init_db(db_path, seed=True)
_startup_db.close()


def get_db():
    """Get a per-request DB connection."""
    if 'db' not in g:
        g.db = init_db(db_path, seed=False)
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.route('/api/health', methods=['GET'])
def health():
    from datetime import datetime
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})


# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------

@app.route('/api/clients', methods=['GET'])
def list_clients():
    return jsonify(get_clients(get_db()))

@app.route('/api/clients/<int:client_id>', methods=['GET'])
def read_client(client_id):
    client = get_client(get_db(), client_id)
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    return jsonify(client)

@app.route('/api/clients', methods=['POST'])
def create_client():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    new_id = add_client(get_db(), data['name'], data.get('phone'), data.get('email'), data.get('notes'))
    return jsonify({'id': new_id}), 201

@app.route('/api/clients/<int:client_id>', methods=['PUT'])
def edit_client(client_id):
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    update_client(get_db(), client_id, data['name'], data.get('phone'), data.get('email'), data.get('notes'))
    return jsonify({'success': True})

@app.route('/api/clients/<int:client_id>', methods=['DELETE'])
def remove_client(client_id):
    delete_client(get_db(), client_id)
    return jsonify({'success': True})


# ---------------------------------------------------------------------------
# Catalog Items
# ---------------------------------------------------------------------------

@app.route('/api/catalog', methods=['GET'])
def list_catalog():
    category = request.args.get('category')
    return jsonify(get_catalog_items(get_db(), category))

@app.route('/api/catalog/<int:item_id>', methods=['GET'])
def read_catalog_item(item_id):
    item = get_catalog_item(get_db(), item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    return jsonify(item)

@app.route('/api/catalog', methods=['POST'])
def create_catalog_item():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('category'):
        return jsonify({'error': 'Name and category are required'}), 400
    new_id = add_catalog_item(
        get_db(), data['name'], data['category'], data.get('description'),
        data.get('unit_cost', 0), data.get('unit_price', 0),
        data.get('stock_qty', 0), data.get('image_url')
    )
    return jsonify({'id': new_id}), 201

@app.route('/api/catalog/<int:item_id>', methods=['PUT'])
def edit_catalog_item(item_id):
    data = request.get_json()
    if not data or not data.get('name') or not data.get('category'):
        return jsonify({'error': 'Name and category are required'}), 400
    update_catalog_item(
        get_db(), item_id, data['name'], data['category'], data.get('description'),
        data.get('unit_cost', 0), data.get('unit_price', 0),
        data.get('stock_qty', 0), data.get('image_url')
    )
    return jsonify({'success': True})

@app.route('/api/catalog/<int:item_id>', methods=['DELETE'])
def remove_catalog_item(item_id):
    delete_catalog_item(get_db(), item_id)
    return jsonify({'success': True})


# ---------------------------------------------------------------------------
# Catering Packages
# ---------------------------------------------------------------------------

@app.route('/api/catering', methods=['GET'])
def list_catering():
    pkg_type = request.args.get('type')
    return jsonify(get_catering_packages(get_db(), pkg_type))

@app.route('/api/catering/<int:pkg_id>', methods=['GET'])
def read_catering(pkg_id):
    pkg = get_catering_package(get_db(), pkg_id)
    if not pkg:
        return jsonify({'error': 'Package not found'}), 404
    return jsonify(pkg)

@app.route('/api/catering', methods=['POST'])
def create_catering():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('type'):
        return jsonify({'error': 'Name and type are required'}), 400
    new_id = add_catering_package(
        get_db(), data['name'], data['type'], data.get('description'),
        data.get('price_per_person', 0), data.get('min_guests', 1)
    )
    return jsonify({'id': new_id}), 201

@app.route('/api/catering/<int:pkg_id>', methods=['PUT'])
def edit_catering(pkg_id):
    data = request.get_json()
    if not data or not data.get('name') or not data.get('type'):
        return jsonify({'error': 'Name and type are required'}), 400
    update_catering_package(
        get_db(), pkg_id, data['name'], data['type'], data.get('description'),
        data.get('price_per_person', 0), data.get('min_guests', 1)
    )
    return jsonify({'success': True})

@app.route('/api/catering/<int:pkg_id>', methods=['DELETE'])
def remove_catering(pkg_id):
    delete_catering_package(get_db(), pkg_id)
    return jsonify({'success': True})


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

@app.route('/api/events', methods=['GET'])
def list_events():
    return jsonify(get_events(get_db()))

@app.route('/api/events/<int:event_id>', methods=['GET'])
def read_event(event_id):
    event = get_event(get_db(), event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    event['line_items'] = get_event_line_items(get_db(), event_id)
    return jsonify(event)

@app.route('/api/events', methods=['POST'])
def create_event():
    data = request.get_json()
    if not data or not data.get('client_id') or not data.get('event_type') or not data.get('event_date'):
        return jsonify({'error': 'client_id, event_type, and event_date are required'}), 400
    new_id = add_event(
        get_db(), data['client_id'], data['event_type'], data['event_date'],
        data.get('venue'), data.get('guest_count', 0),
        data.get('status', 'draft'), data.get('special_requirements')
    )
    return jsonify({'id': new_id}), 201

@app.route('/api/events/<int:event_id>', methods=['PUT'])
def edit_event(event_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    update_event(
        get_db(), event_id, data['client_id'], data['event_type'], data['event_date'],
        data.get('venue'), data.get('guest_count', 0),
        data.get('status', 'draft'), data.get('special_requirements')
    )
    return jsonify({'success': True})

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def remove_event(event_id):
    delete_event(get_db(), event_id)
    return jsonify({'success': True})


# ---------------------------------------------------------------------------
# Event Line Items
# ---------------------------------------------------------------------------

@app.route('/api/events/<int:event_id>/items', methods=['GET'])
def list_event_items(event_id):
    return jsonify(get_event_line_items(get_db(), event_id))

@app.route('/api/events/<int:event_id>/items', methods=['POST'])
def create_event_item(event_id):
    data = request.get_json()
    if not data or not data.get('item_type'):
        return jsonify({'error': 'item_type is required'}), 400
    new_id = add_line_item(
        get_db(), event_id, data['item_type'],
        data.get('catalog_item_id'), data.get('catering_package_id'),
        data.get('quantity', 1), data.get('unit_price', 0)
    )
    return jsonify({'id': new_id}), 201

@app.route('/api/events/<int:event_id>/items/<int:item_id>', methods=['DELETE'])
def remove_event_item(event_id, item_id):
    delete_line_item(get_db(), item_id)
    return jsonify({'success': True})


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

@app.route('/api/analytics/top-items', methods=['GET'])
def api_top_items():
    limit = request.args.get('limit', 10, type=int)
    return jsonify(analytics_top_items(get_db(), limit))

@app.route('/api/analytics/revenue', methods=['GET'])
def api_revenue():
    return jsonify(analytics_revenue_by_type(get_db()))

@app.route('/api/analytics/seasonal', methods=['GET'])
def api_seasonal():
    return jsonify(analytics_seasonal_demand(get_db()))

@app.route('/api/analytics/margins', methods=['GET'])
def api_margins():
    return jsonify(analytics_margins(get_db()))


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"\n{'='*50}")
    print(f"Starting Flask on http://localhost:{port}")
    print(f"{'='*50}\n")
    app.run(host='localhost', port=port, debug=True)

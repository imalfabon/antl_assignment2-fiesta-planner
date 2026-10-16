"""
Database module for Event Planner system.
SQLiteDB class + schema + CRUD functions.
"""

import sqlite3
import os


class SQLiteDB:
    def __init__(self, db_file):
        try:
            self.connection = sqlite3.connect(db_file, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # return dicts instead of tuples
            self.connection.execute("PRAGMA foreign_keys = ON")
        except sqlite3.Error as error:
            print("Error:", error)

    def execute_query(self, qry, params=()):
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute(qry, params)
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as error:
            print("Error:", error)
            return None

    def executemany_query(self, qry, params=()):
        try:
            self.cursor = self.connection.cursor()
            self.cursor.executemany(qry, params)
            self.connection.commit()
        except sqlite3.Error as error:
            print("Error:", error)

    def fetch_all(self, qry, params=()):
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute(qry, params)
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as error:
            print("Error:", error)
            return []

    def fetch_one(self, qry, params=()):
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute(qry, params)
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as error:
            print("Error:", error)
            return None

    def close(self):
        self.connection.close()


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

def create_schema(db):
    """Create all tables for the event planner system."""

    db.execute_query('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    ''')

    db.execute_query('''
        CREATE TABLE IF NOT EXISTS catalog_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            unit_cost REAL NOT NULL DEFAULT 0,
            unit_price REAL NOT NULL DEFAULT 0,
            stock_qty INTEGER NOT NULL DEFAULT 0,
            image_url TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    ''')

    db.execute_query('''
        CREATE TABLE IF NOT EXISTS catering_packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            description TEXT,
            price_per_person REAL NOT NULL DEFAULT 0,
            min_guests INTEGER NOT NULL DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now'))
        )
    ''')

    db.execute_query('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            event_date TEXT NOT NULL,
            venue TEXT,
            guest_count INTEGER DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'draft',
            special_requirements TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    ''')

    db.execute_query('''
        CREATE TABLE IF NOT EXISTS event_line_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            item_type TEXT NOT NULL,
            catalog_item_id INTEGER,
            catering_package_id INTEGER,
            quantity INTEGER NOT NULL DEFAULT 1,
            unit_price_at_booking REAL NOT NULL DEFAULT 0,
            subtotal REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
            FOREIGN KEY (catalog_item_id) REFERENCES catalog_items(id),
            FOREIGN KEY (catering_package_id) REFERENCES catering_packages(id)
        )
    ''')


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

def seed_demo_data(db):
    """Insert demo data for development/testing."""

    # Clients
    clients = [
        ('María García', '916-555-0101', 'maria.garcia@email.com', 'Preferred client'),
        ('Roberto Hernández', '916-555-0102', 'roberto.h@email.com', None),
        ('Ana López', '916-555-0103', 'ana.lopez@email.com', 'Referred by María'),
        ('Carlos Mendoza', '916-555-0104', 'carlos.m@email.com', None),
        ('Sofía Ramírez', '916-555-0105', 'sofia.r@email.com', 'VIP client'),
    ]
    db.executemany_query(
        'INSERT OR IGNORE INTO clients (name, phone, email, notes) VALUES (?, ?, ?, ?)',
        clients
    )

    # Catalog items
    catalog = [
        # Floral
        ('Rosa Centerpiece', 'floral', 'Red and white roses arrangement', 15.00, 35.00, 50, None),
        ('Lily Bouquet', 'floral', 'Mixed lily bouquet for tables', 12.00, 28.00, 30, None),
        ('Orchid Arrangement', 'floral', 'Premium orchid centerpiece', 25.00, 55.00, 20, None),
        # Balloon
        ('Balloon Arch', 'balloon', 'Full arch in custom colors', 40.00, 120.00, 10, None),
        ('Balloon Centerpiece', 'balloon', 'Table balloon arrangement', 8.00, 22.00, 40, None),
        ('Number Balloon Set', 'balloon', 'Foil number balloons (XV, age)', 10.00, 30.00, 25, None),
        # Centerpiece
        ('Crystal Vase Set', 'centerpiece', 'Crystal vase with LED base', 18.00, 42.00, 35, None),
        ('Candelabra Gold', 'centerpiece', '5-arm gold candelabra', 22.00, 50.00, 20, None),
        # Linen
        ('Satin Tablecloth', 'linen', '120" round satin tablecloth', 8.00, 18.00, 100, None),
        ('Organza Runner', 'linen', 'Sheer organza table runner', 3.00, 8.00, 150, None),
        ('Napkin Set (10)', 'linen', 'Matching cloth napkins', 5.00, 12.00, 80, None),
        # Silverware
        ('Premium Silverware Set', 'silverware', '5-piece setting per guest', 4.00, 10.00, 200, None),
        ('Gold Charger Plate', 'silverware', 'Decorative charger plate', 3.00, 7.00, 150, None),
        # Chair cover
        ('Spandex Chair Cover', 'chair_cover', 'Stretch fit, multiple colors', 2.50, 6.00, 300, None),
        ('Chair Sash - Organza', 'chair_cover', 'Organza bow sash', 1.00, 3.00, 400, None),
    ]
    db.executemany_query(
        '''INSERT OR IGNORE INTO catalog_items
           (name, category, description, unit_cost, unit_price, stock_qty, image_url)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        catalog
    )

    # Catering packages
    catering = [
        ('Taco Bar', 'food', 'Carne asada, carnitas, chicken — rice, beans, salsas', 18.00, 30),
        ('Buffet Mexicano', 'food', 'Enchiladas, mole, tamales, rice, beans, tortillas', 25.00, 50),
        ('Premium Dinner', 'food', 'Plated 3-course: soup, entrée, dessert', 45.00, 20),
        ('Kids Menu', 'food', 'Chicken nuggets, mac & cheese, juice', 10.00, 10),
        ('Agua Fresca Bar', 'beverage', 'Horchata, jamaica, tamarindo, limón', 5.00, 20),
        ('Open Bar Basic', 'beverage', 'Beer, wine, soft drinks', 15.00, 30),
        ('Open Bar Premium', 'beverage', 'Full spirits, cocktails, beer, wine', 28.00, 30),
    ]
    db.executemany_query(
        '''INSERT OR IGNORE INTO catering_packages
           (name, type, description, price_per_person, min_guests)
           VALUES (?, ?, ?, ?, ?)''',
        catering
    )

    # Events
    events = [
        (1, 'quinceañera', '2026-12-15', 'Salón Las Palmas', 150, 'confirmed', 'Tema: mariposas'),
        (2, 'wedding', '2027-02-14', 'Jardín Real', 200, 'confirmed', 'Ceremonia civil + religiosa'),
        (3, 'birthday', '2026-11-20', 'Casa del cliente', 40, 'draft', 'Cumpleaños 50'),
        (4, 'quinceañera', '2027-03-08', 'Hacienda Morelos', 180, 'draft', 'Color rosa y dorado'),
        (5, 'special', '2026-12-24', 'Salón Fiesta', 100, 'confirmed', 'Posada navideña empresarial'),
    ]
    db.executemany_query(
        '''INSERT OR IGNORE INTO events
           (client_id, event_type, event_date, venue, guest_count, status, special_requirements)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        events
    )

    # Event line items
    line_items = [
        # Event 1 — Quinceañera (María)
        (1, 'catalog', 1, None, 15, 35.00, 525.00),    # Rosa Centerpiece x15
        (1, 'catalog', 4, None, 1, 120.00, 120.00),     # Balloon Arch x1
        (1, 'catalog', 6, None, 1, 30.00, 30.00),       # Number Balloon Set x1
        (1, 'catalog', 9, None, 15, 18.00, 270.00),     # Satin Tablecloth x15
        (1, 'catalog', 14, None, 150, 6.00, 900.00),    # Spandex Chair Cover x150
        (1, 'catalog', 12, None, 150, 10.00, 1500.00),  # Premium Silverware x150
        (1, 'catering', None, 2, 150, 25.00, 3750.00),  # Buffet Mexicano x150
        (1, 'catering', None, 5, 150, 5.00, 750.00),    # Agua Fresca Bar x150
        # Event 2 — Wedding (Roberto)
        (2, 'catalog', 3, None, 20, 55.00, 1100.00),    # Orchid Arrangement x20
        (2, 'catalog', 8, None, 20, 50.00, 1000.00),    # Candelabra Gold x20
        (2, 'catalog', 9, None, 20, 18.00, 360.00),     # Satin Tablecloth x20
        (2, 'catalog', 10, None, 20, 8.00, 160.00),     # Organza Runner x20
        (2, 'catalog', 14, None, 200, 6.00, 1200.00),   # Spandex Chair Cover x200
        (2, 'catalog', 15, None, 200, 3.00, 600.00),    # Chair Sash x200
        (2, 'catalog', 12, None, 200, 10.00, 2000.00),  # Premium Silverware x200
        (2, 'catalog', 13, None, 200, 7.00, 1400.00),   # Gold Charger x200
        (2, 'catering', None, 3, 200, 45.00, 9000.00),  # Premium Dinner x200
        (2, 'catering', None, 7, 200, 28.00, 5600.00),  # Open Bar Premium x200
        # Event 3 — Birthday (Ana)
        (3, 'catalog', 5, None, 4, 22.00, 88.00),       # Balloon Centerpiece x4
        (3, 'catalog', 9, None, 4, 18.00, 72.00),       # Satin Tablecloth x4
        (3, 'catering', None, 1, 40, 18.00, 720.00),    # Taco Bar x40
        (3, 'catering', None, 6, 40, 15.00, 600.00),    # Open Bar Basic x40
    ]
    db.executemany_query(
        '''INSERT OR IGNORE INTO event_line_items
           (event_id, item_type, catalog_item_id, catering_package_id,
            quantity, unit_price_at_booking, subtotal)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        line_items
    )

    print("Demo data seeded.")


# ---------------------------------------------------------------------------
# CRUD — Clients
# ---------------------------------------------------------------------------

def get_clients(db):
    return db.fetch_all('SELECT * FROM clients ORDER BY name')

def get_client(db, client_id):
    return db.fetch_one('SELECT * FROM clients WHERE id = ?', (client_id,))

def add_client(db, name, phone=None, email=None, notes=None):
    return db.execute_query(
        'INSERT INTO clients (name, phone, email, notes) VALUES (?, ?, ?, ?)',
        (name, phone, email, notes)
    )

def update_client(db, client_id, name, phone=None, email=None, notes=None):
    return db.execute_query(
        'UPDATE clients SET name=?, phone=?, email=?, notes=? WHERE id=?',
        (name, phone, email, notes, client_id)
    )

def delete_client(db, client_id):
    return db.execute_query('DELETE FROM clients WHERE id = ?', (client_id,))


# ---------------------------------------------------------------------------
# CRUD — Catalog Items
# ---------------------------------------------------------------------------

def get_catalog_items(db, category=None):
    if category:
        return db.fetch_all(
            'SELECT * FROM catalog_items WHERE category = ? ORDER BY name',
            (category,)
        )
    return db.fetch_all('SELECT * FROM catalog_items ORDER BY category, name')

def get_catalog_item(db, item_id):
    return db.fetch_one('SELECT * FROM catalog_items WHERE id = ?', (item_id,))

def add_catalog_item(db, name, category, description=None, unit_cost=0, unit_price=0, stock_qty=0, image_url=None):
    return db.execute_query(
        '''INSERT INTO catalog_items (name, category, description, unit_cost, unit_price, stock_qty, image_url)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (name, category, description, unit_cost, unit_price, stock_qty, image_url)
    )

def update_catalog_item(db, item_id, name, category, description=None, unit_cost=0, unit_price=0, stock_qty=0, image_url=None):
    return db.execute_query(
        '''UPDATE catalog_items SET name=?, category=?, description=?, unit_cost=?, unit_price=?, stock_qty=?, image_url=?
           WHERE id=?''',
        (name, category, description, unit_cost, unit_price, stock_qty, image_url, item_id)
    )

def delete_catalog_item(db, item_id):
    return db.execute_query('DELETE FROM catalog_items WHERE id = ?', (item_id,))


# ---------------------------------------------------------------------------
# CRUD — Catering Packages
# ---------------------------------------------------------------------------

def get_catering_packages(db, pkg_type=None):
    if pkg_type:
        return db.fetch_all(
            'SELECT * FROM catering_packages WHERE type = ? ORDER BY name',
            (pkg_type,)
        )
    return db.fetch_all('SELECT * FROM catering_packages ORDER BY type, name')

def get_catering_package(db, pkg_id):
    return db.fetch_one('SELECT * FROM catering_packages WHERE id = ?', (pkg_id,))

def add_catering_package(db, name, pkg_type, description=None, price_per_person=0, min_guests=1):
    return db.execute_query(
        '''INSERT INTO catering_packages (name, type, description, price_per_person, min_guests)
           VALUES (?, ?, ?, ?, ?)''',
        (name, pkg_type, description, price_per_person, min_guests)
    )

def update_catering_package(db, pkg_id, name, pkg_type, description=None, price_per_person=0, min_guests=1):
    return db.execute_query(
        '''UPDATE catering_packages SET name=?, type=?, description=?, price_per_person=?, min_guests=?
           WHERE id=?''',
        (name, pkg_type, description, price_per_person, min_guests, pkg_id)
    )

def delete_catering_package(db, pkg_id):
    return db.execute_query('DELETE FROM catering_packages WHERE id = ?', (pkg_id,))


# ---------------------------------------------------------------------------
# CRUD — Events
# ---------------------------------------------------------------------------

def get_events(db):
    return db.fetch_all('''
        SELECT e.*, c.name as client_name
        FROM events e
        JOIN clients c ON e.client_id = c.id
        ORDER BY e.event_date
    ''')

def get_event(db, event_id):
    return db.fetch_one('''
        SELECT e.*, c.name as client_name
        FROM events e
        JOIN clients c ON e.client_id = c.id
        WHERE e.id = ?
    ''', (event_id,))

def add_event(db, client_id, event_type, event_date, venue=None, guest_count=0, status='draft', special_requirements=None):
    return db.execute_query(
        '''INSERT INTO events (client_id, event_type, event_date, venue, guest_count, status, special_requirements)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (client_id, event_type, event_date, venue, guest_count, status, special_requirements)
    )

def update_event(db, event_id, client_id, event_type, event_date, venue=None, guest_count=0, status='draft', special_requirements=None):
    return db.execute_query(
        '''UPDATE events SET client_id=?, event_type=?, event_date=?, venue=?, guest_count=?, status=?, special_requirements=?
           WHERE id=?''',
        (client_id, event_type, event_date, venue, guest_count, status, special_requirements, event_id)
    )

def delete_event(db, event_id):
    return db.execute_query('DELETE FROM events WHERE id = ?', (event_id,))


# ---------------------------------------------------------------------------
# CRUD — Event Line Items
# ---------------------------------------------------------------------------

def get_event_line_items(db, event_id):
    return db.fetch_all('''
        SELECT eli.*,
               ci.name as catalog_item_name, ci.category as catalog_item_category,
               cp.name as catering_package_name, cp.type as catering_package_type
        FROM event_line_items eli
        LEFT JOIN catalog_items ci ON eli.catalog_item_id = ci.id
        LEFT JOIN catering_packages cp ON eli.catering_package_id = cp.id
        WHERE eli.event_id = ?
        ORDER BY eli.id
    ''', (event_id,))

def add_line_item(db, event_id, item_type, catalog_item_id=None, catering_package_id=None, quantity=1, unit_price=0):
    subtotal = quantity * unit_price
    return db.execute_query(
        '''INSERT INTO event_line_items
           (event_id, item_type, catalog_item_id, catering_package_id, quantity, unit_price_at_booking, subtotal)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (event_id, item_type, catalog_item_id, catering_package_id, quantity, unit_price, subtotal)
    )

def delete_line_item(db, line_item_id):
    return db.execute_query('DELETE FROM event_line_items WHERE id = ?', (line_item_id,))


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

def analytics_top_items(db, limit=10):
    """Most requested catalog items by total quantity."""
    return db.fetch_all('''
        SELECT ci.name, ci.category, SUM(eli.quantity) as total_qty, COUNT(DISTINCT eli.event_id) as event_count
        FROM event_line_items eli
        JOIN catalog_items ci ON eli.catalog_item_id = ci.id
        WHERE eli.item_type = 'catalog'
        GROUP BY eli.catalog_item_id
        ORDER BY total_qty DESC
        LIMIT ?
    ''', (limit,))

def analytics_revenue_by_type(db):
    """Total revenue by event type."""
    return db.fetch_all('''
        SELECT e.event_type, COUNT(DISTINCT e.id) as event_count, SUM(eli.subtotal) as total_revenue
        FROM events e
        JOIN event_line_items eli ON e.id = eli.event_id
        GROUP BY e.event_type
        ORDER BY total_revenue DESC
    ''')

def analytics_seasonal_demand(db):
    """Event count and revenue by month."""
    return db.fetch_all('''
        SELECT strftime('%m', e.event_date) as month,
               COUNT(DISTINCT e.id) as event_count,
               SUM(eli.subtotal) as total_revenue
        FROM events e
        JOIN event_line_items eli ON e.id = eli.event_id
        GROUP BY month
        ORDER BY month
    ''')

def analytics_margins(db):
    """Cost vs price margin per event."""
    return db.fetch_all('''
        SELECT e.id, e.event_type, e.event_date, c.name as client_name,
               SUM(eli.subtotal) as total_revenue,
               SUM(CASE
                   WHEN eli.item_type = 'catalog' THEN ci.unit_cost * eli.quantity
                   ELSE eli.subtotal * 0.6
               END) as total_cost
        FROM events e
        JOIN clients c ON e.client_id = c.id
        JOIN event_line_items eli ON e.id = eli.event_id
        LEFT JOIN catalog_items ci ON eli.catalog_item_id = ci.id
        GROUP BY e.id
        ORDER BY e.event_date
    ''')


# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------

def init_db(db_path='events.db', seed=False):
    """Initialize the database. Returns a SQLiteDB instance."""
    db = SQLiteDB(db_path)
    create_schema(db)
    if seed:
        # Only seed if tables are empty
        count = db.fetch_one('SELECT COUNT(*) as cnt FROM clients')
        if count and count['cnt'] == 0:
            seed_demo_data(db)
    return db

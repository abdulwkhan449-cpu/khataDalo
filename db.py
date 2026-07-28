"""
KhataDalo POS - Database Layer
Handles SQLite connection, schema creation, seed data, and EOD backup.
"""

import sqlite3
import os
import shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "khatadalo.db")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")


def get_connection():
    """Return a new SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'cashier',      -- admin / cashier
    full_name TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_en TEXT NOT NULL,
    name_ur TEXT,
    default_tax_percent REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode TEXT UNIQUE,
    name_en TEXT NOT NULL,
    name_ur TEXT,
    category_id INTEGER,
    cost_price REAL DEFAULT 0,
    sale_price REAL DEFAULT 0,
    stock_qty REAL DEFAULT 0,
    min_stock_alert REAL DEFAULT 5,
    unit TEXT DEFAULT 'pcs',
    tax_percent REAL DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    address TEXT,
    credit_limit REAL DEFAULT 0,
    balance REAL DEFAULT 0,           -- positive = customer owes shop
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    address TEXT,
    balance REAL DEFAULT 0,           -- positive = shop owes supplier
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER,
    invoice_no TEXT,
    total_amount REAL DEFAULT 0,
    paid_amount REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

CREATE TABLE IF NOT EXISTS purchase_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    purchase_id INTEGER NOT NULL,
    product_id INTEGER,
    qty REAL DEFAULT 0,
    cost_price REAL DEFAULT 0,
    FOREIGN KEY (purchase_id) REFERENCES purchases(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS sales_header (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_no TEXT UNIQUE,
    customer_id INTEGER,
    subtotal REAL DEFAULT 0,
    discount REAL DEFAULT 0,
    tax REAL DEFAULT 0,
    total REAL DEFAULT 0,
    payment_method TEXT DEFAULT 'cash',   -- cash / easypaisa / jazzcash / bank / udhar
    paid_amount REAL DEFAULT 0,
    status TEXT DEFAULT 'completed',      -- completed / void / refund
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS sales_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL,
    product_id INTEGER,
    barcode TEXT,
    item_name TEXT,
    qty REAL DEFAULT 1,
    rate REAL DEFAULT 0,
    discount_percent REAL DEFAULT 0,
    total REAL DEFAULT 0,
    FOREIGN KEY (sale_id) REFERENCES sales_header(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS khata_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    sale_id INTEGER,
    type TEXT NOT NULL,                -- 'debit' (bill on udhar) / 'credit' (payment received)
    amount REAL NOT NULL,
    note TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (sale_id) REFERENCES sales_header(id)
);
"""

SEED_CATEGORIES = [
    ("General", "عام", 0),
    ("Grocery", "گروسری", 0),
    ("Sanitary", "سینیٹری", 0),
    ("Electric", "الیکٹرک", 0),
]


def init_db():
    """Create tables if they do not exist and seed minimal defaults."""
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript(SCHEMA)

    cur.execute("SELECT COUNT(*) AS c FROM categories")
    if cur.fetchone()["c"] == 0:
        cur.executemany(
            "INSERT INTO categories (name_en, name_ur, default_tax_percent) VALUES (?, ?, ?)",
            SEED_CATEGORIES,
        )

    cur.execute("SELECT COUNT(*) AS c FROM users")
    if cur.fetchone()["c"] == 0:
        # Default admin login: admin / admin123  (change after first login)
        cur.execute(
            "INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
            ("admin", "admin123", "admin", "Administrator"),
        )

    conn.commit()
    conn.close()


def backup_database():
    """Copy the live DB into /backups with a date-stamp. Returns backup file path."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dest = os.path.join(BACKUP_DIR, f"khatadalo_backup_{stamp}.db")
    if os.path.exists(DB_PATH):
        shutil.copy2(DB_PATH, dest)
    return dest


def next_invoice_no(cur):
    """Generate a simple incrementing invoice number like INV-000123."""
    cur.execute("SELECT COUNT(*) AS c FROM sales_header")
    n = cur.fetchone()["c"] + 1
    return f"INV-{n:06d}"

import sqlite3
from werkzeug.security import generate_password_hash

DB = 'expenses.db'

schema = '''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT
);

CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    is_recurring INTEGER DEFAULT 0,
    recurring_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS recurring_expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    frequency TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT NOT NULL,
    UNIQUE(user_id, name)
);

CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    amount REAL NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id),
    UNIQUE(user_id, month)
);
'''

sample_users = [
    ('demo', generate_password_hash('demo123'), 'demo@example.com'),
    ('alice', generate_password_hash('alice123'), 'alice@example.com')
]

sample_data = [
    (1, '2026-01-01', 12.5, 'Food', 'Lunch', 0, None),
    (1, '2026-01-02', 40.0, 'Transport', 'Monthly pass', 0, None),
    (1, '2026-01-03', 25.0, 'Entertainment', 'Movie', 0, None),
    (1, '2026-01-04', 120.0, 'Shopping', 'Clothes', 0, None),
    (2, '2026-01-05', 15.0, 'Food', 'Coffee', 0, None)
]

sample_categories = [
    (1, 'Food'), (1, 'Transport'), (1, 'Entertainment'), (1, 'Shopping'),
    (2, 'Food'), (2, 'Utilities'), (2, 'Entertainment')
]

sample_budgets = [
    (1, '2026-01', 2750.0),
    (1, '2026-02', 2500.0),
    (2, '2026-01', 3000.0)
]

sample_recurring = [
    (1, 50.0, 'Transport', 'Monthly gym', 'monthly', '2026-01-01', None),
    (2, 30.0, 'Utilities', 'Streaming service', 'monthly', '2026-01-01', None)
]

conn = sqlite3.connect(DB)
c = conn.cursor()
c.executescript(schema)
conn.commit()

# insert users if empty
c.execute('SELECT COUNT(*) FROM users')
count = c.fetchone()[0]
if count == 0:
    c.executemany('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', sample_users)
    conn.commit()
    print('Inserted sample users')

# insert expenses
c.execute('SELECT COUNT(*) FROM expenses')
if c.fetchone()[0] == 0:
    c.executemany('INSERT INTO expenses (user_id, date, amount, category, description, is_recurring, recurring_id) VALUES (?, ?, ?, ?, ?, ?, ?)', sample_data)
    conn.commit()
    print('Inserted sample expenses')

# insert categories
c.execute('SELECT COUNT(*) FROM categories')
if c.fetchone()[0] == 0:
    c.executemany('INSERT OR IGNORE INTO categories (user_id, name) VALUES (?, ?)', sample_categories)
    conn.commit()
    print('Inserted sample categories')

# insert budgets
c.execute('SELECT COUNT(*) FROM budgets')
if c.fetchone()[0] == 0:
    c.executemany('INSERT INTO budgets (user_id, month, amount) VALUES (?, ?, ?)', sample_budgets)
    conn.commit()
    print('Inserted sample budgets')

# insert recurring
c.execute('SELECT COUNT(*) FROM recurring_expenses')
if c.fetchone()[0] == 0:
    c.executemany('INSERT INTO recurring_expenses (user_id, amount, category, description, frequency, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?, ?)', sample_recurring)
    conn.commit()
    print('Inserted sample recurring expenses')

conn.close()
print('Initialized', DB)

from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
from datetime import datetime, timedelta
import csv
from io import StringIO
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = 'expenses.db'

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user['id'], user['username'], user['email'])
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            login_user(User(user['id'], user['username'], user['email']))
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email', '')
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                        (username, generate_password_hash(password), email))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('signup.html', error='Username already exists')
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    month = request.args.get('month')
    year = request.args.get('year')
    conn = get_db_connection()
    q = 'SELECT * FROM expenses WHERE user_id = ?'
    params = [current_user.id]
    if month:
        q += ' AND substr(date,1,7) = ?'
        params.append(month)
    elif year:
        q += ' AND substr(date,1,4) = ?'
        params.append(year)
    q += ' ORDER BY date DESC'
    expenses = conn.execute(q, params).fetchall()
    total = conn.execute('SELECT COALESCE(SUM(amount),0) as total FROM expenses WHERE user_id = ?', (current_user.id,)).fetchone()['total']
    y = year or datetime.now().strftime('%Y')
    ytd = conn.execute("SELECT COALESCE(SUM(amount),0) as ytd FROM expenses WHERE user_id = ? AND substr(date,1,4)=?", (current_user.id, y)).fetchone()['ytd']
    ma = conn.execute("SELECT AVG(month_total) as avg FROM (SELECT SUM(amount) as month_total FROM expenses WHERE user_id = ? AND substr(date,1,4)=? GROUP BY substr(date,1,7))", (current_user.id, y)).fetchone()['avg'] or 0
    budget_amount = None
    if month:
        b = conn.execute('SELECT amount FROM budgets WHERE user_id = ? AND month = ?', (current_user.id, month)).fetchone()
        budget_amount = b['amount'] if b else None
    categories = conn.execute('SELECT name FROM categories WHERE user_id = ? ORDER BY name', (current_user.id,)).fetchall()
    conn.close()
    return render_template('index.html', expenses=expenses, total=total, ytd=ytd, monthly_avg=ma, budget_amount=budget_amount, categories=categories, filter_month=month, filter_year=year)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    conn = get_db_connection()
    if request.method == 'POST':
        date = request.form['date'] or datetime.now().strftime('%Y-%m-%d')
        amount = float(request.form['amount'])
        category = request.form['category']
        description = request.form.get('description', '')
        conn.execute('INSERT INTO expenses (user_id, date, amount, category, description) VALUES (?, ?, ?, ?, ?)',
                     (current_user.id, date, amount, category, description))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    categories = conn.execute('SELECT name FROM categories WHERE user_id = ? ORDER BY name', (current_user.id,)).fetchall()
    conn.close()
    return render_template('add_expense.html', categories=categories)

@app.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    conn = get_db_connection()
    expense = conn.execute('SELECT * FROM expenses WHERE id = ? AND user_id = ?', (expense_id, current_user.id)).fetchone()
    if not expense:
        conn.close()
        return redirect(url_for('index'))
    if request.method == 'POST':
        date = request.form['date']
        amount = float(request.form['amount'])
        category = request.form['category']
        description = request.form.get('description', '')
        conn.execute('UPDATE expenses SET date = ?, amount = ?, category = ?, description = ? WHERE id = ?',
                     (date, amount, category, description, expense_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    categories = conn.execute('SELECT name FROM categories WHERE user_id = ? ORDER BY name', (current_user.id,)).fetchall()
    conn.close()
    return render_template('edit_expense.html', expense=expense, categories=categories)

@app.route('/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM expenses WHERE id = ? AND user_id = ?', (expense_id, current_user.id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/report')
@login_required
def report():
    return render_template('report.html')

@app.route('/recurring', methods=['GET', 'POST'])
@login_required
def recurring():
    conn = get_db_connection()
    if request.method == 'POST':
        amount = float(request.form['amount'])
        category = request.form['category']
        description = request.form.get('description', '')
        frequency = request.form['frequency']
        start_date = request.form['start_date']
        end_date = request.form.get('end_date')
        conn.execute('INSERT INTO recurring_expenses (user_id, amount, category, description, frequency, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (current_user.id, amount, category, description, frequency, start_date, end_date))
        conn.commit()
        conn.close()
        return redirect(url_for('recurring'))
    recs = conn.execute('SELECT * FROM recurring_expenses WHERE user_id = ? ORDER BY start_date DESC', (current_user.id,)).fetchall()
    categories = conn.execute('SELECT name FROM categories WHERE user_id = ? ORDER BY name', (current_user.id,)).fetchall()
    conn.close()
    return render_template('recurring.html', recurring=recs, categories=categories)


@app.route('/export')
@login_required
def export_csv():
    month = request.args.get('month')
    year = request.args.get('year')
    conn = get_db_connection()
    q = 'SELECT date, category, description, amount FROM expenses WHERE user_id = ?'
    params = [current_user.id]
    if month:
        q += ' AND substr(date,1,7) = ?'
        params.append(month)
    elif year:
        q += ' AND substr(date,1,4) = ?'
        params.append(year)
    q += ' ORDER BY date DESC'
    rows = conn.execute(q, params).fetchall()
    conn.close()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['date', 'category', 'description', 'amount'])
    for r in rows:
        cw.writerow([r['date'], r['category'], r['description'], r['amount']])
    return app.response_class(si.getvalue(), mimetype='text/csv', headers={'Content-Disposition':'attachment;filename=expenses.csv'})


@app.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name'].strip()
        if name:
            conn.execute('INSERT OR IGNORE INTO categories (user_id, name) VALUES (?, ?)', (current_user.id, name))
            conn.commit()
        conn.close()
        return redirect(url_for('categories'))
    cats = conn.execute('SELECT * FROM categories WHERE user_id = ? ORDER BY name', (current_user.id,)).fetchall()
    conn.close()
    return render_template('categories.html', categories=cats)


@app.route('/budgets', methods=['GET', 'POST'])
@login_required
def budgets():
    conn = get_db_connection()
    if request.method == 'POST':
        month = request.form['month']
        amount = float(request.form['amount'] or 0)
        if month:
            conn.execute('INSERT INTO budgets (user_id, month, amount) VALUES (?, ?, ?) ON CONFLICT(user_id, month) DO UPDATE SET amount=excluded.amount', 
                        (current_user.id, month, amount))
            conn.commit()
        conn.close()
        return redirect(url_for('budgets'))
    b = conn.execute('SELECT * FROM budgets WHERE user_id = ? ORDER BY month DESC', (current_user.id,)).fetchall()
    conn.close()
    return render_template('budgets.html', budgets=b)

@app.route('/api/summary')
@login_required
def api_summary():
    conn = get_db_connection()
    rows = conn.execute('SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY category', (current_user.id,)).fetchall()
    conn.close()
    data = {row['category']: row['total'] for row in rows}
    return jsonify(data)

@app.route('/api/monthly')
@login_required
def api_monthly():
    year = request.args.get('year')
    conn = get_db_connection()
    if year:
        rows = conn.execute("SELECT substr(date,1,7) as month, SUM(amount) as total FROM expenses WHERE user_id = ? AND substr(date,1,4)=? GROUP BY month ORDER BY month ASC", (current_user.id, year)).fetchall()
    else:
        rows = conn.execute("SELECT substr(date,1,7) as month, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY month ORDER BY month ASC", (current_user.id,)).fetchall()
    conn.close()
    out = [{'month': r['month'], 'total': r['total']} for r in rows]
    return jsonify(out)

@app.route('/api/budget-vs-actual')
@login_required
def api_budget_vs_actual():
    conn = get_db_connection()
    today = datetime.now()
    months = [(today - timedelta(days=30*i)).strftime('%Y-%m') for i in range(6)]
    months.reverse()
    data = []
    for m in months:
        budget_row = conn.execute('SELECT COALESCE(amount, 0) as amt FROM budgets WHERE user_id = ? AND month = ?', (current_user.id, m)).fetchone()
        actual_row = conn.execute("SELECT COALESCE(SUM(amount), 0) as amt FROM expenses WHERE user_id = ? AND substr(date,1,7) = ?", (current_user.id, m)).fetchone()
        data.append({
            'month': m,
            'budget': budget_row['amt'] if budget_row else 0,
            'actual': actual_row['amt'] if actual_row else 0
        })
    conn.close()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)

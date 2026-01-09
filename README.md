# Personal Spending Tracker & Budget Manager

Simple Flask + SQLite app to track daily expenses, view category breakdowns, and manage entries.

Quick start

1. Create a venv and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Initialize the database (creates `expenses.db` and sample data):

```bash
python init_db.py
```

3. Run the app:

```bash
python app.py
```

4. Open http://127.0.0.1:5000 in your browser.

Files

- [app.py](app.py) - Flask application with CRUD routes and API endpoint.
- [init_db.py](init_db.py) - Creates the SQLite schema and inserts sample data.
- [templates](templates) - Jinja2 HTML templates.
- [static/css/style.css](static/css/style.css) - Minimal styling.

Notes

- Chart.js is loaded from a CDN in the reports view. Replace with local copy if required.
- For production, disable `debug=True` and use a proper WSGI server.
Additional features added

- Categories management page at `/categories` to add and view categories.
- Monthly budgets at `/budgets` to set budget per month (format `YYYY-MM`).
- Dashboard filters: filter by month or year and export visible entries as CSV (`/export`).
- Reports: pie chart (category breakdown) and monthly trend line powered by `/api/monthly`.

Run notes

- To reset or initialize DB with sample categories/budgets run:

```bash
python init_db.py
```

Then start the app as before.

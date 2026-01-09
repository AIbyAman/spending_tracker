# Personal Spending Tracker & Budget Manager

A full-stack web application for tracking daily expenses, managing budgets, and analyzing spending patterns with intuitive dashboards and real-time visualizations.

## ✨ Features

- **Multi-User Authentication** - Secure login/signup with password hashing using Werkzeug
- **Expense Tracking** - Add, edit, delete expenses with categories and descriptions
- **Budget Management** - Set monthly budgets and track actual spending vs budget
- **Recurring Expenses** - Automate recurring payments (daily, weekly, monthly, yearly) with optional end dates
- **Financial Analytics** - 3 interactive Chart.js visualizations:
  - Category breakdown (pie chart)
  - Monthly spending trend (line chart)
  - Budget vs actual comparison (bar chart)
- **CSV Export** - Download expense data with date/year filtering
- **Responsive Design** - Modern UI with Bootstrap 5, gradient navbar, and Font Awesome icons
- **User Isolation** - Each user's data is completely private with database-level FK constraints
- **RESTful APIs** - JSON endpoints for dashboard data and chart feeds (`/api/summary`, `/api/monthly`, `/api/budget-vs-actual`)

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Flask, Flask-Login |
| **Database** | SQLite3 |
| **Frontend** | HTML5, CSS3, Bootstrap 5.3.0 |
| **Charting** | Chart.js 3.9.1 |
| **Icons** | Font Awesome 6.4.0 |
| **Security** | Werkzeug password hashing |

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd spending_tracker
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python init_db.py
```
This creates `expenses.db` with schema and sample data for 2 demo users.

### 3. Run Application
```bash
python app.py
```
Visit `http://localhost:5000` in your browser.

## 📝 Demo Credentials

| Username | Password | Purpose |
|----------|----------|---------|
| demo | demo123 | Demo user with sample data |
| alice | alice123 | Additional demo user |

## 📁 Project Structure

```
spending_tracker/
├── app.py                          # Main Flask app (350+ LOC)
│   ├── Authentication routes (login, signup, logout)
│   ├── CRUD operations (add, edit, delete expenses)
│   ├── Budget management endpoints
│   ├── Recurring expenses handler
│   └── RESTful API endpoints
├── init_db.py                      # Database initialization & schema
│   ├── 5-table schema with FK relationships
│   └── Sample multi-user data insertion
├── requirements.txt                # Python dependencies
├── expenses.db                     # SQLite database (created after init_db.py)
├── README.md                       # This file
├── .gitignore                      # Git ignore rules
├── templates/                      # Jinja2 HTML templates
│   ├── base.html                  # Master layout with sticky navbar
│   ├── index.html                 # Dashboard with stats & expense table
│   ├── login.html                 # Login form
│   ├── signup.html                # Registration form
│   ├── add_expense.html           # Add expense form
│   ├── edit_expense.html          # Edit expense form
│   ├── recurring.html             # Recurring expenses management
│   ├── report.html                # Analytics with Chart.js
│   ├── categories.html            # Category management
│   └── budgets.html               # Budget management
└── static/
    └── css/style.css              # Custom styling (gradients, shadows, responsive)
```

## 📊 Database Schema

### Users Table
- `id` (PRIMARY KEY)
- `username` (UNIQUE)
- `password` (hashed)
- `email`

### Expenses Table
- `id` (PRIMARY KEY)
- `user_id` (FK → users)
- `date`
- `amount`
- `category`
- `description`

### Categories Table
- `id` (PRIMARY KEY)
- `user_id` (FK → users)
- `name` (UNIQUE per user)

### Budgets Table
- `id` (PRIMARY KEY)
- `user_id` (FK → users)
- `month` (YYYY-MM format)
- `amount`

### Recurring Expenses Table
- `id` (PRIMARY KEY)
- `user_id` (FK → users)
- `amount`
- `category`
- `description`
- `frequency` (daily, weekly, monthly, yearly)
- `start_date`
- `end_date` (optional)

## 💡 Usage Guide

### Adding Expenses
1. Click "Add Expense" on dashboard
2. Enter date, amount, category, and optional description
3. Submit to save

### Setting Budgets
1. Go to "Budgets" section
2. Select month (YYYY-MM format) and budget amount
3. Track actual spending vs budget on dashboard

### Creating Recurring Expenses
1. Go to "Recurring" section
2. Enter amount, category, frequency, and dates
3. System tracks recurring charges

### Viewing Reports
1. Click "Reports" to see 3 visualizations
2. Pie chart: spending by category
3. Line chart: monthly spending trend
4. Bar chart: budget vs actual spending

### Exporting Data
1. Filter expenses by month/year on dashboard
2. Click "Export CSV"
3. Download formatted expense data

## 🔐 Security Features

- ✅ Password hashing with Werkzeug
- ✅ Per-user data isolation with database FK constraints
- ✅ Login required for all protected routes (@login_required)
- ✅ Session-based authentication with Flask-Login
- ✅ CSRF protection via Flask session management

### Production Deployment Notes

Before deploying to production:

```python
# Set SECRET_KEY from environment variable
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-key')

# Disable debug mode
app.config['DEBUG'] = False

# Use production WSGI server (Gunicorn, uWSGI, etc.)
# gunicorn -w 4 app:app
```

## 📈 API Endpoints

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/summary` | GET | Yes | Category-wise spending totals (JSON) |
| `/api/monthly` | GET | Yes | Monthly spending trend (JSON) |
| `/api/budget-vs-actual` | GET | Yes | Last 6 months budget vs actual (JSON) |

All APIs return JSON and require user authentication.

## 🔧 Configuration

Environment variables (optional):
```bash
export SECRET_KEY="your-secret-key-here"
export FLASK_ENV="production"  # or "development"
```

## ⚠️ Limitations & Future Enhancements

- No email notifications for budget alerts (future feature)
- No multi-currency support (current: single currency)
- No data import from CSV (future feature)
- No mobile app (web-only)

## 🤝 Contributing

Feel free to fork and submit pull requests for improvements.

## 📄 License

MIT License - feel free to use this project for personal or commercial purposes.

## 📞 Support

For issues or questions, please open a GitHub issue or contact the maintainer.

---

**Last Updated:** January 2026

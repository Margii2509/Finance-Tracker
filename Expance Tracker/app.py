from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import func, extract
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    transactions = db.relationship('Transaction', backref='category', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

# Initialize database and create default categories
def init_db():
    with app.app_context():
        db.create_all()
        
        # Add default categories if they don't exist
        if Category.query.count() == 0:
            default_categories = [
                Category(name='Salary', type='income'),
                Category(name='Freelance', type='income'),
                Category(name='Investment', type='income'),
                Category(name='Food', type='expense'),
                Category(name='Transport', type='expense'),
                Category(name='Entertainment', type='expense'),
                Category(name='Utilities', type='expense'),
                Category(name='Healthcare', type='expense'),
                Category(name='Shopping', type='expense'),
                Category(name='Other', type='expense')
            ]
            db.session.add_all(default_categories)
            db.session.commit()

# Routes
@app.route('/')
def index():
    # Get summary statistics
    total_income = db.session.query(func.sum(Transaction.amount)).filter_by(type='income').scalar() or 0
    total_expenses = db.session.query(func.sum(Transaction.amount)).filter_by(type='expense').scalar() or 0
    balance = total_income - total_expenses
    
    # Get recent transactions
    recent_transactions = Transaction.query.order_by(Transaction.date.desc()).limit(10).all()
    
    # Get monthly data for current month
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    monthly_income = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.type == 'income',
        extract('month', Transaction.date) == current_month,
        extract('year', Transaction.date) == current_year
    ).scalar() or 0
    
    monthly_expenses = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.type == 'expense',
        extract('month', Transaction.date) == current_month,
        extract('year', Transaction.date) == current_year
    ).scalar() or 0
    
    return render_template('index.html', 
                         total_income=total_income,
                         total_expenses=total_expenses,
                         balance=balance,
                         monthly_income=monthly_income,
                         monthly_expenses=monthly_expenses,
                         recent_transactions=recent_transactions)

@app.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        description = request.form['description']
        trans_type = request.form['type']
        category_id = int(request.form['category'])
        date_str = request.form['date']
        
        date = datetime.strptime(date_str, '%Y-%m-%d')
        
        transaction = Transaction(
            amount=amount,
            description=description,
            type=trans_type,
            category_id=category_id,
            date=date
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('index'))
    
    categories = Category.query.all()
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('transactions/add_transaction.html', categories=categories, today=today)

@app.route('/transactions')
def transactions():
    all_transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    return render_template('transactions/transactions.html', transactions=all_transactions)

@app.route('/delete_transaction/<int:id>')
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('transactions'))

@app.route('/reports')
def reports():
    # Get expense breakdown by category
    expense_by_category = db.session.query(
        Category.name,
        func.sum(Transaction.amount).label('total')
    ).join(Transaction).filter(
        Transaction.type == 'expense'
    ).group_by(Category.name).all()
    
    # Get income breakdown by category
    income_by_category = db.session.query(
        Category.name,
        func.sum(Transaction.amount).label('total')
    ).join(Transaction).filter(
        Transaction.type == 'income'
    ).group_by(Category.name).all()
    
    # Get monthly trends (last 6 months)
    monthly_data = []
    for i in range(5, -1, -1):
        date = datetime.now() - timedelta(days=30*i)
        month = date.month
        year = date.year
        
        income = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.type == 'income',
            extract('month', Transaction.date) == month,
            extract('year', Transaction.date) == year
        ).scalar() or 0
        
        expenses = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.type == 'expense',
            extract('month', Transaction.date) == month,
            extract('year', Transaction.date) == year
        ).scalar() or 0
        
        monthly_data.append({
            'month': date.strftime('%b %Y'),
            'income': income,
            'expenses': expenses
        })
    
    return render_template('transactions/option/reports.html',
                         expense_by_category=expense_by_category,
                         income_by_category=income_by_category,
                         monthly_data=monthly_data)

@app.route('/categories')
def categories():
    all_categories = Category.query.all()
    return render_template('transactions/option/categories.html', categories=all_categories)

@app.route('/add_category', methods=['POST'])
def add_category():
    name = request.form['name']
    cat_type = request.form['type']
    
    category = Category(name=name, type=cat_type)
    db.session.add(category)
    db.session.commit()
    
    flash('Category added successfully!', 'success')
    return redirect(url_for('categories'))

# Templates would go in a 'templates' folder
# Create the following HTML files:

"""
templates/base.html:
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Finance Tracker</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        nav { background: #2c3e50; color: white; padding: 1rem 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        nav h1 { display: inline-block; margin-right: 2rem; }
        nav a { color: white; text-decoration: none; margin-right: 1.5rem; padding: 0.5rem 1rem; border-radius: 4px; transition: background 0.3s; }
        nav a:hover { background: #34495e; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }
        .alert { padding: 1rem; margin-bottom: 1rem; border-radius: 4px; }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 1.5rem; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 8px; text-align: center; }
        .stat-card.income { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
        .stat-card.expense { background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%); }
        .stat-card h3 { font-size: 0.9rem; margin-bottom: 0.5rem; opacity: 0.9; }
        .stat-card p { font-size: 2rem; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: 600; }
        .btn { padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; transition: all 0.3s; }
        .btn-primary { background: #667eea; color: white; }
        .btn-primary:hover { background: #5568d3; }
        .btn-danger { background: #ee0979; color: white; }
        .btn-danger:hover { background: #d60862; }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
        .form-group input, .form-group select, .form-group textarea { width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; }
        .income { color: #38ef7d; }
        .expense { color: #ff6a00; }
    </style>
</head>
<body>
    <nav>
        <h1>💰 Finance Tracker</h1>
        <a href="/">Dashboard</a>
        <a href="/add_transaction">Add Transaction</a>
        <a href="/transactions">Transactions</a>
        <a href="/reports">Reports</a>
        <a href="/categories">Categories</a>
    </nav>
    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </div>
</body>
</html>

templates/index.html:
{% extends "base.html" %}
{% block content %}
<h2>Dashboard</h2>
<div class="stats-grid">
    <div class="stat-card income">
        <h3>Total Income</h3>
        <p>₹{{ "%.2f"|format(total_income) }}</p>
    </div>
    <div class="stat-card expense">
        <h3>Total Expenses</h3>
        <p>₹{{ "%.2f"|format(total_expenses) }}</p>
    </div>
    <div class="stat-card">
        <h3>Balance</h3>
        <p>₹{{ "%.2f"|format(balance) }}</p>
    </div>
</div>

<div class="stats-grid">
    <div class="stat-card income">
        <h3>Monthly Income</h3>
        <p>₹{{ "%.2f"|format(monthly_income) }}</p>
    </div>
    <div class="stat-card expense">
        <h3>Monthly Expenses</h3>
        <p>₹{{ "%.2f"|format(monthly_expenses) }}</p>
    </div>
</div>

<div class="card">
    <h3>Recent Transactions</h3>
    <table>
        <thead>
            <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Category</th>
                <th>Amount</th>
            </tr>
        </thead>
        <tbody>
            {% for transaction in recent_transactions %}
            <tr>
                <td>{{ transaction.date.strftime('%Y-%m-%d') }}</td>
                <td>{{ transaction.description }}</td>
                <td>{{ transaction.category.name }}</td>
                <td class="{{ transaction.type }}">
                    {{ '+' if transaction.type == 'income' else '-' }}₹{{ "%.2f"|format(transaction.amount) }}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}

templates/add_transaction.html:
{% extends "base.html" %}
{% block content %}
<div class="card">
    <h2>Add Transaction</h2>
    <form method="POST">
        <div class="form-group">
            <label>Type</label>
            <select name="type" id="type" required onchange="filterCategories()">
                <option value="expense">Expense</option>
                <option value="income">Income</option>
            </select>
        </div>
        <div class="form-group">
            <label>Amount</label>
            <input type="number" name="amount" step="0.01" required>
        </div>
        <div class="form-group">
            <label>Category</label>
            <select name="category" id="category" required>
                {% for category in categories %}
                <option value="{{ category.id }}" data-type="{{ category.type }}">{{ category.name }}</option>
                {% endfor %}
            </select>
        </div>
        <div class="form-group">
            <label>Description</label>
            <textarea name="description" rows="3"></textarea>
        </div>
        <div class="form-group">
            <label>Date</label>
            <input type="date" name="date" value="{{ today }}" required>
        </div>
        <button type="submit" class="btn btn-primary">Add Transaction</button>
        <a href="/" class="btn">Cancel</a>
    </form>
</div>
<script>
function filterCategories() {
    const type = document.getElementById('type').value;
    const options = document.getElementById('category').options;
    for (let i = 0; i < options.length; i++) {
        if (options[i].getAttribute('data-type') === type) {
            options[i].style.display = 'block';
            if (options[i].style.display !== 'none') {
                document.getElementById('category').value = options[i].value;
            }
        } else {
            options[i].style.display = 'none';
        }
    }
}
filterCategories();
</script>
{% endblock %}

templates/transactions.html:
{% extends "base.html" %}
{% block content %}
<div class="card">
    <h2>All Transactions</h2>
    <table>
        <thead>
            <tr>
                <th>Date</th>
                <th>Type</th>
                <th>Category</th>
                <th>Description</th>
                <th>Amount</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
            {% for transaction in transactions %}
            <tr>
                <td>{{ transaction.date.strftime('%Y-%m-%d') }}</td>
                <td>{{ transaction.type.title() }}</td>
                <td>{{ transaction.category.name }}</td>
                <td>{{ transaction.description }}</td>
                <td class="{{ transaction.type }}">
                    {{ '+' if transaction.type == 'income' else '-' }}₹{{ "%.2f"|format(transaction.amount) }}
                </td>
                <td>
                    <a href="/delete_transaction/{{ transaction.id }}" class="btn btn-danger" 
                       onclick="return confirm('Are you sure?')">Delete</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}

templates/reports.html:
{% extends "base.html" %}
{% block content %}
<h2>Financial Reports</h2>

<div class="card">
    <h3>Monthly Trends</h3>
    <table>
        <thead>
            <tr>
                <th>Month</th>
                <th>Income</th>
                <th>Expenses</th>
                <th>Savings</th>
            </tr>
        </thead>
        <tbody>
            {% for month in monthly_data %}
            <tr>
                <td>{{ month.month }}</td>
                <td class="income">₹{{ "%.2f"|format(month.income) }}</td>
                <td class="expense">₹{{ "%.2f"|format(month.expenses) }}</td>
                <td>₹{{ "%.2f"|format(month.income - month.expenses) }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<div class="card">
    <h3>Expenses by Category</h3>
    <table>
        <thead>
            <tr>
                <th>Category</th>
                <th>Total</th>
            </tr>
        </thead>
        <tbody>
            {% for category, total in expense_by_category %}
            <tr>
                <td>{{ category }}</td>
                <td class="expense">₹{{ "%.2f"|format(total) }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<div class="card">
    <h3>Income by Category</h3>
    <table>
        <thead>
            <tr>
                <th>Category</th>
                <th>Total</th>
            </tr>
        </thead>
        <tbody>
            {% for category, total in income_by_category %}
            <tr>
                <td>{{ category }}</td>
                <td class="income">₹{{ "%.2f"|format(total) }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}

templates/categories.html:
{% extends "base.html" %}
{% block content %}
<div class="card">
    <h2>Manage Categories</h2>
    <form method="POST" action="/add_category">
        <div class="form-group">
            <label>Category Name</label>
            <input type="text" name="name" required>
        </div>
        <div class="form-group">
            <label>Type</label>
            <select name="type" required>
                <option value="expense">Expense</option>
                <option value="income">Income</option>
            </select>
        </div>
        <button type="submit" class="btn btn-primary">Add Category</button>
    </form>
</div>

<div class="card">
    <h3>Existing Categories</h3>
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Type</th>
            </tr>
        </thead>
        <tbody>
            {% for category in categories %}
            <tr>
                <td>{{ category.name }}</td>
                <td>{{ category.type.title() }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
"""

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
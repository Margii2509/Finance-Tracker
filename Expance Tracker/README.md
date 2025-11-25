# 💰 Finance Tracker

A modern, full-featured personal finance tracking web application built with Flask, Python, and SQLite. Track your income and expenses, visualize spending patterns, and gain insights into your financial health.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

- **Dashboard** - Get a quick overview of your financial status
  - Total income, expenses, and current balance
  - Monthly income and expense tracking
  - Recent transactions at a glance

- **Transaction Management** - Easy-to-use interface for tracking money flow
  - Add income and expense transactions
  - Categorize transactions for better organization
  - Add descriptions and custom dates
  - Delete transactions when needed

- **Financial Reports** - Understand your spending habits
  - Monthly trends over the last 6 months
  - Expense breakdown by category with percentage analysis
  - Income sources visualization
  - Savings rate calculation

- **Category Management** - Organize your finances your way
  - Pre-loaded default categories
  - Add custom income and expense categories
  - Color-coded category display

- **Modern UI** - Beautiful and responsive design
  - Gradient color schemes
  - Mobile-friendly responsive layout
  - Smooth animations and transitions
  - Intuitive navigation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the repository**
```bash
git clone <repository-url>
cd finance_tracker
```

2. **Install required packages**
```bash
pip install flask flask-sqlalchemy
```

3. **Run the application**
```bash
**.\.venv311\Scripts\python.exe app.py**
```

4. **Open your browser**
```
http://127.0.0.1:5000
```

That's it! The application will automatically create the SQLite database and populate it with default categories on first run.

## Project Structure

```
finance_tracker/
│
├── app.py                      # Main Flask application
├── finance.db                  # SQLite database (auto-generated)
├── README.md                   # This file
│
└── templates/                  # HTML templates
    ├── base.html              # Base template with navigation
    ├── index.html             # Dashboard page
    ├── add_transaction.html   # Add transaction form
    ├── transactions.html      # All transactions view
    ├── reports.html           # Financial reports
    └── categories.html        # Category management
```

## Usage Guide

### Adding a Transaction

1. Click **"Add Transaction"** in the navigation bar
2. Select transaction type (Income or Expense)
3. Enter the amount in INR (₹)
4. Choose a category (filtered by transaction type)
5. Add an optional description
6. Select the date
7. Click **"Add Transaction"**

### Viewing Reports

1. Navigate to **"Reports"** section
2. View monthly trends for the last 6 months
3. Analyze expense breakdown by category
4. Check income sources and their percentages
5. Monitor your savings rate

### Managing Categories

1. Go to **"Categories"** page
2. Enter a new category name
3. Select type (Income or Expense)
4. Click **"Add Category"**
5. View all categories organized by type

## Technologies Used

- **Backend:** Flask (Python web framework)
- **Database:** SQLite with SQLAlchemy ORM
- **Frontend:** HTML5, CSS3, Jinja2 templates
- **Styling:** Custom CSS with gradients and animations

## Database Schema

### Transaction Table
- `id` (Primary Key)
- `amount` (Float)
- `description` (String)
- `date` (DateTime)
- `type` (String: 'income' or 'expense')
- `category_id` (Foreign Key)

### Category Table
- `id` (Primary Key)
- `name` (String, Unique)
- `type` (String: 'income' or 'expense')

## Default Categories

### Income Categories:
- Salary
- Freelance
- Investment

### Expense Categories:
- Food
- Transport
- Entertainment
- Utilities
- Healthcare
- Shopping
- Other

## Configuration

### Change Secret Key
In `app.py`, update the secret key for production:
```python
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this!
```

### Change Database Location
Modify the database URI in `app.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
```

## Features Breakdown

| Feature | Description |
|---------|-------------|
| **Dashboard** | Real-time financial overview with colorful stat cards |
| **Transactions** | Complete transaction history with search and filter |
| **Reports** | Visual analytics with charts and percentage breakdowns |
| **Categories** | Flexible categorization system for better organization |
| **Responsive** | Works perfectly on desktop, tablet, and mobile devices |

## Tips for Best Use

1. **Be Consistent** - Add transactions regularly for accurate tracking
2. **Use Descriptions** - Add notes to remember transaction details
3. **Categorize Properly** - Use appropriate categories for better insights
4. **Check Reports** - Review monthly reports to identify spending patterns
5. **Custom Categories** - Create categories that match your lifestyle

## Troubleshooting

### Application won't start
```bash
# Make sure Flask is installed
pip install flask flask-sqlalchemy

# Check Python version
python --version  # Should be 3.7+
```

### Database errors
```bash
# Delete the database and restart (WARNING: This deletes all data)
rm finance.db
python app.py
```

### Port already in use
Change the port in `app.py`:
```python
app.run(debug=True, port=5001)  # Use different port
```

## Security Notes

- This is a local application intended for personal use
- For production deployment, ensure proper security measures:
  - Change the secret key
  - Use environment variables for configuration
  - Implement user authentication
  - Use HTTPS
  - Add input validation and sanitization

## Future Enhancements

Potential features to add:
- [ ] User authentication and multi-user support
- [ ] Budget planning and alerts
- [ ] Data export (CSV, PDF)
- [ ] Charts and graphs visualization
- [ ] Recurring transactions
- [ ] Bill reminders
- [ ] Mobile app version
- [ ] Cloud backup

## License

This project is licensed under the MIT License - feel free to use and modify as needed.

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## Support

If you encounter any issues or have questions:
1. Check the troubleshooting section
2. Review the code comments in `app.py`
3. Create an issue in the repository

## Acknowledgments

- Flask framework for the excellent web development tools
- SQLAlchemy for the powerful ORM
- The Python community for continuous support

---
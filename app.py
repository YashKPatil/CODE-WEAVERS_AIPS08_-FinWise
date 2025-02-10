import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash  # Add flash here

import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from collections import defaultdict
from datetime import datetime
import json
import joblib
from sklearn.preprocessing import LabelEncoder
import google.generativeai as genai
import re

app = Flask(__name__)
app.secret_key = "finwise_secret_key"

# Load the machine learning model and encoders at startup
model = joblib.load("transaction_classifier.pkl")
le_receiver = joblib.load("receiver_encoder.pkl")
le_category = joblib.load("category_encoder.pkl")

# Generative AI setup
genai.configure(api_key="AIzaSyCsQu31o8WJSVmggCavy0NBjVpzlUPVqw0")
# Database for user authentication
def init_auth_db():
    conn = sqlite3.connect('auth_users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS auth_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    user_name TEXT NOT NULL,
                    password TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        user_name = request.form['user_name']
        password = request.form['password']

        # Ensure all fields are filled in
        if not email or not user_name or not password:
            flash('All fields are required!', 'warning')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        # Database connection and insertion
        conn = sqlite3.connect('auth_users.db')
        c = conn.cursor()
        try:
            # Insert the user into the database
            c.execute('INSERT INTO auth_users (email, user_name, password) VALUES (?, ?, ?)',
                      (email, user_name, hashed_password))
            conn.commit()  # Commit the changes
            session['user_id'] = c.lastrowid  # Set the session for the user
            session['name'] = user_name  # Store the username in session
            flash('Registration successful! Please log in.', 'success')  # Flash message
            return redirect(url_for('login'))  # Redirect to login page after success
        except sqlite3.IntegrityError:
            flash('Email already exists. Please use a different email.', 'danger')  # Handle email already exists
            conn.close()
            return redirect(url_for('register'))  # Redirect to register page in case of error

    return render_template('register.html')  # Render register page on GET request

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('auth_users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM auth_users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):  # Verify the hashed password
            session['user_id'] = user[0]
            session['name'] = user[2]  # Store the username in session
            flash('Login successful!', 'success')
            
            # Redirect to user_info.html to collect name and salary if they are not provided
            if 'name' not in session or 'salary' not in session:
                return redirect(url_for('get_user_info'))
            
            return redirect(url_for('index'))  # Otherwise, go to the index page
        else:
            flash('Invalid email or password. If you are not registered, please sign up.', 'danger')
            return redirect(url_for('register'))  # Redirect to registration if login fails.

    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()  # Clears all session variables
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))
    
    # Modify the home page to require login
# @app.route('/home')
# def index():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))

#     # Calculate budget allocations based on the 50-30-20 rule
#     monthly_salary = session.get('salary', 0)
#     budget_allocation = {
#         'needs': monthly_salary * 0.5,
#         'wants': monthly_salary * 0.3,
#         'savings': monthly_salary * 0.2
#     }

#     return render_template('index.html', name=session['name'], salary=monthly_salary, budget_allocation=budget_allocation)

# Database setup
def init_db():
    conn = sqlite3.connect('finwise.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  category TEXT NOT NULL,
                  amount REAL NOT NULL,
                  date TEXT NOT NULL,
                  user_name TEXT,
                  expense_type TEXT)''')  # Added expense_type for 50-30-20 rule
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  salary REAL NOT NULL)''')
    conn.commit()
    conn.close()

# Predict transaction category
def predict_transaction_category(amount, receiver):
    # Encode the receiver
    if receiver in le_receiver.classes_:
        receiver_encoded = le_receiver.transform([receiver])[0]
    else:
        return "Unknown"  # Return "Unknown" if the receiver is not recognized
    
    # Predict category
    transaction_data = [[amount, receiver_encoded]]
    category_encoded = model.predict(transaction_data)[0]
    
    # Decode the category
    category = le_category.inverse_transform([category_encoded])[0]
    return category

# Function to get investment suggestions using Generative AI
def get_investment_suggestions(savings, salary, total_spent, name1):
    try:
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
            "response_mime_type": "text/plain",
        }

        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config=generation_config,
        )

        chat_session = model.start_chat(history=[])

        # Construct the prompt correctly
        spending_percentages = {
            'needs': (total_spent / salary * 100) if salary > 0 else 0,
            'wants': 30,  # Dummy value for demonstration
        }

        budget_targets = {
            'needs': salary * 0.5,
            'wants': salary * 0.3,
            'savings': salary * 0.2,
        }

        # Fetch spending by category and format it for the prompt
        category_totals = get_total_spending_by_category(name1)
        category_summary = "\n".join([f"- {category}: ₹{total:.2f}" for category, total in category_totals])

        prompt = f"""
        
        I have the following financial details about {name1} in the Indian market:

        Monthly Salary: ₹{salary}  
        Total Monthly Expenditure: ₹{total_spent}  
        Monthly Savings: ₹{savings}  

        Spending Distribution by Category:  
        {category_summary}

        Budget Targets:  
        - Needs (50% Target): ₹{salary * 0.5}  
        - Wants (30% Target): ₹{salary * 0.3}  
        - Savings (20% Target): ₹{salary * 0.2}  

        Provide personalized financial strategies and investment suggestions.
        If the balance is zero or negative, focus only on expense control:  

        - Cut Costs:Cancel unnecessary subscriptions.  
        - Prioritize Essentials: Rent, groceries, and utilities.  
        - Avoid Debt: Focus on loan repayments.  
        - Track Spending: Use budgeting apps effectively.
           give output like you are speaking to {name1}
        """

        response = chat_session.send_message(prompt)
        response_text = response.text.strip()

        # Clean up any unnecessary formatting
        cleaned_response = re.sub(r'\*{2}', '', response_text)
        return cleaned_response if cleaned_response else "No suggestions found."

    except Exception as e:
        print(f"Generative AI Error: {e}")
        return "Error fetching suggestions."


# Route to redirect to login first
@app.route('/', methods=['GET', 'POST'])
def home_redirect():
    if 'user_id' in session:
        if 'salary' not in session:
            return redirect(url_for('get_user_info'))
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/user_info', methods=['GET', 'POST'])
def get_user_info():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # If the user is not logged in, redirect to login
    
    if request.method == 'POST':
        session['name'] = request.form['name']
        session['salary'] = float(request.form['salary'])
        session.modified = True  # Ensure session changes are saved
        print("User info saved:", session['name'], session['salary']) 
        return redirect(url_for('index'))  # Redirect to the index page after collecting data
    
    return render_template('user_info.html')  # Render the form to collect user data


@app.route('/home')
def index():
    if 'user_id' not in session:
        flash('Please log in to access your budget details.', 'warning')
        return redirect(url_for('login'))

    if 'name' not in session or 'salary' not in session:
        flash('Please provide your name and salary information.', 'info')
        return redirect(url_for('get_user_info'))
    print("Redirecting to index page for:", session['name'], session['salary'])  # Debugging line

    monthly_salary = session['salary']
    budget_allocation = {
        'needs': monthly_salary * 0.5,
        'wants': monthly_salary * 0.3,
        'savings': monthly_salary * 0.2
    }

    return render_template('index.html', 
                          name=session['name'], 
                          salary=session['salary'], 
                          budget_allocation=budget_allocation)

@app.route('/clear_session')
def clear_session():
    session.clear()
    return "Session cleared"

@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if 'name' not in session:
        return redirect(url_for('get_user_info'))

    if request.method == 'POST':
        receiver = request.form['receiver_name']
        amount = float(request.form['amount'])
        date = request.form['date']
        user_name = session['name']
        
        # Predict the category using the machine learning model
        category = predict_transaction_category(amount, receiver)
        if category == "Unknown":
            category = "Miscellaneous"  # Default category for unknown receivers
        
        # Determine expense type for 50-30-20 rule
        if category.lower() in ['rent', 'utilities', 'groceries']:
            expense_type = 'needs'
        elif category.lower() in ['entertainment', 'dining']:
            expense_type = 'wants'
        else:
            expense_type = 'savings'

        # Store the expense in the database
        conn = sqlite3.connect('finwise.db')
        c = conn.cursor()
        c.execute('INSERT INTO expenses (category, amount, date, user_name, expense_type) VALUES (?, ?, ?, ?, ?)',
                  (category, amount, date, user_name, expense_type))
        conn.commit()
        conn.close()
        return redirect(url_for('view_expenses'))
    
    return render_template('add_expense.html')

#creating map of category and there total expence
def get_total_spending_by_category(user_name):
    """Fetch total spending for each category for the given user."""
    conn = sqlite3.connect('finwise.db')
    c = conn.cursor()
    c.execute('SELECT category, SUM(amount) FROM expenses WHERE user_name = ? GROUP BY category', (user_name,))
    category_totals = c.fetchall()  # Returns a list of tuples [(category, total_spent), ...]
    conn.close()
    
    return category_totals

@app.route('/view')
def view_expenses():
    if 'name' not in session:
        return redirect(url_for('get_user_info'))

    user_name = session['name']
    monthly_salary = session['salary']

    try:
        conn = sqlite3.connect('finwise.db')
        c = conn.cursor()
        
        # Fetch expenses with expense type
        c.execute('SELECT * FROM expenses WHERE user_name = ? ORDER BY date DESC', (user_name,))
        expenses = c.fetchall()

        # Initialize spending for each type
        type_spending = {
            'needs': 0.0,
            'wants': 0.0,
            'savings': 0.0
        }

        # Calculate total spending by expense type
        for expense in expenses:
            expense_type = expense[5] if len(expense) > 5 and expense[5] else 'needs'  # Default to needs if not specified
            if expense_type in type_spending:
                type_spending[expense_type] += expense[2]

        # Calculate total spent
        total_spent = sum(type_spending.values())

        # Calculate savings (This is the savings spending from the 'savings' category)
        # savings = type_spending['savings']

        # Calculate percentages of monthly salary for each type
        spending_percentages = {
            'needs': (type_spending['needs'] / monthly_salary * 100) if monthly_salary > 0 else 0,
            'wants': (type_spending['wants'] / monthly_salary * 100) if monthly_salary > 0 else 0,
            # 'savings': (savings / monthly_salary * 100) if monthly_salary > 0 else 0
        }

        # Calculate budget targets
        budget_targets = {
            'needs': monthly_salary * 0.5,
            'wants': monthly_salary * 0.3,
            'savings': monthly_salary * 0.2
        }

        # Regular expense tracking data
        category_spending = defaultdict(float)
        for expense in expenses:
            category_spending[expense[1]] += expense[2]

        category_spending = dict(sorted(category_spending.items(), key=lambda x: x[1], reverse=True))

        # Monthly trends
        monthly_data = defaultdict(float)
        for expense in expenses:
            date = datetime.strptime(expense[3], "%Y-%m-%d")
            month_year = date.strftime("%b %Y")
            monthly_data[month_year] += expense[2]

        sorted_months = sorted(monthly_data.keys(), key=lambda x: datetime.strptime(x, "%b %Y"))
        monthly_spending = {month: monthly_data[month] for month in sorted_months}

        conn.close()

        # Pass salary and savings to the template
        return render_template(
            'view_expenses.html',
            expenses=expenses,
            total_spent=total_spent,
            category_spending=json.dumps(category_spending),
            monthly_spending=json.dumps(monthly_spending),
            type_spending=type_spending,
            budget_targets=budget_targets,
            spending_percentages=spending_percentages,
            salary=monthly_salary,  # Add the salary
            savings= monthly_salary-total_spent  # Add the savings
        )
    except Exception as e:
        print(f"Error in view_expenses: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return render_template('error.html', error=str(e))

@app.route('/investment')
def investment():
    if 'name' not in session or 'salary' not in session:
        return redirect(url_for('get_user_info'))

    salary = session['salary']
    name1 = session['name']
    
    conn = sqlite3.connect('finwise.db')
    c = conn.cursor()
    
    # Get total expenses for the user
    c.execute('SELECT SUM(amount) FROM expenses WHERE user_name = ?', (name1,))
    total_spent = c.fetchone()[0] or 0  # Handle None if no expenses

    # Get category-wise spending
    c.execute('SELECT category, SUM(amount) FROM expenses WHERE user_name = ? GROUP BY category', (name1,))
    category_spending = c.fetchall()  # Returns a list of tuples [(category1, total1), (category2, total2), ...]

    conn.close()

    savings = salary - total_spent

    # Get personalized investment and saving suggestions from Generative AI
    ai_suggestions = get_investment_suggestions(savings, salary, total_spent, name1)

    # Define general investment tips based on savings
    if savings < 5000:
        investment_tips = ["Fixed Deposit (FD)", "Recurring Deposit (RD)", "Emergency Fund"]
    elif 5000 <= savings < 20000:
        investment_tips = ["Mutual Funds (SIP)", "Debt Funds", "Gold Investment"]
    else:
        investment_tips = ["Stock Market", "Bonds", "Cryptocurrency", "Real Estate"]

    return render_template(
        "investment.html", 
        name=name1, 
        salary=salary, 
        savings=savings, 
        total_spent=total_spent,
        category_spending=category_spending,  # Pass category-wise spending to the template
        investment_tips=investment_tips, 
        ai_suggestions=ai_suggestions
    )


# Update the database schema if required
def update_database():
    conn = sqlite3.connect('finwise.db')
    c = conn.cursor()
    
    # Check if required columns exist
    c.execute("PRAGMA table_info(expenses)")
    columns = [column[1] for column in c.fetchall()]
    
    if "user_name" not in columns:
        c.execute("ALTER TABLE expenses ADD COLUMN user_name TEXT")
    
    if "expense_type" not in columns:
        c.execute("ALTER TABLE expenses ADD COLUMN expense_type TEXT")
    
    conn.commit()
    conn.close()

# Delete expense
@app.route('/delete/<int:id>')
def delete_expense(id):
    conn = sqlite3.connect('finwise.db')
    c = conn.cursor()
    c.execute('DELETE FROM expenses WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_expenses'))

if __name__ == '__main__':
    init_auth_db()  # Initialize the authentication database
    init_db()        # Initialize the main database
    update_database() # Update database schema if needed
    app.run(debug=True)

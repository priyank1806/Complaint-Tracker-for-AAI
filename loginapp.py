from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize DB with users and complaints table
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            otp TEXT
        )
    ''')

    # Complaints table with status
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            date TEXT,
            time TEXT,
            complaint TEXT,
            description TEXT,
            status TEXT DEFAULT 'Opened'
        )
    ''')

    conn.commit()
    conn.close()

# 🔐 Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = user[0]
            session['name'] = user[1]
            session['email'] = user[2]
            return redirect('/complain')
        else:
            return "Invalid Credentials. Try again, baby 😏"

    return render_template('login.html')

# 📝 Complaint Submission
@app.route('/complain', methods=['GET', 'POST'])
def complain():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        name = session.get('name')
        email = session.get('email')
        date = request.form['date']
        time = request.form['time']
        complaint = request.form['complaint']
        description = request.form['description']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO complaints 
            (name, email, date, time, complaint, description, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, email, date, time, complaint, description, "Opened"))
        conn.commit()
        conn.close()

        return redirect('/success')

    return render_template('complaint.html')

# ✅ Success Page After Submission
@app.route('/success')
def success():
    return render_template('success.html')

# 📋 View All Complaints by Logged-in User
@app.route('/complaints')
def complaints():
    if 'user' not in session:
        return redirect('/login')

    email = session.get('email')

    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, date, time, complaint, description, status 
        FROM complaints WHERE email = ?
    ''', (email,))
    rows = cursor.fetchall()
    conn.close()

    complaints_list = []
    for row in rows:
        complaints_list.append({
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'date': row[3],
            'time': row[4],
            'complaint': row[5],
            'description': row[6],
            'status': row[7]
        })

    return render_template('user_complaint.html', complaints=complaints_list)

# 🌐 Home Route (Redirect to Login)
@app.route('/')
def home():
    return redirect('/login')

# 💥 Run the app
if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)
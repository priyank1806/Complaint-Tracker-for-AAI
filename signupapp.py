from flask import Flask, render_template, request, redirect, session
import sqlite3
import random
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# --- INIT DB ---
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            otp TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            date TEXT,
            time TEXT,
            complaint TEXT,
            description TEXT
        )
    ''')

    conn.commit()
    conn.close()

# --- Send OTP Email ---
def send_otp(email, otp):
    msg = EmailMessage()
    msg.set_content(f'Your OTP for account verification is: {otp}')
    msg['Subject'] = 'Verify Your Email - Complaint Tracker'
    msg['From'] = 'priyankar18aarav@gmail.com'
    msg['To'] = email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('priyankar18aarav@gmail.com', 'qfzj xocj ftee ihcf')
        smtp.send_message(msg)

# --- SIGNUP ---
@app.route('/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        otp = str(random.randint(100000, 999999))

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (name, email, password, otp) VALUES (?, ?, ?, ?)",
                           (name, email, password, otp))
            conn.commit()
            send_otp(email, otp)
            session['email'] = email
            session['name'] = name
            return redirect('/verify')
        except sqlite3.IntegrityError:
            return "Oopsie! That email already exists, silly baby 🥴"
        finally:
            conn.close()

    return render_template('signup.html')

# --- OTP VERIFICATION ---
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        email = session.get('email')

        if not email:
            return "Session expired. Start again, my confused cutie 😵‍💫"

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT otp FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        conn.close()

        if result and result[0] == entered_otp:
            return redirect('/login')
        else:
            return "Wrong OTP baby 🙄 Try harder next time."

    return render_template('otpverify.html')

# --- LOGIN ---
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
            return "Invalid login. Baby, do it right this time 😘"

    return render_template('login.html')

# --- COMPLAINT SUBMISSION ---
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
            (name, email, date, time, complaint, description) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, email, date, time, complaint, description))
        conn.commit()
        conn.close()

        return redirect('/success')

    return render_template('complaint.html')

# --- SUCCESS PAGE ---
@app.route('/success')
def success():
    return render_template('success.html')

# --- VIEW ALL COMPLAINTS ---
@app.route('/user_complaint')
def user_complaint():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, date, time, complaint, description FROM complaints")
    complaints = cursor.fetchall()
    conn.close()

    return render_template('user_complaint.html', complaints=complaints)

# --- LOGOUT ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# --- RUN APP ---
if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
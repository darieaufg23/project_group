from flask import Flask, render_template, request, g, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
import sqlite3
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a secure secret key


# Function to get the database connection
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('database.db', check_same_thread=False)
    return g.db

# Function to initialize the database
def initialize_db():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            surname TEXT NOT NULL,
            phone_number INTEGER,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    db.commit()

# Route for the index page
@app.route('/')
def index():
    return render_template('index.html')

# Route for login and registration
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[5], password):  # Assuming the password hash is stored at index 5
            return redirect(url_for('dashboard'))  # Redirect to the dashboard on successful login
        else:
            return 'Невірне ім\'я користувача або пароль'

    return render_template("login.html")

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        surname = request.form['surname']
        phone_number = request.form['phone_number']
        email = request.form['email']

        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, surname, phone_number, email, password_hash) VALUES (?, ?, ?, ?, ?)",
                       (username, surname, phone_number, email, generate_password_hash(password)))
        db.commit()
        return redirect(url_for('login'))  # Redirect to the login page after successful registration

    return render_template('registration.html')

# Route for the dashboard
@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    if request.method == 'POST':
        username = request.form['username']
        surname = request.form['surname']
        phone_number = request.form['phone_number']
        email = request.form['email']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor()

        cursor.execute("INSERT INTO users (username, surname, phone_number, email, password_hash) VALUES (?, ?, ?, ?, ?)",
                       (username, surname, phone_number, email, generate_password_hash(password)))
        db.commit()

    # Fetch all users from the database
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, username, surname, phone_number, email FROM users")
    users = cursor.fetchall()

    return render_template('dashboard.html', users=users)


if __name__ == '__main__':
    with app.app_context():
        initialize_db()
    app.run(debug=True)

    
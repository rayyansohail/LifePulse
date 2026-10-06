
from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'lifepulse_super_secret_key'

def get_db_connection():
    return psycopg2.connect(host="localhost", database="lifepulse_khi", user="postgres", password="admin")

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username, email, password, role FROM users WHERE username = %s OR email = %s;", (identifier, identifier))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[4]
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username/email or password.', 'error')
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form.get('role', 'Medical Officer')
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s);", (username, email, password, role))
            conn.commit()
            cur.close()
            conn.close()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Username or email already exists.', 'error')
            
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT hospital_id, hospital_name, region, city, available_beds, icu_beds, ventilators, oxygen_cylinders, blood_units_o_neg, surgical_masks, status FROM hospital_inventory ORDER BY hospital_id;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', inventory=rows, username=session.get('username'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/tracking')
def tracking():
    return render_template('tracking.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
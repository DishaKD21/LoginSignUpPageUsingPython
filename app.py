from flask import Flask, request, render_template, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Database setup function (create a connection, etc.)
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',  # e.g., 'localhost' or '127.0.0.1'
            database='pythondb',  # Here, you can write the name of your database
            user='root',  # Here, you can write your MySQL username
            password='root'  # Here, you can write your MySQL password
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')  # Ensure your HTML file is named index.html

@app.route('/auth', methods=['POST'])
def authenticate():
    action = request.form.get('action')  # 'login' or 'register'
    username = request.form['username']
    password = request.form['password']
    email = request.form.get('email')  # Will be None for login

    conn = get_db_connection()
    
    if conn is None:
        return jsonify(success=False, message='Database connection failed!'), 500
    
    try:
        cursor = conn.cursor()
        if action == 'register':
            # Logic to store user credentials
            cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (username, email, password))
            conn.commit()
            return jsonify(success=True, message='Registration successful!')
        elif action == 'login':
            # Logic to verify user credentials
            cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
            user = cursor.fetchone()
            if user:
                return jsonify(success=True, message='Login successful!')
            else:
                return jsonify(success=False, message='Invalid username or password'), 401
        else:
            return jsonify(success=False, message='Invalid action'), 400
    except mysql.connector.IntegrityError:
        return jsonify(success=False, message='Username already exists!'), 409
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)

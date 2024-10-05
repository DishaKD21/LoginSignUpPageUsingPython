from flask import Flask, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)

# Configuration for MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/pythondb'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

# Create the database tables if they don't exist
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect('/login')  # Redirect to the login page

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'email' in session:
        return redirect('/dashboard')

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if the email already exists
        existing_email = Users.query.filter_by(email=email).first()
        if existing_email:
            return render_template('register.html', error='Email already registered. Please log in.')

        # Check if the username already exists
        existing_username = Users.query.filter_by(username=username).first()
        if existing_username:
            return render_template('register.html', error='Username already registered. Please choose a different one.')

        # Register the new user
        new_user = Users(username=username, email=email, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Rollback if there is an error
            return render_template('register.html', error='Error registering user. Please try again.')

        # Automatically log in the user after registration
        session['email'] = new_user.email
        return redirect('/dashboard')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'email' in session:
        # If user is already logged in, redirect to dashboard
        return redirect('/dashboard')

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = Users.query.filter_by(email=email).first()

        # Check if user exists and validate the password
        if user and user.check_password(password):
            # Log in the user
            session['email'] = user.email
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid email or password.')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        user = Users.query.filter_by(email=session['email']).first()
        return render_template('dashboard.html', user=user)
    return redirect('/login')  # Redirect to login if not logged in

@app.route('/logout')
def logout():
    session.pop('email', None)  # Clear session data
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)

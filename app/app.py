import os
import sqlite3
from flask import Flask, request, jsonify, render_template, session
from flask_sqlalchemy import SQLAlchemy
from models import db, User
from prepopulate_db import prepopulate_db



app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)  

# Store
@app.route('/')
def home():
    return "Hello, Flask!"

# login
@app.route('/login', methods=['GET'])
def login_form():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    """Authenticate user by username and password."""
    data = request.form
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session['username'] = user.username
        session['role'] = user.role
        return jsonify({"message": "Login successful!", "user_id": user.role}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401

# publish game
@app.route('/publish')
def publish():
    pass

# Purchase game
@app.route('/purchase')
def purchase():
    pass

# view game details
@app.route('/game/<game_id>')
def game(game_id):
    pass

# view my games
@app.route('/myGames/<user_id>')
def viewGames(user_id):
    pass

"""THIS IS AN EXAMPLE ONLY!"""

# Route to display all users
@app.route('/users', methods=['GET'])
def get_users():
    """Fetch and return all users from the database."""
    users = User.query.all()  # Query all users
    # Convert user objects to a list of dictionaries
    users_list = [{"id": user.id, "username": user.username, "email": user.email} for user in users]
    return jsonify(users_list)  # Return as JSON

# Run the application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        prepopulate_db(app)
    
    app.run(debug=True)

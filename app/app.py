import os
import sqlite3
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, User
from prepopulate_db import prepopulate_db

from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# Store
@app.route('/')
def home():
    return render_template('home.html')


# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Logged in successfully.')
            return redirect(url_for('home'))
        else:
            flash('Please check your login details and try again.')
            return redirect(url_for('login'))

    return render_template('login.html')


# helper function
def is_logged_in():
    return 'user_id' in session


app.config['SECRET_KEY'] = 'your-secret-key-here'  # Required for session handling


# logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


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

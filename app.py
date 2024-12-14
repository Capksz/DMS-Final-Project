import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlite3

app = Flask(__name__)

DATABASE = 'mydatabase.db'
def get_db_connection():
    conn = sqlite3.connect(DATABASE)  
    return conn

def initalize_database():
    if not os.path.exists(DATABASE):
        print(f"Database file '{DATABASE}' not found. Initializing database...")
        with open(SCHEMA_FILE, 'r') as schema:
            sql_script = schema.read()
        conn = sqlite3.connect(DATABASE)
        conn.executescript(sql_script)
        conn.close()
        print("Database initialized successfully!")
    else:
        print(f"Database file '{DATABASE}' already exists. Skipping initialization and connecting.")
        conn = sqlite3.connect(DATABASE)
    return conn     

# Store
@app.route('/')
def home():
    return "Hello, Flask!"

# login
@app.route('/login')
def login():
    pass

# publish game
@app.route('/publish')
def publish():
    pass

# publish game
@app.route('/purchase')
def purchase():
    pass

# publish game
@app.route('/publish')
def publish():
    pass

# view game details
@app.route('/game/<game_id>')
def game(game_id):
    pass

# view my games
@app.route('/myGames/<user_id>')
def viewGames(user_id):
    pass

# Run the application
if __name__ == '__main__':
    app.run(debug=True)

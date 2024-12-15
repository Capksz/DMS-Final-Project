import os
import sqlite3
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, User
from prepopulate_db import prepopulate_db

from models import Game, LibraryGame
from datetime import datetime
from sqlalchemy import and_
from decimal import Decimal

from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# Store
@app.route('/')
def home():
    games = Game.query.all()
    print(f"Found {len(games)} games")  # test
    for game in games:
        print(f"Game: {game.name}")  # test
    return render_template('home.html', games=games)


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


@app.route('/purchase/<int:game_id>', methods=['GET', 'POST'])
def purchase(game_id):
    if not is_logged_in():
        flash('Please login to purchase games.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    game = Game.query.get_or_404(game_id)

    if request.method == 'POST':
        # Check if user already owns the game
        existing_game = LibraryGame.query.filter(
            and_(
                LibraryGame.user_id == user.id,
                LibraryGame.game_id == game.id
            )
        ).first()

        if existing_game:
            flash('You already own this game!')
            return redirect(url_for('home'))

        # Check if user has enough balance
        if user.wallet_balance < game.price:
            flash('Insufficient funds!')
            return redirect(url_for('purchase', game_id=game_id))

        # Process purchase
        user.wallet_balance -= game.price

        # Add game to user's library
        library_game = LibraryGame(
            user_id=user.id,
            game_id=game.id,
            last_played=None,
            favorite_status=False,
            hours_played=0,
            is_downloaded=False
        )

        db.session.add(library_game)
        db.session.commit()

        flash('Game purchased successfully!')
        return redirect(url_for('home'))

    return render_template('purchase.html', game=game, user=user)


@app.route('/library')
def library():
    if not is_logged_in():
        flash('Please login to view your library.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    library_games = LibraryGame.query.filter_by(user_id=user.id).all()

    # Get full game details for each library entry
    games = []
    for lib_game in library_games:
        game = Game.query.get(lib_game.game_id)
        if game:
            games.append({
                'game': game,
                'last_played': lib_game.last_played,
                'hours_played': lib_game.hours_played,
                'is_downloaded': lib_game.is_downloaded,
                'favorite_status': lib_game.favorite_status
            })

    return render_template('library.html', games=games, user=user)

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
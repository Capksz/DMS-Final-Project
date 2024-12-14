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

from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session, abort

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
db.init_app(app)


# Store
@app.route('/')
def home():
    return render_template('home.html', session=session)


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
            session['role'] = user.role
            session['username'] = user.username
            return redirect(url_for('home'))
        else:
            flash('Please check your login details and try again.')
            return redirect(url_for('login'))

    return render_template('login.html')

# logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


# publish game
@app.route('/publish', methods=['GET', 'POST'])
def publish():
    if session.get('role') != 'developer/publisher':
        abort(403)
    if request.method == 'POST':
        form_data = {
            "game_name": request.form.get('game_name'),
            "required_age": int(request.form.get('required_age')),
            "price": float(request.form.get('price')),
            "dlc_count": int(request.form.get('dlc_count')),
            "windows": request.form.get('windows') == 'yes',
            "mac": request.form.get('mac') == 'yes',
            "linux": request.form.get('linux') == 'yes',
            "achievements": int(request.form.get('achievements')),
            "supported_languages": request.form.getlist('supported_languages'),
            "full_audio_languages": request.form.getlist('full_audio_languages'),
            "developers": request.form.get('developers'),
            "publishers": request.form.getlist('publishers'),
            "categories": request.form.getlist('categories'),
            "genres": request.form.getlist('genres'),
            "game_tags": request.form.getlist('game_tags'),
        }

        session['form_data'] = form_data

        predicted_popularity = 10 # Placeholder popularity score
        session['predicted_popularity'] = predicted_popularity

        publishing_fee = round(predicted_popularity * 10, 2)
        session['publishing_fee'] = publishing_fee

        return redirect(url_for('publish_review'))

    return render_template('publish.html')

@app.route('/publish/review', methods=['GET', 'POST'])
def publish_review():
    if session.get('role') != 'developer/publisher':
        abort(403)
    form_data = session.get('form_data', {})
    predicted_popularity = session.get('predicted_popularity', None)
    publishing_fee = session.get('publishing_fee', None)

    if not form_data or predicted_popularity is None or publishing_fee is None:
        flash("You need to submit the form before accessing the review page.")
        return redirect(url_for('publish'))

    if request.method == 'POST':
        flash(f"Game '{form_data['game_name']}' has been published successfully!")
        session.pop('form_data', None)
        session.pop('predicted_popularity', None)
        session.pop('publishing_fee', None)
        return redirect(url_for('publish_success'))

    return render_template(
        'publish_cost.html',
        form_data=form_data,
        predicted_popularity=predicted_popularity,
        publishing_fee=publishing_fee
    )

@app.route('/publish/success', methods=['GET'])
def publish_success():
    return render_template('publish_success.html')

# purcahse
@app.route('/purchase/<int:game_id>', methods=['GET', 'POST'])
def purchase(game_id):
    if not is_logged_in():
        flash('Please login to purchase games.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    game = Game.query.get_or_404(game_id)

    if request.method == 'POST':
        existing_game = LibraryGame.query.filter(
            and_(
                LibraryGame.user_id == user.id,
                LibraryGame.game_id == game.id
            )
        ).first()

        if existing_game:
            flash('You already own this game!')
            return redirect(url_for('home'))

        if user.wallet_balance < game.price:
            flash('Insufficient funds!')
            return redirect(url_for('purchase', game_id=game_id))

        user.wallet_balance -= game.price

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

#game library
@app.route('/library')
def library():
    if not is_logged_in():
        flash('Please login to view your library.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    library_games = LibraryGame.query.filter_by(user_id=user.id).all()

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

import os
import sys
import sqlite3
import pickle
import pandas as pd
from sklearn.tree import plot_tree, export_text
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, User
from prepopulate_db import prepopulate_db

from models import Game, LibraryGame
from datetime import datetime
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from decimal import Decimal
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session, abort
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ML.mltable import AllDataModel, BasicInfoModel

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
db.init_app(app)

MLMODEL_URL = 'sqlite:///mlmodel.db'
ml_engine = create_engine(MLMODEL_URL)
MLSession = sessionmaker(bind=ml_engine)
ml_session = MLSession()


# Store
@app.route('/')
def home():
    games = Game.query.all()
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return render_template('home.html', games=games, session=session, user=user)


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

# helper function
def is_logged_in():
    return 'user_id' in session

# logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

#helper functions for publish

def get_most_recent_basic_info_model():
    model_entry = ml_session.query(BasicInfoModel).order_by(BasicInfoModel.created_at.desc()).first()
    if model_entry:
        return model_entry
    return None

def load_most_recent_model():
    model_entry = get_most_recent_basic_info_model()
    if model_entry:
        model, trained_columns, label_encoder = pickle.loads(model_entry.model_data)
        print("Trained columns:", trained_columns[:20])
        return model, trained_columns, label_encoder
    raise ValueError("No model found in the database.")


def prepare_numeric_features(form_data):
    numeric_features = {
        "required_age": form_data["required_age"],
        "price": form_data["price"],
        "dlc_count": form_data["dlc_count"],
        "support_windows": int(form_data["windows"]),
        "support_mac": int(form_data["mac"]),
        "support_linux": int(form_data["linux"]),
        "achievements": form_data["achievements"],
        "tags_count": len(form_data["game_tags"]),
        "developers_count": len(form_data["developers"].split(',')) if form_data["developers"] else 0,
        "publishers_count": len(form_data["publishers"]),
        "categories_count": len(form_data["categories"]),
        "genres_count": len(form_data["genres"]),
        "languages_count": len(form_data["supported_languages"]),
        "full_audio_languages_count": len(form_data["full_audio_languages"]),
    }
    return numeric_features

def map_popularity_to_numeric(labels):
    ranges = []
    for label in labels:
        try:
            upper_bound = int(label.split('-')[1].replace(',', '').strip())
        except IndexError:
            upper_bound = 0
        ranges.append((label, upper_bound))
    sorted_ranges = sorted(ranges, key=lambda x: x[1])
    print(sorted_ranges)
    return {label: i for i, (label, _) in enumerate(sorted_ranges)}


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

        try:
            model, trained_columns, label_encoder = load_most_recent_model()
        except ValueError as e:
            return str(e), 500

        input_features = prepare_numeric_features(form_data)
        input_df = pd.DataFrame([input_features])

        # Predict popularity
        predicted_class_index = model.predict(input_df)[0]
        print("Original Labels from Label Encoder:")
        for i, label in enumerate(label_encoder.classes_):
            print(f"Class Index {i}: {label}")
        
        predicted_popularity = label_encoder.inverse_transform([predicted_class_index])[0]
        label_mapping = map_popularity_to_numeric(label_encoder.classes_)
        numeric_popularity = label_mapping[predicted_popularity]

        session['predicted_popularity'] = predicted_popularity
        session['numeric_popularity'] = numeric_popularity
        print(f"Predicted Popularity (Decoded): {predicted_popularity}")
        print(f"Mapped Numeric Popularity: {numeric_popularity}")

        # Calculate publishing fee
        publishing_fee = 200
        cut = 50

        if numeric_popularity > 0:
            publishing_fee -= numeric_popularity * 10
            cut -= numeric_popularity * 3

        publishing_fee = max(publishing_fee, 0)
        cut = max(cut, 0)

        print(f"Numeric Popularity: {numeric_popularity}")
        print(f"Publishing Fee: ${publishing_fee}")
        print(f"Cut Percentage: {cut}%")
        session['publishing_fee'] = publishing_fee
        session['cut'] = cut

        return redirect(url_for('publish_review'))

    return render_template('publish.html')

@app.route('/publish/review', methods=['GET', 'POST'])
def publish_review():
    if session.get('role') != 'developer/publisher':
        abort(403)
    form_data = session.get('form_data', {})
    predicted_popularity = session.get('predicted_popularity', None)
    publishing_fee = session.get('publishing_fee', None)
    cut = session.get('cut', None)

    if not form_data or predicted_popularity is None or publishing_fee is None:
        flash("You need to submit the form before accessing the review page.")
        return redirect(url_for('publish'))

    if request.method == 'POST':
        new_game = Game(
            name=form_data['game_name'],
            price=form_data['price'],
            description=form_data.get('description', 'No description provided'),
            developer=form_data.get('developers', ''),
            publisher=','.join(form_data.get('publishers', [])),
            release_date=datetime.now().date(),
            required_age=form_data['required_age'],
            dlc_count=form_data['dlc_count'],
            achievements=form_data['achievements'],
            windows_support=form_data['windows'] == 'yes',
            mac_support=form_data['mac'] == 'yes',
            linux_support=form_data['linux'] == 'yes',
            supported_languages=','.join(form_data.get('supported_languages', [])),
            full_audio_languages=','.join(form_data.get('full_audio_languages', [])),
            categories=','.join(form_data.get('categories', [])),
            genres=','.join(form_data.get('genres', [])),
            game_tags=','.join(form_data.get('game_tags', [])),
            publishing_fee = publishing_fee,
            cut = cut
        )
        db.session.add(new_game)
        db.session.commit()
        published_game = Game.query.filter_by(name=form_data['game_name']).first()
        if published_game:
            print(f"Published Game Details:")
            print(f"Name: {published_game.name}")
        session.pop('form_data', None)
        session.pop('predicted_popularity', None)
        session.pop('publishing_fee', None)
        session.pop('cut', None)
        return redirect(url_for('publish_success'))

    return render_template(
        'publish_cost.html',
        form_data=form_data,
        predicted_popularity=predicted_popularity,
        publishing_fee=publishing_fee,
        cut=cut
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
        return redirect(url_for('library'))

    if not request.args.get('confirm'):
        return render_template('purchase.html', game=game, user=user)

    return render_template('transaction.html', game=game, user=user)


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
    if not is_logged_in():
        flash('Please login to view game details.')
        return redirect(url_for('login'))

    game = Game.query.get_or_404(game_id)
    game_details = {
        "name": game.name,
        "price": game.price,
        "developer": game.developer,
        "publisher": game.publisher,
        "description": game.description,
        "required_age": game.required_age,
        "categories": game.categories.split(',') if game.categories else [],
        "genres": game.genres.split(',') if game.genres else [],
        "supported_platforms": {
            "Windows": game.windows_support,
            "Mac": game.mac_support,
            "Linux": game.linux_support,
        }
        
    }

    return render_template(
        'game_details.html',
        game=game_details,
        purchase_url=url_for('purchase', game_id=game.id)
    )





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

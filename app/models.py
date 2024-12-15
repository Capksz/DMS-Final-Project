from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    wallet_balance = db.Column(db.Numeric(10, 2), default=5000) 

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(6, 2), nullable=False)
    description = db.Column(db.Text, nullable=False)
    developer = db.Column(db.String(100))
    publisher = db.Column(db.String(100))
    release_date = db.Column(db.Date)
    required_age = db.Column(db.Integer, nullable=True, default=0)
    dlc_count = db.Column(db.Integer, nullable=True, default=0)
    achievements = db.Column(db.Integer, nullable=True, default=0)
    windows_support = db.Column(db.Boolean, nullable=True, default=False)
    mac_support = db.Column(db.Boolean, nullable=True, default=False)
    linux_support = db.Column(db.Boolean, nullable=True, default=False)
    supported_languages = db.Column(db.Text, nullable=True, default="")
    full_audio_languages = db.Column(db.Text, nullable=True, default="")
    categories = db.Column(db.Text, nullable=True, default="")
    genres = db.Column(db.Text, nullable=True, default="")
    game_tags = db.Column(db.Text, nullable=True, default="")
    def get_supported_languages(self):
        return self.supported_languages.split(',')

    def get_categories(self):
        return self.categories.split(',')

    def set_supported_languages(self, languages_list):
        self.supported_languages = ','.join(languages_list)

    def set_categories(self, categories_list):
        self.categories = ','.join(categories_list)


class LibraryGame(db.Model):  # weak entity dependent on user and game
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), primary_key=True)
    last_played = db.Column(db.DateTime)
    favorite_status = db.Column(db.Boolean, default=False)
    hours_played = db.Column(db.Numeric(6, 2), default=0.0)
    is_downloaded = db.Column(db.Boolean, default=False)


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    payment_method = db.Column(db.String(50))  # credit card or paypal
    status = db.Column(db.String(20), default='completed')
    amount = db.Column(db.Numeric(6, 2), nullable=False)

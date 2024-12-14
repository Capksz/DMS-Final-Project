from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
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


class LibraryGame(db.Model):  # weak entity depended on user
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    last_played = db.Column(db.DateTime)
    favorite_status = db.Column(db.Boolean, default=False)
    hours_played = db.Column(db.Numeric(6, 2), default=0.0)
    is_downloaded = db.Column(db.Boolean, default=False)
    game = db.relationship('Game', backref='library_entries')


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    payment_method = db.Column(db.String(50))  # credit card or paypal
    status = db.Column(db.String(20), default='completed')
    amount = db.Column(db.Numeric(6, 2), nullable=False)

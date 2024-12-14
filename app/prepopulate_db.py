from models import db, User

def prepopulate_db(app):
    """Populate the database with initial data."""
    with app.app_context():
        if User.query.first() is None:
            print("Prepopulating the database...")
            user1 = User(username="John Doe", email="john.doe@example.com")
<<<<<<< HEAD
            user1.set_password("test")
            user2 = User(username="Jane Smith", email="jane.smith@example.com")
            user2.set_password("test2")
            user3 = User(username="Alice Johnson", email="alice.johnson@example.com")
            user3.set_password("test3")
            db.session.add_all([user1, user2, user3])
=======
            user1.set_password("password123")

            user2 = User(username="Jane Smith", email="jane.smith@example.com")
            user2.set_password("password456")

            user3 = User(username="Alice Johnson", email="alice.johnson@example.com")
            user3.set_password("password789")
            db.session.add_all([user1, user2, user3])  # Add multiple users
>>>>>>> d1ffded21f67460d94056c623ac18692e1f05fe5
            db.session.commit()
            print("Database prepopulated successfully!")
        else:
            print("Database already has data, skipping prepopulation.")

from models import db, User

def prepopulate_db(app):
    """Populate the database with initial data."""
    with app.app_context():
        if User.query.first() is None:  # Check if the User table is empty
            print("Prepopulating the database...")
            user1 = User(username="John Doe", email="john.doe@example.com")
            user1.set_password("password123")

            user2 = User(username="Jane Smith", email="jane.smith@example.com")
            user2.set_password("password456")

            user3 = User(username="Alice Johnson", email="alice.johnson@example.com")
            user3.set_password("password789")
            db.session.add_all([user1, user2, user3])  # Add multiple users
            db.session.commit()
            print("Database prepopulated successfully!")
        else:
            print("Database already has data, skipping prepopulation.")

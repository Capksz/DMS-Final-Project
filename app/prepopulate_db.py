from models import db, User, Game
from datetime import date

def prepopulate_db(app):
    """Populate the database with initial data."""
    with app.app_context():
        should_populate = False

        if User.query.first() is None or Game.query.first() is None:
            should_populate = True
            print("Database needs population, starting process...")

        if should_populate:
            if User.query.first() is None:
                print("Adding users...")
                user1 = User(username="John Doe", email="john.doe@example.com", role="user")
                user1.set_password("test")

                user2 = User(username="Jane Smith", email="jane.smith@example.com", role="developer/publisher")
                user2.set_password("test2")

                user3 = User(username="Alice Johnson", email="alice.johnson@example.com", role="admin")
                user3.set_password("test3")

                db.session.add_all([user1, user2, user3])
                db.session.commit()
                print("Users added successfully!")

            if Game.query.first() is None:
                print("Adding games...")
                games = [
                    Game(
                        name='Cyberpunk 2077',
                        price=59.99,
                        description='An open-world action-adventure game set in a futuristic metropolis.',
                        developer='CD Projekt Red',
                        publisher='CD Projekt',
                        release_date=date(2020, 12, 10)
                    ),
                    Game(
                        name='Elden Ring',
                        price=69.99,
                        description='A challenging action RPG set in a vast fantasy world.',
                        developer='FromSoftware',
                        publisher='Bandai Namco',
                        release_date=date(2022, 2, 25)
                    ),
                    Game(
                        name='Red Dead Redemption 2',
                        price=49.99,
                        description='An epic tale of honor and loyalty in the dying days of the outlaw age.',
                        developer='Rockstar Games',
                        publisher='Rockstar Games',
                        release_date=date(2018, 10, 26)
                    )
                ]
                db.session.add_all(games)
                db.session.commit()
                print("Games added successfully!")

            print("Database population completed!")
        else:
            print("Database already populated, skipping initialization.")

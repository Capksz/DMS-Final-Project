# DMS-Final-Project

## How to Run the Program

1. Clone or download the project, open the folder with a code editor of choice.
2. Download these [files](https://drive.google.com/drive/folders/1GhwZqpVS8e4JrZPaApRALSExSvl8Pyfg?usp=sharing) (must be NYU authorized), put them in the ```DMS-Final-Project/ML``` folder.
3. In the code editor, open the terminal. Note that the terminal should be in the base folder DMS-Final-Project and not in one of the subdirectories like ML or app.
4. Run ```pipenv install``` to install the dependencies.
5. Run ```pipenv shell``` to start the virtual environment shell.
6. Run ```python ./ML/mltrainer.py```, this will create the ML files.
7. Run ```python ./app/app.py```, this will start the web app. Access the url provided by the shell.

## Logins

Due to time constraints, we have not implemented a registration function. The current default logins are:

- username="John Doe", password="test", email="john.doe@example.com", role="user"
- username="Jane Smith", passowrd="test2", email="jane.smith@example.com", role="developer/publisher"
- username="Alice Johnson", password="test3", email="alice.johnson@example.com", role="admin"

## Functionality

Given the 1 week time frame, we only implemented the core features that pertain to making money in a business. Therefore, these are the following features in our program:

1. Login
2. Purchase a game
3. Publish a game
4. View the details of a game
5. View your library of games

Note that downloading and register has not been implemented yet.

## Additional Notes
- Since the timeframe only allowed for a proof of concept, we used SQLite for the database to remove complex configurations with cloud servers or shared servers (e.g. MongoDB, Azure).
- We implemented the ORMs for extra credit using SQLAlchemy. The objects are in models.py, games.py and mltable.py, while mltrainer.py and app.py use the ORM for queries.
- The MLtrainer tries to emulate the idea of parsing data, storing it in a database and then fetching the data to train the model. We were able to do most of that except for the data parsing emulation due to the complexity of the Steam Games dataset code not always running correctly and the concurrent user dataset requiring scraping with delays. Therefore, we used the files given in step 3 which we had gathered beforehand as a proof of concept. Note that we had to store the files in such a way due to Github file size constraints.
- Ideally, we would set up a docker container with cron and run the mltrainer.py with a real parser to emulate scheduled data updates. However, this increases complexity and troubleshooting, so we avoided this for now.
- The "admin" role does not have any special privileges at the given moment since the core of the pricing is based on the ML model, user and publisher.
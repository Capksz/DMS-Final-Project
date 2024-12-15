import os
import json
import pandas as pd
import pickle
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sklearn.model_selection import KFold, cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer
from datetime import datetime, timezone
from games import ExternalGame, ConcurrentUserData
from mltable import AllDataModel, BasicInfoModel
from sqlalchemy import create_engine, Column, Integer, String, Float, LargeBinary, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = 'sqlite:///external_data.db'
MLMODEL_URL = 'sqlite:///mlmodel.db'

engine = create_engine(DATABASE_URL)
ml_engine = create_engine(MLMODEL_URL)

Session = sessionmaker(bind=engine)
MLSession = sessionmaker(bind=ml_engine)

session = Session()
ml_session = MLSession()

# Step 1: Load Data into Database

def load_json_to_db(json_path):
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as file:
            dataset = json.load(file)
        for app_id, game in dataset.items():
            game_entry = ExternalGame(
                game_id=app_id,
                name=game['name'],
                release_date=game.get('release_date'),
                estimated_owners=game.get('estimated_owners'),
                peak_ccu=game.get('peak_ccu'),
                required_age=game.get('required_age'),
                price=game.get('price'),
                dlc_count=game.get('dlc_count'),
                support_windows=game.get('windows', False),
                support_mac=game.get('mac', False),
                support_linux=game.get('linux', False),
                positive_votes=game.get('positive'),
                negative_votes=game.get('negative'),
                achievements=game.get('achievements'),
                recommendations=game.get('recommendations'),
                average_playtime=game.get('average_playtime_forever'),
                average_playtime_2w=game.get('average_playtime_2weeks'),
                median_playtime=game.get('median_playtime_forever'),
                median_playtime_2w=game.get('median_playtime_2weeks'),
                developers=",".join(game.get('developers', [])),
                publishers=",".join(game.get('publishers', [])),
                categories=",".join(game.get('categories', [])),
                genres=",".join(game.get('genres', [])),
                tags=",".join(game.get('tags', [])),
                languages=",".join(game.get('supported_languages', [])),
                full_audio_languages=",".join(game.get('full_audio_languages', [])),
            )
            session.add(game_entry)
        session.commit()


def load_parquet_to_db(parquet_path):
    if os.path.exists(parquet_path):
        concurrent_data = pd.read_parquet(parquet_path)
        for _, row in concurrent_data.iterrows():
            data_entry = ConcurrentUserData(
                game_id=row['game_id'],
                avg_concurrent_users=row.get('Average Concurrent User Over Time'),
                net_gain=row.get('Net Gain'),
                avg_peak_concurrent_users=row.get('Average Peak Concurrent User Over Time'),
                min_peak_players=row.get('Minimum Peak Players'),
                max_peak_players=row.get('Maximum Peak Players'),
                log_avg_concurrent_users=row.get('Log Average Concurrent User Over Time'),
                log_avg_peak_users=row.get('Log Average Peak Concurrent User Over Time'),
                avg_gain=row.get('Average Gain'),
                log_avg_gain=row.get('Log Average Gain'),
                positive_gain_count=row.get('Positive Gain Count'),
                negative_gain_count=row.get('Negative Gain Count'),
            )
            session.add(data_entry)
        session.commit()


# Step 2: Preprocess Data

def preprocess_data():
    external_games = pd.read_sql(session.query(ExternalGame).statement, session.bind)
    concurrent_users = pd.read_sql(session.query(ConcurrentUserData).statement, session.bind)
    external_games['game_id'] = external_games['game_id'].astype(int)
    concurrent_users['game_id'] = concurrent_users['game_id'].astype(float).astype(int)

    merged_df = pd.merge(external_games, concurrent_users, on="game_id", how="inner")

    for column in ['tags', 'developers', 'publishers', 'categories', 'genres', 'languages', 'full_audio_languages']:
        merged_df[column] = merged_df[column].apply(lambda x: x.split(',') if isinstance(x, str) else [])

    merged_df['upvote_ratio'] = merged_df['positive_votes'] / (merged_df['positive_votes'] + merged_df['negative_votes'])
    merged_df['tags_count'] = merged_df['tags'].apply(len)
    merged_df['developers_count'] = merged_df['developers'].apply(len)
    merged_df['publishers_count'] = merged_df['publishers'].apply(len)
    merged_df['categories_count'] = merged_df['categories'].apply(len)
    merged_df['genres_count'] = merged_df['genres'].apply(len)
    merged_df['languages_count'] = merged_df['languages'].apply(len)
    merged_df['full_audio_languages_count'] = merged_df['full_audio_languages'].apply(len)
    merged_df.drop(['tags', 'developers', 'publishers', 'categories', 'genres', 'languages', 'full_audio_languages'], axis=1, inplace=True)

    return merged_df


# Step 3: Train and Save Model

def train_and_save_model(processed_df):
    """
    Train both the all-data model and the basic-info model,
    and save them in their respective tables.
    """

    label_encoder = LabelEncoder()
    processed_df['estimated_owners'] = label_encoder.fit_transform(processed_df['estimated_owners'])

    all_data_features = processed_df.drop(columns=[
        'estimated_owners', 'game_id', 'name', 'release_date', 'positive_votes', 'negative_votes'
    ]).columns.tolist()

    basic_info_features = processed_df.drop(columns=[
        'estimated_owners', 'game_id', 'name', 'release_date', 'positive_votes', 'negative_votes',
        'avg_concurrent_users', 'net_gain', 'avg_peak_concurrent_users', 'min_peak_players',
        'max_peak_players', 'log_avg_concurrent_users', 'log_avg_peak_users', 'avg_gain',
        'log_avg_gain', 'peak_ccu', 'median_playtime', 'recommendations', 'positive_gain_count',
        'negative_gain_count', 'average_playtime', 'median_playtime_2w', 'average_playtime_2w', 'upvote_ratio'
    ]).columns.tolist()

    # Train All Data Model
    print("Training All-Data Model...")
    X_all = processed_df[all_data_features]
    y = processed_df['estimated_owners']
    model_all = DecisionTreeClassifier(random_state=42, max_depth=5)

    kfold = KFold(n_splits=5, shuffle=True, random_state=42)
    accuracy_scores_all = cross_val_score(model_all, X_all, y, scoring='accuracy', cv=kfold)
    mean_accuracy_all = accuracy_scores_all.mean()

    model_all.fit(X_all, y)

    # Serialize and save the all-data model
    serialized_all_data_model = pickle.dumps((model_all, all_data_features, label_encoder))  # Include feature names and encoder
    all_data_model_entry = AllDataModel(
        model_name="all_data_model",
        model_data=serialized_all_data_model,
        accuracy=mean_accuracy_all,
        version="v1.0",
        created_at=datetime.now(timezone.utc)
    )
    ml_session.add(all_data_model_entry)
    print(f"All-Data Model saved successfully with accuracy {mean_accuracy_all:.4f}.")

    # Train Basic Info Model
    print("Training Basic-Info Model...")
    X_basic = processed_df[basic_info_features]
    model_basic = DecisionTreeClassifier(random_state=42, max_depth=5) 

    accuracy_scores_basic = cross_val_score(model_basic, X_basic, y, scoring='accuracy', cv=kfold)
    mean_accuracy_basic = accuracy_scores_basic.mean()

    model_basic.fit(X_basic, y)

    # Serialize and save the basic-info model
    serialized_basic_info_model = pickle.dumps((model_basic, basic_info_features, label_encoder))  # Include feature names and encoder
    basic_info_model_entry = BasicInfoModel(
        model_name="basic_info_model",
        model_data=serialized_basic_info_model,
        accuracy=mean_accuracy_basic,
        version="v1.0",
        created_at=datetime.now(timezone.utc)
    )
    ml_session.add(basic_info_model_entry)
    print(f"Basic-Info Model saved successfully with accuracy {mean_accuracy_basic:.4f}.")

    ml_session.commit()




load_json_to_db('ML/games.json')
load_parquet_to_db('ML/part-00000-2b76e765-63a7-4945-bb86-64dae48a3445-c000.snappy.parquet')

processed_df = preprocess_data()
train_and_save_model(processed_df)

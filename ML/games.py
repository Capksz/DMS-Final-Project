from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class ExternalGame(Base):
    __tablename__ = 'external_games'

    game_id = Column(String, primary_key=True)
    name = Column(String(255), nullable=False)
    release_date = Column(String, nullable=True)
    estimated_owners = Column(Integer, nullable=True)
    peak_ccu = Column(Integer, nullable=True)
    required_age = Column(Integer, nullable=True)
    price = Column(Float, nullable=True)
    dlc_count = Column(Integer, nullable=True)
    support_windows = Column(Boolean, nullable=False, default=False)
    support_mac = Column(Boolean, nullable=False, default=False)
    support_linux = Column(Boolean, nullable=False, default=False)
    positive_votes = Column(Integer, nullable=True)
    negative_votes = Column(Integer, nullable=True)
    achievements = Column(Integer, nullable=True)
    recommendations = Column(Integer, nullable=True)
    average_playtime = Column(Float, nullable=True)
    average_playtime_2w = Column(Float, nullable=True)
    median_playtime = Column(Float, nullable=True)
    median_playtime_2w = Column(Float, nullable=True)
    upvote_ratio = Column(Float, nullable=True)
    developers = Column(Text, nullable=True)
    publishers = Column(Text, nullable=True)
    categories = Column(Text, nullable=True)
    genres = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)
    languages = Column(Text, nullable=True)
    full_audio_languages = Column(Text, nullable=True)

class ConcurrentUserData(Base):
    __tablename__ = 'concurrent_users'

    game_id = Column(String, primary_key=True)
    avg_concurrent_users = Column(Float, nullable=True)
    net_gain = Column(Float, nullable=True)
    avg_peak_concurrent_users = Column(Float, nullable=True)
    min_peak_players = Column(Integer, nullable=True)
    max_peak_players = Column(Integer, nullable=True)
    log_avg_concurrent_users = Column(Float, nullable=True)
    log_avg_peak_users = Column(Float, nullable=True)
    avg_gain = Column(Float, nullable=True)
    log_avg_gain = Column(Float, nullable=True)
    positive_gain_count = Column(Integer, nullable=True)
    negative_gain_count = Column(Integer, nullable=True)

DATABASE_URL = 'sqlite:///external_data.db'
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

from sqlalchemy import create_engine, Column, Integer, String, Float, LargeBinary, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

Base = declarative_base()

class BasicInfoModel(Base):
    __tablename__ = 'basic_info_models'

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(255), nullable=False)
    model_data = Column(LargeBinary, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=lambda: datetime.now(timezone.utc)) 
    accuracy = Column(Float, nullable=False)
    version = Column(String(50), nullable=False) 

class AllDataModel(Base):
    __tablename__ = 'all_data_models'

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(255), nullable=False)
    model_data = Column(LargeBinary, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=lambda: datetime.now(timezone.utc)) 
    accuracy = Column(Float, nullable=False)
    version = Column(String(50), nullable=False) 

DATABASE_URL = 'sqlite:///mlmodel.db'
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

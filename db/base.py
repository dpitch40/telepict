from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import Config

Base = declarative_base()

engine = create_engine(Config.DB_URL)
Session = sessionmaker(bind=engine)

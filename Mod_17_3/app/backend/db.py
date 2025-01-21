from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

engine = create_engine("sqlite:///taskmanager.db")
session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass

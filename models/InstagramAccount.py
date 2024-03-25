from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class InstagramAccount(Base):
    __tablename__ = 'instagram_accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column("username", String, unique=True)
    password = Column('password', String)


    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
from sqlalchemy import Column, Integer, String, Boolean
from database import Base, session
from utils import load_accounts

class InstagramAccount(Base):
    __tablename__ = 'instagram_accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column("username", String(255), unique=True)
    password = Column('password', String(255))
    locked = Column("locked", Boolean, default=False) 


    def __init__(self, username, password, locked=False):
        self.username = username
        self.password = password
        self.locked = locked

    @classmethod
    def create(cls, username, password):
        new_account = cls(username=username, password=password)
        session.add(new_account)
        session.commit()

    @classmethod
    def get_account_choice(cls):
         account = session.query(cls).filter_by(locked=False).with_for_update().first()
         account.locked = True
         session.commit()
         return account
    
    @classmethod
    def unlock_account_choice(cls, account):
         old_account = session.query(cls).get(account.id)
         old_account.locked = False
         session.commit()
         old_account

    @staticmethod
    def seed_data_accounts():
            
        if not session.query(InstagramAccount).first():
                # Seed data
                # Check if seed data exists
                accounts = load_accounts()
                new_accounts = []
                if accounts:
                    for a in accounts:
                        new_account = InstagramAccount.create(username=a["username"], password=a["password"])
                        new_accounts.append(new_account)
                
                session.add_all(new_accounts)
                session.commit()
        else:
                return
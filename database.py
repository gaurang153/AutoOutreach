from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists
from dotenv import dotenv_values
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote

Base = declarative_base()

# Load environment variables from .env file
env_vars = dotenv_values('.env')

user = env_vars.get('DB_USER')
password = env_vars.get('DB_PASS')
host = env_vars.get('DB_HOST')
port = env_vars.get('DB_PORT')
name = env_vars.get('DB_NAME')

url = 'mysql://{0}:{1}@{2}:{3}/{4}'.format(user, quote(password), host, port, name)
engine = create_engine(url)

if not database_exists(url):
        create_database(url)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
        
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists
from dotenv import dotenv_values
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote

Base = declarative_base()

# Load environment variables from .env file
env_vars = dotenv_values('.env')
url = ""

dockerized = env_vars.get('DOCKERIZED')
if dockerized == "true":
        user = env_vars.get('MYSQL_USER')
        password = env_vars.get('MYSQL_PASSWORD')
        host = env_vars.get('MYSQL_HOST')
        name = env_vars.get('MYSQL_DB')
        port = env_vars.get('MYSQL_PORT')
        url = 'mysql://{0}:{1}@{2}/{3}'.format(user, quote(password), host, name)

else:
        user = env_vars.get('DB_USER')
        password = env_vars.get('DB_PASS')
        host = env_vars.get('DB_HOST')
        port = env_vars.get('DB_PORT')
        name = env_vars.get('DB_NAME')
        url = 'mysql://{0}:{1}@{2}:{3}/{4}'.format(user, quote(password), host, port, name)



print(f"SQL Connection String: {url}")
engine = create_engine(url)

if not database_exists(url):
        create_database(url)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
        
from sqlalchemy import create_engine, DDL
from sqlalchemy_utils import create_database, database_exists
from dotenv import dotenv_values
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote
from sqlalchemy.engine.reflection import Inspector
import os

Base = declarative_base()

# Load environment variables from .env file
env_vars = dotenv_values('.env')
url = ""

dockerized = os.environ['DOCKERIZED']
if dockerized == "true":
        user = os.environ['MYSQL_USER']
        password = os.environ['MYSQL_PASSWORD']
        host = os.environ['MYSQL_HOST']
        name = os.environ['MYSQL_DB']
        port = os.environ['MYSQL_PORT']
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


Session = sessionmaker(bind=engine)
session = Session()

def add_missing_columns(engine, metadata, table_name):

    # Get the table object
    your_table = metadata.tables[table_name]

     # Get the columns from the database
    inspector = Inspector.from_engine(engine)
    db_columns = inspector.get_columns(table_name)
    db_column_names = [col['name'] for col in db_columns]

    # Check for missing columns and add them
    for column in your_table.columns:
        if column.name not in db_column_names:
            # Create a DDL object for ALTER TABLE
            ddl = DDL(f"ALTER TABLE {table_name} ADD COLUMN {column.name} {column.type} DEFAULT NULL")
            # Execute the DDL statement
            with engine.begin() as connection:
                connection.execute(ddl)
def init_db():
        import models.InstagramAccount
        import models.ProfileOutreach
        Base.metadata.create_all(engine)
        tables = ["profile_outreach", "instagram_accounts"]
        # Add Missing Columns
        for table in tables:
              add_missing_columns(engine=engine, metadata=Base.metadata, table_name=table)

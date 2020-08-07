from sqlalchemy import create_engine
import pymysql
import os

host = os.environ['DB_HOST']
user = os.environ['DB_USER']
passw = os.environ['DB_PASSWORD']
schema = os.environ['DB_SCHEMA']
db_connection_str = "mysql+pymysql://{0}:{1}@{2}/{3}".format(user, passw, host, schema)
db_connection = create_engine(db_connection_str)
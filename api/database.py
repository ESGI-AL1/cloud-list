import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from google.cloud.sql.connector import Connector, IPTypes

db_user = os.environ.get("CLOUD_SQL_USERNAME")
db_password = os.environ.get("CLOUD_SQL_PASSWORD")
db_name = os.environ.get("CLOUD_SQL_DATABASE")
db_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")


Base = declarative_base()
connector = Connector()


def init_connection_pool(connector: Connector):
    def getconn():
        conn = connector.connect(
            db_connection_name,
            "pymysql",
            user=db_user,
            password=db_password,
            db=db_name,
            ip_type=IPTypes.PUBLIC,
        )
        return conn

    engine = create_engine("mysql+pymysql://", creator=getconn)
    return engine


engine = init_connection_pool(connector)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

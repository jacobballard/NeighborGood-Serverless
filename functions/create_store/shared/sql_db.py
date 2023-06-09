import sqlalchemy
import os


db_user = os.environ["DB_USER"]
db_pass = os.environ["DB_PASS"]
db_name = os.environ["DB_NAME"]
unix_socket_path = os.environ[
    "INSTANCE_UNIX_SOCKET"
]

db =sqlalchemy.create_engine(
    sqlalchemy.engine.url.URL.create(
        drivername="postgresql+pg8000",
        username=db_user,
        password=db_pass,
        database=db_name,
        query={"unix_sock": f"{unix_socket_path}/.s.PGSQL.5432"},
    ),
    
)
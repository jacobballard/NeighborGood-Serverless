# import sqlalchemy
# import os


# db_user = os.environ["DB_USER"]
# db_pass = os.environ["DB_PASS"]
# db_name = os.environ["DB_NAME"]
# unix_socket_path = os.environ[
#     "INSTANCE_UNIX_SOCKET"
# ]

# db =sqlalchemy.create_engine(
#     sqlalchemy.engine.url.URL.create(
#         drivername="postgresql+pg8000",
#         username=db_user,
#         password=db_pass,
#         database=db_name,
#         query={"unix_sock": f"{unix_socket_path}/.s.PGSQL.5432"},
#     ),
    
# )
from sqlalchemy import create_engine
db_user = 'jacobballard'
db_pass = 'postgres'
db_name = 'postgres'
db_host = 'localhost'
db_port = '5432'

connection_string = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
db = create_engine(connection_string)
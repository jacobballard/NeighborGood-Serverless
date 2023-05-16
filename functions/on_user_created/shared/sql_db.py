from sqlalchemy import create_engine

db_user = 'postgres'
db_pass = 'postgres'
db_name = 'postgres'
db_host = 'localhost'
db_port = '5432'

connection_string = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
db = create_engine(connection_string)

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine('postgresql://postgres:20000404@localhost/delivery_database',
                       echo=True)
Base = declarative_base()
session = sessionmaker() # for CRUD
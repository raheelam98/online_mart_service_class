# user_service - db_connector.py

from app.settings import DB_URL
from sqlmodel import create_engine, SQLModel, Session

from typing import Annotated
from fastapi import Depends, FastAPI

### ========================= *****  ========================= ###

# Set up the database connection
connection_string = str(DB_URL).replace(
    "postgresql", "postgresql+psycopg"
)

# Create an engine for the database connection
engine = create_engine(
    connection_string, connect_args={}, pool_recycle=300
)

# function, before the yield, will be executed before the application starts
# create session to get memory space in db
def get_session():
    with Session(engine) as session:
        yield session

# Dependency injection to get a session
DB_SESSION = Annotated[Session, Depends(get_session)]

# Function to create the database and tables
async def create_db_and_tables(app: FastAPI):
    # Print a message indicating the start of table creation
    print(f'Create Tables ...  {app} ') 
    # Create all tables based on the defined SQLModel metadata 
    SQLModel.metadata.create_all(engine) 
    # Yield control back to the caller (generator function) 
    yield  


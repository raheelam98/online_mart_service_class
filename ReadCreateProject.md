# Online Mart - User Service

## DATABASE_URL    
 
.env  (Write secret credential.)

```bash
DATABASE_URL=postgresql://database_username:password@hostname:port/database_name?sslmode=require
```

**Note:-** When copying the database URL (DB_URL), ensure that only the owner has access to add, update, and delete data. Developers should have limited write access.

Note :- default port : 5432

## Contecting with database

setting.py

```bash
from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()  

DATABASE_URL = config("DATABASE_URL", cast=Secret)
```

**======================== ** ** ========================**

## Create Database Schema using SQLModel

UserBase defines the shared attributes for a user, while User extends it to represent a database table with user_id as the primary key.

```bash
# Define the UserBase and User models
class UserBase(SQLModel):
    user_name: str
    user_address: str
    user_email: str
    user_password: str    

class User(UserBase, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
```

**======================== ** ** ========================**

## Create a Table with SQLModel - Use the Engine

```bash
# Set up the database connection
connection_string = str(DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)

# Create an engine for the database connection
engine = create_engine(connection_string, connect_args={}, pool_recycle=300)

# Function to create the database and tables
async def create_db_and_tables():
    print(f'Creating Tables ...')
    # Create all the database tables
    SQLModel.metadata.create_all(engine)

# function, before the yield, will be executed before the application starts
# create session to get memory space in db
def get_session():
    with Session(engine) as session:
        yield session

# Dependency injection to get a session
DB_Session = Annotated[Session, Depends(get_session)]
```

## FastAPI

```bash
# Lifespan function provided by FastAPI (creates DB table at program startup)
# It creates the table only once; if the table already exists, it won't create it again
async def life_span(app: FastAPI):
    print("Call create tables function during lifespan startup...")
    await create_db_and_tables()  # Properly await table creation
    yield  # Lifespan generator is working correctly

# Create FastAPI instance
app = FastAPI(lifespan=life_span, title='Product API')

```

**Explanation**

#### Contection String

```bash
connection_string = str(DATABASE_URL).replace("postgresql", "postgresql+psycopg")
``` 

This code modifies the DATABASE_URL so it can use the psycopg driver when connecting to a PostgreSQL database:

**str(DATABASE_URL):** Converts DATABASE_URL into a string representation, which is necessary for the replacement to be performed.

**.replace("postgresql", "postgresql+psycopg"):** Changes "postgresql" to "postgresql+psycopg" in the connection string. This ensures that SQLAlchemy knows to use the psycopg driver to connect to the PostgreSQL database.

**psycopg** driver is a popular and efficient library for interacting with PostgreSQL databases in Python

#### create a connection to the database

```bash
engine = create_engine(connection_string, connect_args={}, pool_recycle=300)
``` 

**create_engine()** SQLModel Function (create a connection to the database)

**Detail Description**

**connection_string:** Specifies the database URL (e.g., the type of database and its location).

**connect_args={}:** Additional arguments for the connection (often used for settings specific to the type of database).

**pool_recycle=300:** Prevents stale connections by recycling (re-establishing) them every 300 seconds to avoid issues like timeout.

####  Create all tables defined in the model

```bash
SQLModel.metadata.create_all(engine)
``` 

**SQLModel.metadata.create_all()**

**.metadata:** attribute keeps track of all the models (tables)

**.create_all():** Uses .metadata to create the tables in your database

**.engine:** SQLAlchemy database engine that points to your database.

**Detail Description**

SQLModel: It’s a library built on top of SQLAlchemy and Pydantic that simplifies working with SQL databases in Python, commonly used with FastAPI for defining database models.

.metadata: This attribute of SQLModel contains metadata about all the defined tables, such as table names and their columns. It acts as a registry for your models.

.create_all(): This method, when called, uses the metadata to generate SQL commands that create the necessary tables in the connected database. Essentially, it will ensure all your defined models have corresponding tables.

### Session

```bash
def get_session():
    with Session(engine) as session:
        yield session
``` 

This function creates a session object using the provided engine for database connectivity, and it yields this session. It ensures that the session is properly created and closed after use. 

**- with** statement ensures that resources are properly managed, like automatically closing the session after it's used.

**- yield** allows a function to return a value and then pause its execution, resuming right where it left off the next time it’s called. This is what makes a generator function. It’s perfect for situations where you want to iterate through a sequence without storing the entire thing in memory

The code in the function before yield will be executed each time the generator is called.

## Function to create the database and tables
```bash
# Function to create the database and tables
async def create_db_and_tables(app: FastAPI):
    # Print a message indicating the start of table creation
    print(f'Create Tables ...  {app} ') 
    # Create all tables based on the defined SQLModel metadata 
    SQLModel.metadata.create_all(engine) 
    # Yield control back to the caller (generator function) 
    yield  
```


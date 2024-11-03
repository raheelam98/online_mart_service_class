from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, Annotated, List
from datetime import date
from app.settings import DB_URL

### ========================= *****  ========================= ###

class ProductModel(SQLModel):
    product_name: str
    product_price : float
    is_available: bool = False 
    product_description: str | None
    product_add_date : date = Field(default=date.today())     

class Product(ProductModel, table=True):
    product_id: Optional[int] = Field(default=None, primary_key=True)

### ========================= *****  ========================= ###

# Set up the database connection
connection_string = str(DB_URL).replace(
    "postgresql", "postgresql+psycopg"
)

# Create an engine for the database connection
engine = create_engine(
    connection_string, connect_args={}, pool_recycle=300
)

# Function to create the database and tables
async def create_db_and_tables():
    print(f'Creating Tables ...')
    # Create all the database tables
    SQLModel.metadata.create_all(engine)

# The code in the function before yield will be executed each time the generator is called.    
# create session to get memory space in db
def get_session():
    with Session(engine) as session:
        yield session

# Dependency injection to get a session
DB_Session = Annotated[Session, Depends(get_session)]

### ========================= *****  ========================= ###

# Lifespan function provided by FastAPI (creates DB table at program startup)
# It creates the table only once; if the table already exists, it won't create it again
async def life_span(app: FastAPI):
    print("Call create tables function during lifespan startup...")
    await create_db_and_tables()  # Properly await table creation
    yield  # Lifespan generator is working correctly

# Create FastAPI instance
app = FastAPI(lifespan=life_span, title='Product API')


@app.get('/')
def get_root_route():
    return "Product Service"

### ========================= *****  ========================= ###

# Function to add a product into the database
def add_product_into_db(form_data: ProductModel, session: Session):
    # Create a new Product object using the details provided in form_data
    product = Product(**form_data.model_dump())

    # Add the product to the session
    session.add(product)
    # Commit the session to save the product to the database
    session.commit()
    # Refresh the session to retrieve the new product data
    session.refresh(product)
    # Debugging
    print("New product added:", product)
    return product


# POST route to add a new product
@app.post('/api/add_product')
def add_product(new_product: ProductModel, session: DB_Session):
    # Call function to add product
    added_product = add_product_into_db(new_product, session)
    print("Add product route ...", added_product)
    return added_product

### ========================= *****  ========================= ###

# Function to retrieve user data from the database
def get_product_from_db(session: DB_Session):
    # Create a SQL statement to select all products
    statement = select(Product)
    # Execute the statement and get the list of users
    product_list = session.exec(statement).all()

    # If no users found, raise an HTTPException with status code 404
    if not product_list:
        raise HTTPException(status_code=404, detail="Not Found")
    # Otherwise, return the list of users
    else:
        return product_list


# API endpoint to get product
@app.get('/api/get_product')
def get_product(session: DB_Session):
    # Call the function to retrieve data from the database
    users = get_product_from_db(session)
    # Return the list of product
    return users

### ========================= *****  ========================= ###

def update_product_from_db(selected_id: int, update_form_data: ProductModel, session: DB_Session):
    # Create a SQL statement to select the product with the given ID
    statement = select(Product).where(Product.product_id == selected_id)
    # Execute the statement and get the selected product
    selected_product = session.exec(statement).first()

    # If the product is not found, raise an HTTPException with status code 404
    if not selected_product:
        raise HTTPException(status_code=404, detail="Not Found")
    
    # Update the product's details with the data from the form
    # database                    = form data
    selected_product.product_name = update_form_data.product_name
    selected_product.product_description = update_form_data.product_description
    selected_product.product_price = update_form_data.product_price
    selected_product.is_available = update_form_data.is_available

    # Add the updated product to the session
    session.add(selected_product)
    # Commit the session to save the changes to the database
    session.commit()
    # Refresh the session to retrieve the updated  data
    session.refresh(selected_product)
    return selected_product


@app.put('/api/update_product')
def update_product(id:int, product_detail: ProductModel, session: DB_Session):
    # Call the function to retrieve data from the database
    user = update_product_from_db(id, product_detail, session)
    return user

### ========================= *****  ========================= ###

# Function to delete a user from the database
def delete_product_from_db(delete_id: int, session: DB_Session):
    # Retrieve the product from the database using the given ID
    product = session.get(Product, delete_id)

    # If the product is not found, raise an HTTPException with status code 404
    if not product:
        raise HTTPException(status_code=404, detail="Not Found")
    # Delete the product from the session
    session.delete(product)
    # Commit the session to save the changes to the database
    session.commit()
    return 'Product deleted'


# API endpoint to delete a product
@app.delete('/api/delete_product')
def delete_product(id: int, session: DB_Session):
    # Call function to delete the product from the database
    deleted_user = delete_product_from_db(id, session)
    return f'Product id {id} has been successfully deleted'

### ========================= *****  ========================= ####

def search_product_by_name(name: str, session: Session) -> List[Product]:
    products = session.exec(
        select(Product).where(Product.product_name.ilike(f"%{name}%"))
    ).all()

    if not products:
        raise HTTPException(status_code=404, detail="No products found with this name.")
    
    return products

@app.get("/api/search_product_by_name/{product_name}", response_model=List[Product])
def search_product(name: str, session: DB_Session):
    return search_product_by_name(name, session)

### ========================= *****  ========================= ####



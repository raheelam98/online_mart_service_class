# user_service -  user_service/app/main.py

from fastapi import FastAPI, HTTPException, status, Depends
from sqlmodel import select, Session
import jwt
from datetime import timedelta, datetime
from typing import Optional
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.db.db_connector import create_db_and_tables, DB_SESSION, get_session
from app.models.user_model import User, UserModel, Token, UserUpdateModel
from app.settings import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY

app = FastAPI(lifespan= create_db_and_tables)     

@app.get('/')
def root_route_user():
    return "User Service"

### ========================= *****  ========================= ###


# CryptContext is used to handle password hashing and verification using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer is used to provide the OAuth2 token URL for token generation
oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")

# Function to create a JWT (JSON Web Token) access token
def create_access_token(data: dict, expire_delta: Optional[timedelta] = None):
    to_ecode = data.copy()  # Create a copy of the data to encode
    
    if expire_delta:
        # Set the expiration time if provided
        expire = datetime.utcnow() + expire_delta 
    else:
        # Default expiration time
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_ecode.update({"exp": expire})  # Add the expiration time to the data

    # Encode the JWT with the specified secret key and algorithm
    encode_jwt = jwt.encode(to_ecode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encode_jwt  # Return the encoded JWT

### ========================= *****  ========================= ###

# Function to hash a password using bcrypt
def hash_password(password: str) -> str:
    return pwd_context.hash(password)  # Hash the password using the bcrypt hashing algorithm

# Function to verify a plain text password against a hashed password
def verify_password(plainText: str, hashedPassword: str) -> bool:
    return pwd_context.verify(plainText, hashedPassword)  # Verify if the plain text password matches the hashed password

### ========================= *****  ========================= ###

# Route to get the current user from the token
def get_current_user(token: str = Depends(oauth2_schema)):
    try:
        # Decode the JWT (JSON Web Token) using the secret key and specified algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Retrieve the email from the decoded payload
        email: str = payload.get("sub")

        # If the email is not found in the payload, raise an unauthorized exception
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
    except jwt.PyJWTError:
        # If there's an error decoding the token, raise an unauthorized exception
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )  
    
    # Return the extracted email
    return email

### ========================= *****  ========================= ###

# Route to register user
@app.post("/register_user", response_model=User)
async def register_user(new_user: UserModel, session: DB_SESSION):

    # Check if user already exists in the database by email
    db_user = session.exec(select(User).where(User.user_email == new_user.user_email)).first()
    
    # If the user already exists, raise an HTTP 409 Conflict exception with a detailed message
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists. Please try registering with a different email address."
        )
    
    # Create a new user object with the provided data and hashed password
    user = User(
        user_name=new_user.user_name,
        user_email=new_user.user_email,
        user_password=hash_password(new_user.user_password),
        user_address=new_user.user_address,
        user_country=new_user.user_country,
        phone_number=new_user.phone_number
    )

    # Add the new user to the session
    session.add(user)
    session.commit()  # Commit to save the new user to the database
    session.refresh(user)  # Refresh the user instance to get the latest data from the database
    
    # Return the created user object as the response
    return user


### ========================= *****  ========================= ###

# Route to login user

@app.post("/login", response_model=Token)
def login_for_access_token(
    token_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    # Find the user in the database by email
    user = session.exec(select(User).where(User.user_email == token_data.username)).first()

    # Validate user credentials
    if not user or not verify_password(token_data.password, user.user_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Define token expiry
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Create the access token with user email as "sub" (subject)
    access_token = create_access_token(
        data={"sub": user.user_email}, 
        expire_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

### ========================= *****  ========================= ###

@app.get("/user/get_profile", response_model=User)
def read_auth_user_profile(current_user_email: str = Depends(get_current_user), session: Session = Depends(get_session)):
    # Retrieve the user from the database using the provided email
    user = session.exec(select(User).where(User.user_email == current_user_email)).first()

    # If the user is not found, raise a 404 (Not Found) exception
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return the user details as the response
    return user

### ========================= *****  ========================= ###

# Route to update profile with authentication

@app.patch("/update_profile", response_model=User)
async def update_auth_user_profile(
    profile_data: UserUpdateModel, 
    current_user_email=Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    # Retrieve the current user from the database using the provided email
    select_current_user = session.exec(select(User).where(User.user_email == current_user_email)).first()

    # If the user is not found, raise a 404 (Not Found) exception
    if not select_current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    
    # Convert the profile_data model to a dictionary, excluding unset fields
    update_profile = profile_data.model_dump(exclude_unset=True)

    # Iterate over the key-value pairs in the updates dictionary and set new values for the user attributes
    for key, value in update_profile.items():
        setattr(select_current_user, key, value)

    # Add the updated user to the session
    session.add(select_current_user) 
    session.commit()  # Commit the transaction to save changes to the database

    # Return a success message
    return {"message": "Profile updated successfully"} 

    
### ========================= *****  ========================= ###

# Function to retrieve user data from the database
def get_user_from_db(session: DB_SESSION):
    # Create a SQL statement to select all users
    statement = select(User)
    # Execute the statement and get the list of users
    user_list = session.exec(statement).all()

    # If no users found, raise an HTTPException with status code 404
    if not user_list:
        raise HTTPException(status_code=404, detail="Not Found")
    # Otherwise, return the list of users
    else:
        return user_list
    

# API endpoint to get users
@app.get('/api/get_users')
def get_user(session: DB_SESSION):
    # Call the function to retrieve user data from the database
    users = get_user_from_db(session)
    # Return the list of users
    return users

### ========================= *****  ========================= ###

@app.delete("/users/{user_id}", response_model=User)
def delete_user(user_id: int, session: DB_SESSION):
    db_user = session.get(User, user_id)  # Retrieve user by ID
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(db_user)  # Delete the user from the session
    session.commit()  # Commit the transaction
    return db_user

### ========================= *****  ========================= ###

### ========================= *****  ========================= ###



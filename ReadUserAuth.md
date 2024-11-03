# Authentication

```shell
pip install fastapi sqlmodel bcrypt pyjwt 

poetry add fastapi sqlmodel bcrypt pyjwt
```

```shell
poetry add pydantic[email]
```

```shell
pip install python-multipart

poetry add python-multipart
```

**generate a secure random secret key**

```shell
openssl rand -hex 16
```

**`passlib`** library provides secure password hashing utilities, and `CryptContext` is a convenient way to manage hashing schemes.
```bash
pip install passlib

poetry add passlib 
```

**`jose`** library in Python provides tools for handling JSON Web Tokens (JWTs), especially for encoding, decoding, and verifying them. `python-jose` to create and verify tokens.
```bash
pip install python-jose
```

**Encoding: `jwt.encode()`** creates a signed JWT using the specified payload, secret key, and algorithm.
```bash
# Encoding the payload to create a token
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
```

**Decoding: `jwt.decode()`** verifies the token and extracts its payload. If the token is expired or invalid, it raises an error.

```bash
# Encoding the payload to create a token
decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
```

### Create a JWT access token
```bash
from typing import  Optional
import jwt
from datetime import datetime, timedelta

SECRET_KEY = 'secret key'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES =60

# Function to create a JWT access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()  # Create a copy of the data to encode
    if expires_delta:
        # Set the expiration time if provided
        expire = datetime.utcnow() + expires_delta
    else:
        # Default expiration time
        expire = datetime.utcnow() + ACCESS_TOKEN_EXPIRE_MINUTES
    to_encode.update({"exp": expire})  # Add the expiration time to the data
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Encode the JWT
    return encoded_jwt
```

### Get the current user from the provided token
```bash
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

SECRET_KEY = 'secret key'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES =60

# OAuth2PasswordBearer is used to provide the OAuth2 token URL for token generation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Function to get the current user from the provided token
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # Decode the JWT token using the secret key and specified algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract the email (subject) from the decoded payload
        email: str = payload.get("sub")
        
        # If the email is not found in the payload, raise an unauthorized exception
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except jwt.PyJWTError:
        # If there's an error decoding the token, raise an unauthorized exception
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    # Return the extracted email
    return email
```

#### Passlib is a password hashing library for Python
**`passlib`** library provides secure password hashing utilities, and `CryptContext` is a convenient way to manage hashing schemes.
```bash
pip install passlib
```

```bash
from passlib.context import CryptContext

# CryptContext is used to handle password hashing and verification using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to hash a password
def passwordIntoHash(password: str) -> str:
    return pwd_context.hash(password)

# Function to verify a plain text password against a hashed password
def verifyPassword(plainText: str, hashedPassword: str) -> bool:
    return pwd_context.verify(plainText, hashedPassword)
```

**Hashing:`pwd_context.hash()`** hashes the password using the specified hashing scheme (e.g., bcrypt).

**Verification: `pwd_context.verify()`** checks if a provided password matches the stored hash, returning True if it matches and False otherwise.

### Register User / Singin
```bash
from fastapi import FastAPI, HTTPException, status
from sqlmodel import select
from passlib.context import CryptContext

from app.db.db_connector import create_db_and_tables, DB_SESSION
from app.models.user_model import User, UserModel

app = FastAPI(lifespan= create_db_and_tables)

# CryptContext is used to handle password hashing and verification using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to hash a password using bcrypt
def hash_password(password: str) -> str:
    return pwd_context.hash(password)  # Hash the password using the bcrypt hashing algorithm

# Function to verify a plain text password against a hashed password
def verify_password(plainText: str, hashedPassword: str) -> bool:
    return pwd_context.verify(plainText, hashedPassword)  # Verify if the plain text password matches the hashed password

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
```

### Login for access toke
```bash
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import SQLModel, Session, select

from app.db.db_connector import  get_session # import from database connector
from app.models.user_model import User  # import from user model
from app.main import verifyPassword, create_access_token # from above code

SECRET_KEY = 'secret key'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES =60

class Token(SQLModel):
    access_token: str
    token_type: str

# OAuth2PasswordBearer is used to provide the OAuth2 token URL for token generation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    # Retrieve the user from the database using the provided email
    user = session.exec(select(User).where(User.user_email == form_data.username)).first()
    
    # If the user does not exist or the password is incorrect, raise an unauthorized exception
    if not user or not verifyPassword(form_data.password, user.user_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Set the token expiration time
    access_token_expires = ACCESS_TOKEN_EXPIRE_MINUTES
    
    # Create the access token with the user's email as the subject
    access_token = create_access_token(data={"sub": user.user_email}, expires_delta=access_token_expires)
    
    # Print the access token (for debugging purposes)
    print("access_token ...", access_token)
    
    # Return the access token and its type
    return {"access_token": access_token, "token_type": "bearer"}
```

#### calculates the expiration time as a Unix timestamp in seconds
```bash
expire = datetime.now(timezone.utc) + expires_delta
expire_delta = int(expire.timestamp())
```
it easy to store, compare, or include in a JWT (JSON Web Token) payload where a timestamp format is typically required for the exp (expiration) claim

**Calculate Expiration Time**
```bash
expire = datetime.now(timezone.utc) + expires_delta
```
`datetime.now(timezone.utc)` creates a timestamp of the current time in UTC.

`expires_delta` is a timedelta object, often representing the duration a token should be valid (e.g., 1 hour, 24 hours).

`+ expires_delta` adds this duration to the current time to determine the final expiration time (expire).

**Convert Expiration Time to Unix Timestamp**
```bash
expire_delta = int(expire.timestamp())
```

`expire.timestamp()` converts the datetime object to a Unix timestamp, which is the number of seconds that have elapsed since January 1, 1970 (UTC).

`int(...)` converts this float to an integer, stripping away any fractional seconds.

#### Automatically Generating a Unique kid Value for Each Model Instance

```bash
kid: str = Field(default_factory=lambda: uuid.uuid4().hex)
```
This is commonly used in fields where a unique ID (such as kid in a JWT header) is required

 `uuid.uuid4()` generates a random UUID (Universally Unique Identifier).

 `.hex` converts the UUID into a hexadecimal string representation, which is a 32-character string.

`default_factory=lambda:` ... ensures that a new unique kid is generated automatically each time without needing an explicit assignment.

```bash
for key, value in updates.items():
        setattr(select_user, key, value) 
```

#### Python update object from dictionary - Iterable Unpacking 

```bash
def update_user(user_id: int, user_update: UserUpdateModel, session: DB_SESSION):
    db_user = session.get(User, user_id)  # Retrieve user by ID
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user_update.model_dump(exclude_unset=True)  # Get the user update data
    for key, value in user_data.items():
        setattr(db_user, key, value)  # Update the user attributes
    session.add(db_user)  # Add the user to the session
    session.commit()  # Commit the transaction
    session.refresh(db_user)  # Refresh the user instance
    return db_user      
```

`model_dump(exclude_unset=True)` on a Pydantic model, it creates a dictionary from the model, but only includes the fields that have been set by the user. Any fields that haven't been given a value are left out.

`updates.items()` This line generates a view object that displays a list of a dictionary's key-value tuple pairs.

`for key, value in updates.items():` This begins a loop that will iterate through each key-value pair in the updates dictionary.

`setattr(db_user, key, value)` This function sets the attribute of db_userr specified by key to value.

**`setattr`**  is a built-in Python function used to set the value of an object's attribute.

## Tutorial

**OAuth2**

[OAuth2 with Password (and hashing), Bearer with JWT tokens](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)

[OAuth2 scopes](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/)

[Get Current User](https://fastapi.tiangolo.com/tutorial/security/get-current-user/#create-a-get_current_user-dependency)

[Body - Updates](https://fastapi.tiangolo.com/tutorial/body-updates/#partial-updates-recap)

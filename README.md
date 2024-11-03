

poetry —-version  

create a virtual environment and install all the dependencies specified in your pyproject.toml file, but it won’t install the project itself as a package.
```bash
poetry install --no-root
```

**Poetry Commands**

**Create Poetry Project**

```bash
poetry new project_name 
```

add drivers mac
```shell
poetry add fastapi uvicorn\[standard\] 
```

add drivers for db
```shell
poetry add sqlmodel psycopg
```

add drivers (one line command) mac
```shell
poetry add fastapi sqlmodel uvicorn\[standard\] psycopg 
```

add drivers (one line command) window
```shell
poetry add fastapi uvicorn[standard] sqlmodel psycopg 
```

**`jose`** library in Python provides tools for handling JSON Web Tokens (JWTs), especially for encoding, decoding, and verifying them. `python-jose` to create and verify tokens.
```bash
pip install python-jose
```

**`passlib`** library provides secure password hashing utilities, and `CryptContext` is a convenient way to manage hashing schemes.
```bash
pip install passlib

poetry add passlib 
```

run poetry app
```shell
poetry run uvicorn folder_name.file_name:app --port 8000 --reload
```

```shell
poetry run uvicorn app.main:app --reload
```


#### Methods HTTP (Hypertext Transfer Protocol)

GET: Retrieves data from a server.

POST: Sends data to the server to create a new resource. 

PUT: Updates or replaces an existing resource on the server.

DELETE: Removes a resource from the server.

PATCH: Applies partial modifications to a resource.

## Generator Function
* iterate on element one by one
* stop after each iteration
* remember old iteration value (last iterate value)
* next iterate 
    * go farward from last iterate value

```bash
def generator_name(arg):
    # statements
    yield something

## Generator Function
def my_range(start:int , end:int , step: int=1):
    for i in range(start,end+1,step):
        yield i # Generator fucntion

a = my_range(1,10)
print(a)
print(list(a))
```   

**`yield`** keyword is used to produce a value from the generator.


#### Difference between return and yield Python

**return** sends a value and terminates a function
**yield** in Python used to create a generator function
-statement only pauses the execution of the function
-yield statements are executed when the function resumes its execution.
**Note:** The generator is NOT a normal function. It remembers the previous state like local variables (stack).

## Tutorials


[Simple Hero API with FastAPI](https://sqlmodel.tiangolo.com/tutorial/fastapi/simple-hero-api/)

[Using Dataclasses](https://fastapi.tiangolo.com/advanced/dataclasses/)

[Why Aren't We Getting More Data](https://sqlmodel.tiangolo.com/tutorial/fastapi/relationships/#why-arent-we-getting-more-data)

[Dependencies with yield](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/)

[Lifespan Events](https://fastapi.tiangolo.com/advanced/events/)

[SQL (Relational) Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/)# online_mart_service_class

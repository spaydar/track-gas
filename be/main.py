from asyncpg.exceptions import UniqueViolationError
import configparser
import databases
from sql_queries import *
from typing import List

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, constr, EmailStr



#### CONFIG ####

config = configparser.ConfigParser()
config.read('config.ini')

psql_username = config['POSTGRES']['username']
psql_password = config['POSTGRES']['password']
psql_host = config['POSTGRES']['host']
psql_port = config['POSTGRES']['port']
psql_db_name = config['POSTGRES']['db_name']

postgres_conn_str = 'postgresql://' + psql_username + ":" + psql_password + \
    '@' + psql_host + ':' + psql_port + '/' + psql_db_name



#### DATABASE ####

db = databases.Database(postgres_conn_str)

async def setup_database():
    
    await db.connect()
    
    for create_ext in create_ext_queries:
    
        await db.execute(query=create_ext)
    
    email_domiain_oid = await db.fetch_one(domain_select_email)
    
    if not email_domiain_oid:
    
        await db.execute(query=create_domain_email)
    
    await db.execute(query=create_users_table)



#### PYDANTIC MODELS ####

class UserBase(BaseModel):
    email_addr: EmailStr
    first_name: constr(max_length=20, strip_whitespace=True)
    last_name: constr(max_length=20, strip_whitespace=True)

class UserIn(UserBase):
    password: constr(min_length=8, max_length=30)

    class Config:
        schema_extra = {
            "example": {
                "email_addr": "johndoe@gmail.com",
                "first_name": "John",
                "last_name": "Doe",
                "password": "abcdef123"
            }
        }

class UserOut(UserBase):
    id: int



#### API ####

app = FastAPI()

# EVENTS #

@app.on_event("startup")
async def startup():
    await setup_database()

@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()

# ENDPOINTS #

@app.get(
    "/users",
    response_model=List[UserOut]
)
async def get_all_users():
    
    try:
        
        result = await db.fetch_all(users_select_all)
        
        print("Result of SELECT query in GET /users", result)
        
        return result if result else []
    
    except Exception as ex:
        
        print("Exception caught in GET /users", type(ex), ex)
        
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post(
    "/user",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED
)
async def create_user(user: UserIn):
    
    try:
        
        result = await db.execute(users_table_insert, values=user.dict())
        
        print("Result of INSERT statement in POST /user", result)
        
        return { **user.dict(), "id": result }
    
    except UniqueViolationError as ex:
        
        print("UniqueViolationError caught in POST /user", ex)
        
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail="There is already an account associated with the given email")
    
    except Exception as ex:
        
        print("Exception caught in POST /user", type(ex), ex)
        
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/check_password")
async def check_password(
    email_addr: EmailStr, 
    password: constr(min_length=8, max_length=30)
    ):
    
    try:

        id = await db.fetch_one(users_select_id_by_email)

        if not id:

            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                detail="No record found for given email address")

    except Exception as ex:

        print("Exception caught in POST/check_password", type(ex), ex)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # TODO CHECK IF PASSWORD MATCHES HASH FOR GIVEN ID
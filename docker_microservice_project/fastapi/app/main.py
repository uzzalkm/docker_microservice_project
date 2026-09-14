from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware  # for cors on react/angular
from ariadne.asgi import GraphQL
from app.graphql.schema import schema
from app.routers.order_router import order_router

app = FastAPI()

# Existing REST APIs
# app.include_router(student_router)


origins = [                   # for cors on react/angular
    "http://localhost:3000",  # React
    "http://localhost:4200",  # Angular
    "http://127.0.0.1:5500",  # VS Code Live Server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


'''
users = [
    {
        "id":1,
        "name":"John",
        "city":"New York"
    },
    {
        "id":2,
        "name":"David",
        "city":"London"
    }
]

class Student(BaseModel):
    id:int
    name:str
    department:str
    
      
@app.get("/")
def home():
    return {
        "message": "Welcome to FastAPI REST API"
    }
    
@app.get("/users")
def get_users():
    return users
    
@app.post("/student")
def create_student(student:Student):

    return {
        "message":"Student Created",
        "data":student
    }
'''

# REST APIs
app.include_router(order_router)

@app.get("/")

def home():
    return {
        "message": "Welcome to FastAPI REST API"
    }

graphql = GraphQL(schema, debug=True)
app.mount("/graphql", graphql)
from fastapi import FastAPI
from fleximongo import FlexiMongo

app = FastAPI()

fleximongo = FlexiMongo(
    url="mongodb://localhost:27017", 
    cors_origins=["http://127.0.0.1:5500"]
)

fleximongo.init_app(app)

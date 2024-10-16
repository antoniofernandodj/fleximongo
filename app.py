from fastapi import FastAPI
from fleximongo import FlexiMongo

app = FastAPI()

fleximongo = FlexiMongo(url="mongodb://localhost:27017")
fleximongo.init_app(app)

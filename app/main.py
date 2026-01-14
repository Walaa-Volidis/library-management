from fastapi import FastAPI
from app.database import engine
from app.models import book

app = FastAPI(title="Library API")

book.Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Library API is running"}

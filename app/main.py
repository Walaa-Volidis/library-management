from fastapi import FastAPI
from app.database import engine
from app.models import book
from app.api.book import router as books_router

app = FastAPI(title="Library API")

book.Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Library API is running successfully!"}
app.include_router(books_router)

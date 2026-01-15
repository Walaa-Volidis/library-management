from fastapi import FastAPI
from app.api.book import router as books_router
from app.api.member import router as members_router

app = FastAPI(title="Library API")

@app.get("/")
def root():
    return {"message": "Library API is running successfully!"}


app.include_router(books_router)
app.include_router(members_router)
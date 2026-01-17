from fastapi import FastAPI
from app.routers.book import router as books_router
from app.routers.member import router as members_router
from app.routers.borrow import router as borrows_router

app = FastAPI(title="Library API")

@app.get("/")
def root():
    return {"message": "Library API is running successfully!"}


app.include_router(books_router)
app.include_router(members_router)
app.include_router(borrows_router)
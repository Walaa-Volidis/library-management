import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.database import Base
from app.main import app
from app.routers.book import get_db

SQLITE_DATABASE_URL = 'sqlite:///./test.db'
engine = create_engine(SQLITE_DATABASE_URL, connect_args={'check_same_thread': False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def client():
    def get_test_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = get_test_db
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_book_data():
    return {'title': 'Clean Code', 'author': 'Robert C. Martin', 'isbn': '978-0132350884', 'total_copies': 5}

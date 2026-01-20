from app.database import Base
from .book import Book
from .member import Member
from .borrow import BorrowRecord
from .users import Users

metadata = Base.metadata
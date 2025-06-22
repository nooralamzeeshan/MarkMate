from sqlalchemy import create_engine, MetaData
from databases import Database

# SQLite database file ka path (local file banega)
DATABASE_URL = "sqlite:///./markmate.db"

# Async database instance (FastAPI ke liye)
database = Database(DATABASE_URL)

# Metadata: table structure store karta hai
metadata = MetaData()

# Engine: actual DB connection object
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite ke liye ye zaruri hai
)

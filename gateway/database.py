import sqlalchemy as _sql
import sqlalchemy.ext.declarative as _declarative
import sqlalchemy.orm as _orm
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


# Retrieve environment variables for postgres
postgres_host = os.environ.get("POSTGRES_HOST")
postgres_db = os.environ.get("POSTGRES_DB")
postgres_user = os.environ.get("POSTGRES_USER")
postgres_password = os.environ.get("POSTGRES_PASSWORD")

# Retrieve environment variables for mysql
mysql_host = os.environ.get("MYSQL_HOST")
mysql_db = os.environ.get("MYSQL_DB")
mysql_user = os.environ.get("MYSQL_USER")
mysql_password = os.environ.get("MYSQL_PASSWORD")
mysql_port = os.environ.get("MYSQL_PORT")


# PostgreSQL server connection url'
DATABASE_URL = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}/{postgres_db}"

# Mysql server connection url
# DATABASE_URL = f"mysql+pymysql://root:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"


engine = _sql.create_engine(DATABASE_URL)
SessionLocal = _orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = _declarative.declarative_base()

def create_database():
    # Create database tables
    return Base.metadata.create_all(bind=engine)

def get_db():
    # Dependency to get a database session
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
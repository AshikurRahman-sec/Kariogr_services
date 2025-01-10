import sqlalchemy.orm as _orm

from models import oauth_model



async def get_user_by_email(email: str, db: _orm.Session):
     # Retrieve a user by email from the database
    return db.query(oauth_model.User).filter(oauth_model.User.email == email).first()
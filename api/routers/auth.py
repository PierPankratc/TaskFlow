from authx import AuthX, AuthXConfig
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from api.config import JWT_SECRET_KEY
from api.password import hash_password, verify_password
from api.schemas import UserSchema
from db.create_db import get_db_connect
from db.models import Users

config = AuthXConfig()
config.JWT_SECRET_KEY = JWT_SECRET_KEY
config.JWT_ACCESS_COOKIE_NAME = "access_token"
config.JWT_TOKEN_LOCATION = ["cookies"]
config.JWT_COOKIE_CSRF_PROTECT = False

security = AuthX(config=config)

router = APIRouter(tags=["Пользователи"])


@router.post("/login")
def login(
    user: UserSchema,
    response: Response,
    db: Session = Depends(get_db_connect),
):
    db_user = db.query(Users).filter(Users.name == user.name).first()

    if not db_user:
        db_user = Users(name=user.name, password=hash_password(user.password))
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    elif not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = security.create_access_token(uid=str(db_user.id))
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)

    return {"token": token}

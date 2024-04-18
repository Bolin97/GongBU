from datetime import datetime, timedelta, timezone
import os
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

SERCET_KEY = os.getenv("SERCET_KEY")
TOKEN_EXPIRATION_DELTA = 1  # days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def veify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def generate_jwt_token(identifier):
    with open("./s.txt", "w") as f:
        f.write(SERCET_KEY)
    expiration = datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRATION_DELTA)
    return jwt.encode(
        {"sub": identifier, "exp": expiration}, SERCET_KEY, algorithm="HS256"
    )


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
from fastapi import status


async def get_current_identifier(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SERCET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
        
SIGN_UP_TOKEN_PATH = os.path.join(
    os.path.dirname(__file__), "sign_up_token.txt"
)

import hashlib
import random
def generate_sign_up_token():
    with open(SIGN_UP_TOKEN_PATH, "w") as f:
        f.write(
            hashlib.md5(
                str(datetime.now().timestamp()).encode() + random.randbytes(16)
            ).hexdigest()
        )

def get_sign_up_token():
    with open(SIGN_UP_TOKEN_PATH, "r") as f:
        return f.read()

def sign_up_token_exists():
    return os.path.exists(SIGN_UP_TOKEN_PATH)


from sqlalchemy.orm import Query
from fastapi import Depends
from sqlalchemy import or_


def accessible(query: Query, identifier: str) -> Query:
    model = query.column_descriptions[0]["entity"]
    return query.filter(or_(model.owner == identifier, model.public == True))


def owned(query: Query, identifier: str) -> Query:
    model = query.column_descriptions[0]["entity"]
    return query.filter(model.owner == identifier)


def owns(query: Query, identifier: str) -> bool:
    return owned(query, identifier).count() > 0


def check_access(query: Query, identifier: str) -> bool:
    return accessible(query, identifier).count() > 0

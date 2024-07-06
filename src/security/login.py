"""This module contains functions to deal with password and generate token."""
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext
import secrets
import string
from config.project_setting import security_config
from src.data_models.auth import TokenData
from src.data_models.user import User
from src.util.authorities import Authorities

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify the plain password is the same as the hashed password.

        Returns:
            True if the password matched the hash, else False.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(plain_password: str) -> str:
    """Get the hashed password with CryptContext.hash()."""
    return pwd_context.hash(plain_password)

def generate_password(length=12):
    characters = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(characters) for i in range(length))
    return password

def get_access_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
    """Get access token from the user information.

        Parameters:
            user: an User object of target user.
            expires_delta: a datetime.timedelta object that shows how long the access token expires.

        Returns:
            an access token string.
    """
    issued = datetime.utcnow()
    if expires_delta:
        expire = issued + expires_delta
    else:
        expire = issued + timedelta(minutes=security_config.access_token_expire_minutes)

    scopes = [user.authority]
    if user.authority == Authorities.SYS_ADMIN:
        scopes.append(Authorities.MEMBER_USER)
        
    token_data = TokenData(
        sub=user.email_address,
        scopes=scopes,
        account=user.account,
        user_id=str(user.id),
        iat=issued,
        exp=expire
    )
    encoded_jwt = jwt.encode(token_data.dict(), security_config.secret_key, algorithm=security_config.algorithm)
    return encoded_jwt

"""This module contains functions to get and check authentication information."""
from typing import List
from typing_extensions import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt

from config.project_setting import security_config
from src.data_models.auth import TokenData
from src.data_models.user import User
from src.service.user import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login")
user_service = UserService()


def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from JWT token and check if the security scopes match,
        typically called by FastAPI.Depends or FastAPI.Security.

        Parameters:
            security_scopes: the required scopes.
            token: JWT token get from request header.

        Returns:
            user: the User object parsed from the JWT token.

        Raises:
            HTTPException: Raises a 401_UNAUTHORIZED if the token can not be validate,
                           or the scopes do not match.

        Examples:
            Requires to use the API with the authority of ADMIN_GROUP:
                >>> Security(get_current_user, scopes=[Authorities.ADMIN_GROUP])
            Requires no authorities to use the API:
                >>> Depends(get_current_user)
    """
    authenticate_header = "Bearer"
    if security_scopes.scopes:
        authenticate_header += f" scope=\"{security_scopes.scope_str}\""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_header},
    )

    try:
        payload = jwt.decode(token, security_config.secret_key, algorithms=[security_config.algorithm])
        email_address: str = payload.get("sub")
        if email_address is None:
            raise credentials_exception
        token_data = TokenData(**payload)
    except JWTError:
        raise credentials_exception

    if not _check_scopes(security_scopes.scopes, token_data.scopes):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": authenticate_header},
        )

    user = user_service.get_user_by_email_address(email_address)
    if not User:
        raise credentials_exception
    return user

def _check_scopes(expected_scopes: List[str], actual_scopes: List[str]) -> bool:
    """Check if all the expected scopes match to the actual ones.

        Parameters:
            security_scopes: the required scopes.
            token: JWT token get from request header.

        Returns:
            True if the scopes matched, else False.
    """
    actual_scopes_set = set(actual_scopes)
    for scope in expected_scopes:
        if not scope in actual_scopes_set:
            return False

    return True


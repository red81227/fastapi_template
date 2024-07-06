"""This module contains function to create the login router."""
# pylint: disable=unused-variable
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from config.project_setting import security_config
from src.security.login import get_access_token
from src.service.user import UserService

def create_login_router():
    """Create the login API router.
    Returns an instance of fastapi.routing.APIRouter.
    """
    router = APIRouter()
    user_service = UserService()

    @router.post("/login")
    def login(form_data: OAuth2PasswordRequestForm = Depends()):
        user = user_service.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(
            minutes=security_config.access_token_expire_minutes)
        access_token = get_access_token(
            user=user, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    
    
    return router

"""This module contains function to create the authentication router."""
# pylint: disable=unused-variable
from fastapi import APIRouter, Depends, HTTPException, status

from config.logger_setting import log
from src.data_models.auth import ChangePasswordRequest
from src.data_models.common import BaseResponse
from src.data_models.user import User
from src.security.auth import get_current_user
from src.service.user import UserService


def create_auth_router():
    """Create the auth API router.
    Returns an instance of fastapi.routing.APIRouter.
    """
    router = APIRouter()
    user_service = UserService()

    @router.post("/change_password", response_model=BaseResponse)
    def change_password(
            change_password_request: ChangePasswordRequest,
            current_user: User = Depends(get_current_user)
        ):
        """Change the password for the User which credentials are used to perform this REST API call.
        Be aware that previously generated JWT tokens will be still valid until they expire.

            Password Rule:
                Contains at least ONE upper case, and ONE lower case alphabet.
                And should be with length in between 8 to 12 characters.
        """
        user = None
        try:
            user = user_service.change_user_password(change_password_request, current_user)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not change password"
            )
        return BaseResponse()

    @router.post("/logout")
    def logout(current_user: User = Depends(get_current_user)):
        """Special API call to record the 'logout' of the user to the Audit Logs.
        Since platform uses JWT,
        the actual logout is the procedure of clearing the JWT token on the client side.
        """
        log.info(f"{current_user.account} logged out.")

    return router

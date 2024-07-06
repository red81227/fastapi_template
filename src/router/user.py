"""This module contains function to create the user router."""
# pylint: disable=unused-variable,blacklisted-name,consider-using-enumerate
from fastapi import APIRouter, HTTPException, Security, status
from src.data_models.common import BaseResponse
from src.util.authorities import Authorities
from pydantic.types import UUID1

from src.data_models.user import CreateUserRequest, UpdateUserRequest, User
from config.logger_setting import log
from src.security.auth import (
    get_current_user
)
from src.service.user import UserService


def create_user_router():
    """Create the recognition result API router.
    Returns an instance of fastapi.routing.APIRouter.
    """
    router = APIRouter()
    service = UserService()

    @router.post("/", response_model=User)
    def create_user(
            create_user_request: CreateUserRequest,
            current_user: User = Security(get_current_user, scopes=[Authorities.SYS_ADMIN])
        ):
        """Create a User with default password."""
        try:
            created_user = service.create_user_with_authority(create_user_request, Authorities.MEMBER_USER)
            if not created_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Could not create user"
                )
            return created_user
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            log.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            )

    @router.get("/all", response_model=list[User])
    def get_users(
            current_user: User = Security(get_current_user, scopes=[Authorities.SYS_ADMIN])
        ):
        """Get all Users."""
        try:
            users = service.find_all()
            if not users:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Could not get users"
                )
            return users
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            log.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            )

    @router.put("/{user_id}", response_model=User)
    def update_user(
            user_id: UUID1,
            update_user_request: UpdateUserRequest,
            current_user: User = Security(get_current_user, scopes=[Authorities.SYS_ADMIN])
        ):
        """Update the User with provided new User object,
        based on the provided user_id.
        """
        try:
            updated_user = service.update_user(str(user_id), update_user_request)
            if not updated_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Could not update user"
                )
            return updated_user
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            log.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            )

    @router.delete("/{user_id}", response_model=BaseResponse)
    def delete_user(
            user_id: UUID1,
            current_user: User = Security(get_current_user, scopes=[Authorities.SYS_ADMIN])
        ):
        """Delete the User based on the provided user_id. 
            Will also delete the user's room and devices.
        """
        try:
            if service.delete_user(str(user_id)):
                return BaseResponse()
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Could not delete user"
                )
            
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            log.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            )

    return router

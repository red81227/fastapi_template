"""This module contains class to for user service."""
from typing import List, Optional

from src.dao.user_dao import UserDao
from src.data_models import entities
from src.data_models.auth import ChangePasswordRequest
from src.data_models.user import CreateUserRequest, UpdateUserRequest, User
from src.security.login import generate_password, get_password_hash, verify_password

from src.util.function_utils import generate_id

class UserService:
    """Provide functions related to User entity."""
    def __init__(self):
        self.user_dao = UserDao()

    def create_user_with_authority(self, create_user_request: CreateUserRequest, authority: str) -> Optional[User]:
        """Create an user with given authority.

        Parameters:
            create_user_request: the create user request object, indicates information to create entities.

        Returns:
            status of creating user
        """
        user_entity = entities.User(
            id=str(generate_id()),
            authority=authority,
            **create_user_request.dict()
        )
        if not user_entity.hashed_password:
            new_password = generate_password(12)
            user_entity.hashed_password = get_password_hash(new_password)
        if not self.user_dao.save(user_entity):
            return None

        user = User(**user_entity.dict())
        user.additional_info = f"defult password (change it):{new_password}"
        return user

    def find_all(self) -> Optional[List[User]]:
        """Get all users.

        Returns:
            a list of User objects.
        """
        user_entities = self.user_dao.find_all()
        if not user_entities:
            return None
        return [User(**user_entity.dict()) for user_entity in user_entities]

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get the user based on provided user_id.

        Parameters:
            user_id: id to get the user.

        Returns:
            an User object.
        """
        user_entity_result = self.user_dao.find_by_id(user_id)
        if not user_entity_result:
            return None
        return User(**user_entity_result.dict())

    def authenticate_user(self, email_address: str, password: str) -> Optional[User]:
        """Check user authentication. Raise 401 Error if there is \
            no such user with email_address, \
            or the password is not correct.

            Parameters:
                email_address: email address to get hashed password.
                password: unhashed password to be authenticated.

            Returns:
                user: the User object with correct authentication.
        """

        user_entity = self._get_user_entity_by_email_address(email_address)
        if not user_entity or not verify_password(password, user_entity.hashed_password):
            return None
        return User(**user_entity.dict())
    
    def get_user_by_email_address(self, email_address: str) -> Optional[User]:
        """Get the user based on provided email_address.

        Parameters:
            email_address: email address to get the user.

        Returns:
            an User object.
        """
        user_entity_result = self._get_user_entity_by_email_address(email_address)
        if not user_entity_result:
            return None
        return User(**user_entity_result.dict())

    def _get_user_entity_by_email_address(self, email_address: str) -> Optional[entities.User]:
        """Get the user entity based on provided email_address.

        Parameters:
            email_address: email address to get the user.

        Returns:
            an entities.User object.
        """
        user_entity_result = self.user_dao.find_by_email_address(email_address)
        return user_entity_result

    def update_user(self, user_id: str, update_user_request: UpdateUserRequest) -> Optional[User]:
        """Update the user based on provided user_id.

        Parameters:
            user_id: id of user to update.
            update_user_request: the update user request object, indicates information to update entities.

        Returns:
            the updated User object.
        """
        user_entity = self.user_dao.find_by_id(user_id)
        new_user_entity = entities.User(
            id=user_id,
            authority=user_entity.authority,
            **update_user_request.dict()
        )
        updated_user_entity = self.user_dao.update_by_id(user_id, new_user_entity)
        if not updated_user_entity:
            return None
        return User(**updated_user_entity.dict())

    def delete_user(self, user_id: str) -> bool:
        """Delete the user based on provided user_id.

        Parameters:
            user_id: id of user to delete.

        Returns:
            the status of deleting user.
        """
        # delete user room
        room_entities = self.room_service.get_all_user_id_rooms(user_id=user_id)
        if room_entities:
            for room_entity in room_entities:
                self.room_service.delete_room(room_entity.id)
        
        # delete user device
        device_entities = self.device_service.get_all_devices_by_user_id(user_id = user_id)
        if device_entities:
            for device_entity in device_entities:
                self.device_service.delete_device(device_entity.id)

        return self.user_dao.delete_by_id(user_id)


    def change_user_password(self, change_password_request: ChangePasswordRequest, user: User):
        """Change user's password after verifying its current password.

            Parameters:
                change_password_request: the change password request object,\
                    includes old and new password.
                user: the User object whose password is to be changed.

            Returns:
                the updated User object.
        """

        hashed_new_password = get_password_hash(change_password_request.new_password)

        updated_user_entity = self.user_dao.update_password(str(user.id), hashed_new_password)
        if not updated_user_entity:
            return None
        return User(**updated_user_entity.dict())

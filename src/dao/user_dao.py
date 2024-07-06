"""This module contains class to for user dao."""
from typing import List, Optional

from config.logger_setting import log
from src.dao.abstract_dao import AbstractDao
from src.data_models.entities import TableName, User


class UserDao(AbstractDao):
    """An class for user dao.

    Attributes:
        table_name: str
            name of the binding table.
        conn_pool: ConnectionPool
            a ConnectionPool instance to get / put psycopg2 connection.

    Methods:
        save(data: EntityBaseModel) -> bool:
            Insert a row of data.
        find_all_by_group_id(group_id: str) -> List[User]:
            Read all rows of data that have the given group id.
        find_by_id(target_id: str) -> Optional[List[Tuple]]:
            Read a row of data by id.
        find_by_email_address(email_address: str) -> Optional[User]:
            Read a row of data by email address.
        update_by_id(user_id: str, new_user: User) -> bool:
            Update whole row of data with input by user id.
        delete_by_id(target_id: str) -> bool:
            Delete a row of data by id.
    """
    def __init__(self):
        super().__init__(TableName.USERS, User)

    def find_all(self) -> List[User]:
        """Read all rows of data.

        Returns:
            device_entities: all of Devices in a list.
        """
        target_columns = ", ".join(self.col_names)
        result_tuples = self._find_all(target_columns)
        if not result_tuples:
            return []
        device_entities = list(map(self.to_entity_model, result_tuples))
        return device_entities

    def find_by_id(self, user_id: str) -> Optional[User]:
        """Read a row of data by user id.

        Parameters:
            user_id: id of target user.

        Returns:
            user_entity: an User entity if there is corresponding data to user_id, \
                else return None.
        """
        target_columns = ", ".join(self.col_names)
        result_tuple = self._find_by_id(user_id, target_columns)
        if not result_tuple:
            return None
        user_entity = self.to_entity_model(result_tuple)
        return user_entity

    def find_by_email_address(self, email_address: str) -> Optional[User]:
        """Read a row of data by email address.

        Parameters:
            email_address: email address of target user.

        Returns:
            user_entity: an User entity if there is corresponding data to email_address, \
                else return None.
        """
        filter_data = {"email_address": email_address}
        target_columns = ", ".join(self.col_names)
        result_tuples = self._find(filter_data, target_columns)
        if not result_tuples:
            return None
        user_entity = self.to_entity_model(result_tuples[0])
        return user_entity

    def update_by_id(self, user_id: str, new_user: User) -> Optional[User]:
        """Update whole row of data with input by user id.

        Parameters:
            user_id: id of target user.
            new_user: an User entity to update database with.

        Returns:
            an User entity in database after update.
        """
        filter_data = {"id": user_id}
        result_tuples = self._update(new_user, filter_data)
        if not result_tuples:
            return None

        user_entity = self.to_entity_model(result_tuples[0])
        return user_entity

    def update_password(self, user_id: str, hashed_new_password: str) -> Optional[User]:
        """Update a user's password by user id.

        Parameters:
            user_id: id of target user.
            hashed_new_password: a hashed string to set as new password.

        Returns:
            an User entity in database after update.
        """
        result_tuple = None
        sql_text = f"UPDATE {self.table_name} "\
                   f"SET hashed_password = %s "\
                   f"WHERE id = %s "\
                   f"RETURNING {', '.join(self.col_names)}"
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(sql_text, (hashed_new_password, user_id,))
            result_tuple = cursor.fetchone()
            conn.commit()
        except Exception as exc:
            conn.rollback()
            log.error(f"Exception when UPDATE data from table({self.table_name}): {exc}")
            log.debug(f"SQL query: {cursor.query}")
        finally:
            conn.close()
            self._put_conn(conn)

        if not result_tuple:
            return None
        user_entity = self.to_entity_model(result_tuple)
        return user_entity

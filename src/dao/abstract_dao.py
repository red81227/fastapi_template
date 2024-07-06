"""This file contains a abstract dao class."""
import abc
import traceback
from typing import Dict, List, Optional, Tuple
import pandas as pd

from config.logger_setting import log
from src.util.database.postgres.connection_pool import ContainerConnectionPool
from src.data_models.entities import EntityBaseModel


db_connection_pool = None


class AbstractDao(metaclass=abc.ABCMeta):
    """An abstract class for dao using psycopg2 connection pool.

    Attributes:
        table_name: str
            name of the binding table.
        conn_pool: ContainerConnectionPool
            a ContainerConnectionPool instance to get / put psycopg2 connection.

    Methods:
        save(data: EntityBaseModel) -> bool:
            Insert a row of data.
        delete_by_id(target_id: str) -> bool:
            Delete a row of data by id.
    """
    def __init__(self, table_name: str, entity_model: EntityBaseModel):
        """Setup connection pool, create related table if doesn't exist."""
        self.table_name = table_name
        self.Entity = entity_model
        self.col_names = list(entity_model.__fields__.keys())
        self._get_conn_pool()
        if not self._check_table_exist():
            self._create_table()
        log.info(f"Successfully initiated {table_name} dao.")

    def _get_conn_pool(self):
        """Get access to database connection pool."""
        global db_connection_pool
        if not db_connection_pool:
            db_connection_pool = ContainerConnectionPool()

        self.conn_pool = db_connection_pool

    def _get_conn(self):
        """Get connection from connection pool.

        Returns:
            a connection instance.
        """
        return self.conn_pool.get_conn()

    def _put_conn(self, conn):
        """Put connection back to connection pool.

        Parameters:
            conn: a connection instance
        """
        self.conn_pool.put_conn(conn)

    def _check_table_exist(self):
        """Check if the related table exist.

        Returns:
            Status of table existence.
        """
        status = False
        sql_text = f"SELECT to_regclass('{self.table_name}');"
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(sql_text)
            if cursor.fetchall()[0][0]:
                status = True
        except Exception as exc:
            log.error(traceback.format_exc())
        finally:
            conn.close()
            self._put_conn(conn)

        return status

    def _create_table(self):
        """Create related table in database.
        Return True if table is successfully created, otherwise False."""
        status = False
        conn = self._get_conn()
        try:
            log.info(f"Create table: {self.table_name} into database.")
            sql_text = ""
            with open(f"./data/sql/postgresql/ems_ai.sql") as sql_file:
                sql_text = sql_file.read()
            # get connection from pool
            cursor = conn.cursor()
            cursor.execute(sql_text)
            conn.commit()
            log.info(f"Successfully create table: {self.table_name} into database.")
            status = True
        except Exception:
            conn.rollback()
            log.error(f"Exception when creating table: {self.table_name} into database.")
            log.error(traceback.format_exc())
        finally:
            conn.close()
            self._put_conn(conn)

        return status

    def save(self, data: EntityBaseModel) -> bool:
        """Insert a row of data.

        Parameters:
            data: a row of data.

        Returns:
            status of database command execution.
        """
        status = False
        column_string, param_format, values = self._export_model(data)
        sql_text = f"INSERT INTO {self.table_name} ({column_string}) VALUES ({param_format})"
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(sql_text, values)
            conn.commit()
            status = True
        except Exception as exc:
            conn.rollback()
            log.error(f"Exception when INSERT data to table({self.table_name}): {exc}")
            log.debug(f"SQL query: {cursor.query}")
            log.error(f"{traceback.format_exc()}")
        finally:
            conn.close()
            self._put_conn(conn)

        return status

    def _save_all(self, data: List[EntityBaseModel]) -> bool:
        """Insert a row of data.

        Parameters:
            data: rows of data.

        Returns:
            status of database command execution.
        """
        # How to insert multiple rows:
        # https://stackoverflow.com/questions/8134602/psycopg2-insert-multiple-rows-with-one-query
        status = False
        exported_model_tuple = self._export_model_list(data, self.col_names)
        zipped_exported_model = zip(exported_model_tuple[0], exported_model_tuple[1])
        col_name_str = ",".join(self.col_names)

        sql_text = f"INSERT INTO {self.table_name} ({col_name_str}) VALUES "
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            args_text = ",".join(cursor.mogrify(
                param_format, row_value).decode("utf-8") for param_format, row_value in zipped_exported_model)
            cursor.execute(sql_text + args_text)
            conn.commit()
            status = True
        except Exception as exc:
            conn.rollback()
            log.error(f"Exception when INSERT data to table({self.table_name}): {exc}")
            log.debug(f"SQL query: {cursor.query}")
            log.error(f"{traceback.format_exc()}")
        finally:
            conn.close()
            self._put_conn(conn)

        return status

    def _save_all_and_update_if_conflict(self, data: List[EntityBaseModel], unique_cols: List[str]) -> bool:
        """Insert or update a row of data based on unique constraint violation.

        Parameters:
            data: rows of data.
            unique_cols: list of column names to be used for the unique constraint.

        Returns:
            status of database command execution.
        """
        status = False
        exported_model_tuple = self._export_model_list(data, self.col_names)
        zipped_exported_model = zip(exported_model_tuple[0], exported_model_tuple[1])
        col_name_str = ",".join(self.col_names)

        # Constructing the SQL command with ON CONFLICT clause to handle unique constraint
        sql_text = f"INSERT INTO {self.table_name} ({col_name_str}) VALUES "
        unique_cols_str = ", ".join(unique_cols)
        update_columns = ", ".join([f"{col}=EXCLUDED.{col}" for col in self.col_names if col not in unique_cols])

        # Appending the ON CONFLICT clause to handle duplicates
        update_sql_text = f" ON CONFLICT ({unique_cols_str}) DO UPDATE SET {update_columns}"

        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            args_text = ",".join(cursor.mogrify(param_format, row_value).decode("utf-8") for param_format, row_value in zipped_exported_model)
            cursor.execute(sql_text + args_text + update_sql_text)
            conn.commit()
            status = True
        except Exception as exc:
            conn.rollback()
            log.error(f"Exception when trying to INSERT/UPDATE data in table ({self.table_name}): {exc}")
            log.debug(f"SQL query: {cursor.query}")
            log.error(f"{traceback.format_exc()}")
        finally:
            conn.close()
            self._put_conn(conn)
        return status

    def _find(self, filter_data: Dict, target_columns: str = "*") -> Optional[List[Tuple]]:
        """Read a row of data filter by condition.

        Parameters:
            filter_data: condition of the query.
            target_columns: columns to find.

        Returns:
            result read from database.
        """
        result = None
        keys_string, values = self._dict_to_params(filter_data)
        sql_text = f"SELECT {target_columns} FROM {self.table_name} WHERE {keys_string} "
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(sql_text, values)
            result = cursor.fetchall()
        except Exception as exc:
            log.error(f"Exception when SELECT data in table({self.table_name}): {exc}")
            log.debug(f"SQL query: {cursor.query}")
            log.debug(f"{traceback.format_exc()}")
        finally:
            conn.close()
            self._put_conn(conn)

        return result

    def _find_all(self, target_columns: str = "*") -> Optional[List[Tuple]]:
        """Read all rows of data.

        Parameters:
            target_columns: columns to find.

        Returns:
            result read from database.
        """
        result = None
        sql_text = f"SELECT {target_columns} FROM {self.table_name} "
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(sql_text)
            result = cursor.fetchall()
        except Exception as exc:
            log.error(f"Exception when SELECT data in table({self.table_name}): {exc}")
            log.debug(f"{traceback.format_exc()}")
        finally:
            conn.close()
            self._put_conn(conn)

        return result

    def _find_by_id(self, target_id: str, target_columns: str = "*") -> Optional[Tuple]:
        """Read a row of data by id.

        Parameters:
            target_id: id of target data.

        Returns
            result read from database.
        """
        result = None
        sql_text = f"SELECT {target_columns} FROM {self.table_name} WHERE id = %s "
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(sql_text, (target_id, ))
            result = cursor.fetchone()
        except Exception as exc:
            log.error(f"Exception when SELECT data in table({self.table_name}): {exc}")
            log.debug(f"SQL query: {cursor.query}")
            log.debug(f"{traceback.format_exc()}")
        finally:
            conn.close()
            self._put_conn(conn)

        return result

    def _update(self, update_data: EntityBaseModel, filter_data: Dict) -> List[Tuple]:
        """Update a row of data by given condition.

        Parameters:
            update_data: data to update.
            filter_data: condition of the query.

        Returns
            status of database command execution.
        """
        result = []
        column_string, param_format, values = self._export_model(update_data)
        condition_keys, condition_values = self._dict_to_params(filter_data)
        sql_text = f"UPDATE {self.table_name} "\
                   f"SET ( {column_string} ) = ( {param_format} ) "\
                   f"WHERE {condition_keys} "\
                   f"RETURNING {', '.join(self.col_names)}"
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(sql_text, values + condition_values)
            # log.debug(f"update row count::: {cursor.rowcount}")
            result = cursor.fetchall()
            conn.commit()
        except Exception as exc:
            conn.rollback()
            log.error(f"Exception when UPDATE data from table({self.table_name}): {exc}")
            log.debug(f"SQL query: {cursor.query}")
            log.debug(f"{traceback.format_exc()}")
        finally:
            conn.close()
            self._put_conn(conn)

        return result

    def delete_by_id(self, target_id: str) -> bool:
        """Delete a row of data by id.

        Parameters:
            target_id: id of target data.

        Returns:
            status of database command execution.
        """
        status = False
        sql_text = f"DELETE FROM {self.table_name} WHERE id = %s "
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(sql_text, (target_id, ))
            conn.commit()
            status = True
        except Exception as exc:
            conn.rollback()
            log.error(f"Exception when DELETE data from table({self.table_name}): {exc}")
            log.debug(f"SQL query: {cursor.query}")
            log.debug(f"{traceback.format_exc()}")
        finally:
            conn.close()
            self._put_conn(conn)

        return status

    def _delete(self, filter_data: Dict) -> bool:
        status = False
        condition_keys, condition_values = self._dict_to_params(filter_data)
        sql_text = f"DELETE FROM {self.table_name} WHERE {condition_keys} "
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(sql_text, condition_values)
            conn.commit()
            status = True
        except Exception as exc:
            conn.rollback()
            log.error(f"Exception when DELETE data from table({self.table_name}): {exc}")
            log.debug(f"SQL query: {cursor.query}")
            log.debug(f"{traceback.format_exc()}")
        finally:
            conn.close()
            self._put_conn(conn)

        return status

    def _delete_small_than(self, filter_data: Dict) -> bool:
        status = False
        condition_keys, condition_values = self._dict_to_params_small_than(filter_data)
        sql_text = f"DELETE FROM {self.table_name} WHERE {condition_keys} "
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(sql_text, condition_values)
            conn.commit()
            status = True
        except Exception as exc:
            conn.rollback()
            log.error(f"Exception when DELETE data from table({self.table_name}): {exc}")
            log.debug(f"SQL query: {cursor.query}")
            log.debug(f"{traceback.format_exc()}")
        finally:
            conn.close()
            self._put_conn(conn)

        return status

    def to_entity_model(self, row_value: Tuple):
        """Transform a row in the type of tuple into an EntityModel object.

        Parameters:
            row_value: a row of value which matches the order of column in query string.

        Returns:
            an EntityModel object represents the row.
        """
        entity_dict = dict(zip(self.col_names, row_value))
        return self.Entity(**entity_dict)

    @staticmethod
    def _dict_to_params(data: Dict) -> Tuple[str, List]:
        """Transform key-value pairs of a database row into psycopg2 parameter strings.

        Parameters:
            data: key-value pairs of a database row in a form of dictionary

        Returns
            keys_string: string to put into psycopg2 query string.
            values: a list of cursor.execute() params.
        """
        keys, values = [], []
        for key, value in data.items():
            keys.append(f"{key} = %s")
            values.append(value)

        keys_string = " AND ".join(keys)
        return keys_string, values

    @staticmethod
    def _dict_to_params_small_than(data: Dict) -> Tuple[str, List]:
        """Transform key-value pairs of a database row into psycopg2 parameter strings.

        Parameters:
            data: key-value pairs of a database row in a form of dictionary

        Returns
            keys_string: string to put into psycopg2 query string.
            values: a list of cursor.execute() params.
        """
        keys, values = [], []
        for key, value in data.items():
            keys.append(f"{key} < %s")
            values.append(value)

        keys_string = " AND ".join(keys)
        return keys_string, values

    @staticmethod
    def _export_model(data: EntityBaseModel):
        """Parse data from pydantic model to params of sql.

        Parameters:
            data: a row of data in pydantic model type.

        Return:
            column_string(str): columns seperated by comma.
            param_format(str): '%s' seperated by comma.
            values(list): a list of value.
        """
        columns, format_list, values = [], [], []
        for column, value in data:
            if value is not None:
                columns.append(f"{column}")
                format_list.append("%s")
                values.append(value)

        column_string = ", ".join(columns)
        param_format = ", ".join(format_list)
        return column_string, param_format, values

    @staticmethod
    def _export_model_list(entity_model_list: List[EntityBaseModel], export_columns: List[str]):
        """Parse rows of data from pydantic model to params of sql.

        Parameters:
            data: rows of data in pydantic model type.

        Return:
            format_list(list): a list of string with '%s' seperated by comma.
            values(list): a list of tuple representing each row of data.
        """
        format_list, values = [], []
        for data in entity_model_list:
            row_format, row_value = [], []
            data_dict = data.dict()
            for col_name in export_columns:
                value = data_dict.get(col_name, None)
                row_format.append("%s")
                row_value.append(value)

            param_format = ", ".join(row_format)
            format_list.append(f"({param_format})")
            values.append(tuple(row_value))

        return format_list, values

    def get_dataframe_from_db(self, sql_text: str, params: Optional[List] = None):
        """Select dataframe from database.

        Arguments:
        - sql_text: str, select sql txt
          ex. select classroom_id, school_id, forecasting_result, predict_date from public.{table_name}
         where classroom_id = %s and predict_date between %s and %s order by predict_date desc

        - params: List, params for sql_text ex. ['classroom_id', 'school_id', 'forecasting_result', 'predict_date']

        Return a dataframe of data.
        """
        result = None

        conn = self._get_conn()
        try:
            result = pd.read_sql(sql_text, con=conn, params = params, dtype_backend = "pyarrow")
        except Exception as exc:
            conn.rollback()
            log.error(
                f"Exception when finding data in server table): {exc}")
            log.error(traceback.format_exc())
        finally:
            conn.close()
            self._put_conn(conn)

        return result
"""This file contains a class for psycopg2 connection pool."""
import traceback
from psycopg2.pool import ThreadedConnectionPool
import psycopg2
from config.logger_setting import log
from config.project_setting import database_config


class ConnectionPool:
    """A class for psycopg2 connection pool.

    - get_conn(): get a connection from the pool.
    - put_conn(): put a connection back to the pool.
    """
    connection_info: dict

    def __init__(self):
        """Setup connection pool to PostgreSQL with service configuration."""
        try:
            self.pool = ThreadedConnectionPool(
                minconn=database_config.minconn,
                maxconn=database_config.maxconn,
                **self.connection_info
            )
            log.info(
                f"successfully connected to db")
        except psycopg2.OperationalError as exc:
            log.error(f"Threaded Connection Pool error: {exc}")
            log.error(traceback.format_exc())

    def get_conn(self):
        """Get a connection from the pool."""
        return self.pool.getconn()

    def put_conn(self, conn):
        """Put a connection back to the pool.

        - conn: a connection instance.
        """
        self.pool.putconn(conn, close=False)


class ContainerConnectionPool(ConnectionPool):
    """This class is to setup container PostgreSQL connection pool"""

    def __init__(self):
        """Setup connection pool to PostgreSQL with container configuration."""
        self.connection_info = {
            "host": database_config.container_postgresql_host,
            "port": database_config.container_postgresql_port,
            "user": database_config.container_postgresql_user,
            "password": database_config.container_postgresql_password,
            "dbname": database_config.container_postgresql_database
        }
        super().__init__()


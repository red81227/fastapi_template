"""This file is for application config"""
from typing import List
from pydantic import BaseSettings, Field


class ServiceConfig(BaseSettings):
    """This file define the config that will be utilized to service"""
    log_file_path: str = 'data/logs/'
    log_file_name: str = 'ems-enterprise-ai.log'
    system_name: str = " ems-enterprise-ai"
    line_notify_token = ''
    default_hashed_password: str = ""

class SecurityConfigSettings(BaseSettings):
    access_token_expire_minutes: int = 30
    # The secret key should be properly generated and stored.
    secret_key: str = ""
    algorithm: str = "HS256"
    # https://stackoverflow.com/questions/19605150/regex-for-password-must-contain-at-least-eight-characters-at-least-one-number-a
    # User's password rule is to contain at least 1 upper case, 1 lower case alphabet, and in length between 8 to 12
    # 2022/03/11 新增@$!%*?&於\d之後，否則會無法輸入標點符號當密碼
    password_rule_regex: str = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,12}$'

class DatabaseConfigSettings(BaseSettings):
    """This class define the database baseconfig"""
    # container parameter
    container_postgresql_host: str = ""
    container_postgresql_user: str = ""
    container_postgresql_database: str = ""
    container_postgresql_password: str = ""
    container_postgresql_port: int = 5432

    minconn: int = 10
    maxconn: int = 20

    # pool parameter
    max_overflow: int = 10
    pool_size: int = 10


class RedisConfigSettings(BaseSettings):
    host: str = Field("redis", env="REDIS_HOST")
    port: int = Field(6379, env="REDIS_PORT")
    password: str = Field(None, env="REDIS_PASSWORD")
    db: int = Field(0, env="REDIS_DB")



database_config = DatabaseConfigSettings()

service_config = ServiceConfig()


redis_config = RedisConfigSettings()

security_config = SecurityConfigSettings()

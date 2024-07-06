import os

class BaseConfig(object):
    """This class define the celery baseconfig"""
    timezone = 'Asia/Taipei'
    include=[
        ''  # Import tasks from service_a/tasks.py or service_b/tasks.py
    ]
    worker_hijack_root_logger = False


class ProdConfig(BaseConfig):
    """This class define the celery ProdConfig"""
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = int(os.getenv("REDIS_PORT", 6379))

    broker_url = f'redis://{redis_host}:{redis_port}/0'
    result_backend = f'redis://{redis_host}:{redis_port}/1'

    result_expires = 3600  # 1小時，可以根據實際需求調整

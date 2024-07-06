"""This file is the celery application."""
from celery import Celery
from config.celery_config import ProdConfig

celery_app = Celery('celery_app')
celery_app.config_from_object(ProdConfig)

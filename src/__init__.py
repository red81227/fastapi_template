"""This file creates the fastapi service."""
# coding=utf-8
# pylint: disable=unused-variable,too-many-locals,too-many-statements,ungrouped-imports
# import relation package.
import os
from fastapi import FastAPI

from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from src.router.auth import create_auth_router
from src.router.login import create_login_router
from src.router.room import create_room_router
from src.router.task import create_task_router
from src.router.health_check import create_health_check_router
from src.router.bill_calculation import create_bill_contract_router
from src.router.demend_prediction import create_demend_prediction_router
from src.router.ac_control import create_ac_control_router
from src.router.anomaly_detection import create_anomaly_detection_router
from src.router.model import create_model_router
from src.router.user import create_user_router
from src.router.device import create_device_router
from src.router.data_receiver import create_data_receive_router


# import project package.
from config.logger_setting import log
from src.service.event.redis.lock_admin import LockAdmin
from src.operator.redis import RedisOperator
from src.service.schedule.apschedule import ScheduleWork
from src.util import function_utils

def create_app():
    """The function to creates the fastapi service."""

    version=function_utils.health_check_parsing()

    # Initial fastapi app
    app = FastAPI(title="Service AI Swagger API",
                description="This is swagger api spec document for the service-ems-enterprise_ai project.",
                version=version,
                root_path="/ems-enterprise-ai")

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        # pylint: disable=W0613,W0612
        return JSONResponse(status_code=400, content=jsonable_encoder({'errCode': '601', 'errMsg': 'Invalid Input', 'errDetail': exc.errors()}),)

    @app.on_event("startup")
    def startup_event():
        """startup events"""
        redis_operator = RedisOperator()

        apschedule_locker = LockAdmin(redis_operator)
        apschedule_lock = apschedule_locker.set_lock(value="apscheduler", ex=1, nx=True)
        if apschedule_lock:
            ScheduleWork().schedule_task_pipeline()

    # Health check router for this service
    health_check_router = create_health_check_router()
    user_router = create_user_router()
    login_router = create_login_router()
    auth_router = create_auth_router()


    api_version = f"/v1/"

    app.include_router(health_check_router, prefix=f"{api_version}service",
                       tags=["Health Check"])
    app.include_router(user_router, prefix=f"{api_version}user",
                          tags=["User"])
    app.include_router(login_router, prefix=f"{api_version}auth",
                            tags=["Login Endpoint"])
    app.include_router(auth_router, prefix=f"{api_version}auth",
                            tags=["Auth"])

    log.info("start fastapi service.")
    return app
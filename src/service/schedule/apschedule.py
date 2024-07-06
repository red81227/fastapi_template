"""This scrip is for define scheduler work"""
import pytz
from apscheduler.schedulers.background import BackgroundScheduler

from config.project_setting import auto_update_model_settings, auto_delete_data_settings
from config.logger_setting import log
from src.service.auto_update_model import AutoUpdateModelService
from src.util.data_management import DataManagement



class ScheduleWork:
    """This class is for the schedule task application."""
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.configure(
            timezone=pytz.timezone("Asia/Taipei"),
        )

    def schedule_task_pipeline(self):
        """schedule_task_pipeline: Use apscheduler to do the cronjob."""
        
        auto_update_model_service = AutoUpdateModelService()

        self.scheduler.add_job(
            auto_update_model_service.schedule_update_model,
            "cron",
            day=auto_update_model_settings.day,
            id=auto_update_model_settings.id
        )
        log.info("Successfully setting the APSchedule.")
        self.scheduler.start()
        log.info("Start the APSchedule.")

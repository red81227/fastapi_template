"""This file is for utility function"""
from io import StringIO
import os
from typing import List, Optional
import time
from functools import lru_cache
from datetime import datetime, timedelta, date
import uuid
import pandas as pd
from config.project_setting import demend_prediction_settings, temperature_predict_settings
import tzlocal


LOCAL_TIMEZONE = tzlocal.get_localzone()

@lru_cache(maxsize=128, typed=False)
def health_check_parsing() -> str:
    """This function is for parsing version information
    Return:
        version_str: str, return the project_version of the setup.py ex: 0.0.1
    """
    with open('setup.py', 'r') as f:
        setup_str = f.read()
    match_str = 'project_version='
    start_pos = setup_str.find(match_str) + len(match_str)
    end_pos = setup_str.find(',', start_pos)
    version_str = setup_str[start_pos:end_pos].replace("'", '')
    return version_str

def get_today_timestamp() -> int:
    """Get today UNIX timestamp in `int` type."""
    date_str = date.today().strftime('%Y-%m-%d')
    return time.mktime(datetime.strptime(date_str, "%Y-%m-%d").timetuple())

def get_current_timestamp() -> int:
    """Get current UNIX timestamp in `int` type."""
    return int(datetime.now().timestamp())

def get_yesterday_current_timestamp() -> int:
    """Get yesterday current UNIX timestamp in `int` type."""
    return int((datetime.now() - timedelta(days=1)).timestamp())

def get_month_first_timestamp() -> int:
    current_date = date.today()
    start_at  = date(current_date.year, current_date.month, 1)
    start_at_datetime = datetime(start_at.year, start_at.month, start_at.day)
    return int(start_at_datetime.timestamp())

def get_year_ago_timestamp() -> int:
    current_date = date.today()
    start_at  = date(current_date.year-1, current_date.month, 1)
    start_at_datetime = datetime(start_at.year, start_at.month, start_at.day)
    return int(start_at_datetime.timestamp())

def get_week_ago_timestamp() -> int:
    current_date = date.today()
    start_at  = current_date - timedelta(days=7)
    start_at_datetime = datetime(start_at.year, start_at.month, start_at.day)
    return int(start_at_datetime.timestamp())

def build_folder():
    """build folder for put data and model"""
    demend_forecasting_meta_data_path = temperature_predict_settings.meta_data_path
    demend_prediction_meta_data_path = demend_prediction_settings.meta_data_path

    demend_forecasting_model_path = temperature_predict_settings.model_path
    demend_prediction_model_path = demend_prediction_settings.model_path

    if not os.path.exists(demend_forecasting_meta_data_path):
        os.mkdir(demend_forecasting_meta_data_path)
    if not os.path.exists(demend_prediction_meta_data_path):
        os.mkdir(demend_prediction_meta_data_path)

    if not os.path.exists(demend_forecasting_model_path):
        os.mkdir(demend_forecasting_model_path)
    if not os.path.exists(demend_prediction_model_path):
        os.mkdir(demend_prediction_model_path)

def list_to_str(target_list: List[str])-> str:
    """List object to str without []
    Arguments:
    - target_list: target list object
    Return
    - str without []
    """
    return str(target_list).replace("[", "(").replace("]", ")")

def create_folder_if_not_exist(path: str)-> None:
    """create folder if not exist"""
    if not os.path.exists(path):
        os.makedirs(path)

def remove_old_meta_data(path: str)-> None:
    """remove old meta data"""

    filelist = [ f for f in os.listdir(path) if f.endswith(".npy") ]
    for f in filelist:
        os.remove(os.path.join(path , f))
    

def convert_timestamp_to_datetime(timestamp: int, time_format="%Y-%m-%d %H:%M:%S") -> str:
    """This function will convert timestamp to datetime with "%Y-%m-%d %H:%M:%S" format
    Example:
            convert_timestamp_to_datetime(1645895393) -> 2022-02-27 01:09:53
    """
    local_time = datetime.fromtimestamp(timestamp, LOCAL_TIMEZONE)
    return local_time.strftime(time_format)

def convert_datetime_to_timestamp(dt: datetime)-> int:
    """Convert a datetime object to a timestamp"""
    return int(dt.timestamp())

def get_predict_data_time(last_data_time: datetime, frequence: int, data_len: int = 4) -> int:
    """Get predict data time
    Arguments:
    - last_data_time: datetime, last date time
    - frequence: int, data time frequence
    """
    predict_data_time = []
    for i in range(data_len):
        next_time =  last_data_time + timedelta(minutes=frequence*(i+1))
        predict_data_time.append(convert_datetime_to_timestamp(next_time))
    return predict_data_time

def generate_id():
    """Generate and return an id."""
    return uuid.uuid1()

def json_to_dataframe(data: str = None)-> Optional[pd.DataFrame]:
    """Convert json to dataframe"""
    if not data:
        return None
    data = pd.read_json(StringIO(data), convert_dates=False)
    data["data_time"] = data["data_time"].astype("int64")
    return data

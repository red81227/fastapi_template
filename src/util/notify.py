
from typing import Dict
import requests


def notify_groups_by_notify_task(line_notify_task: Dict[str, str]) -> None:
    """Notify info to groups by and line notify tasks

    Parameters:
        line_notify_task: the information contains line notify info and tokens
    """
    notify_info = line_notify_task["notify_info"]
    notify_token = line_notify_task["line_notify_token"]
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Bearer {notify_token}"
    }
    data = f"message={notify_info}"
    requests.post(url, headers=headers, data=data)
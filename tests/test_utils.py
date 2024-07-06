"""This file is for testing util function"""

from src.util.function_utils import health_check_parsing
from config.logger_setting import log

def test_health_check_parsing_that_will_return_expected_number():
    """This function will test that health_check_parsing function"""

    RETURN_VERSION_NUMBER = 3
    RETURN_DOT_NUMBER = 2
    version_string = health_check_parsing()

    assert "." in version_string
    assert len(version_string.split('.')) == RETURN_VERSION_NUMBER

    dot_num = 0
    for string in version_string:
        if "." == string:
            dot_num += 1
    assert dot_num == RETURN_DOT_NUMBER

# def test_get_param_from_url(test_client):
#     """This function will test that get_param_from_url function"""
#     username="admin@group.com"
#     password="secret"
#     response = test_client.post(
#         f"craftsman/v1/auth/login?username={username}&password={password}"
#     )
#     log.error(response.json())

#     access_token = response.json()["access_token"]
#     assert access_token is not None




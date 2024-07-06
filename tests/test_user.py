"""This file is for testing user APIs."""
#pylint: disable=no-self-use, duplicate-code


from src.service.user import UserService


class TestUser:
    """Pytest class, test for user module."""
    @classmethod
    def setup_class(cls):
        """Setup for testing"""
        cls.api_version = f"/craftsman/v1"

    def test_create_user_ok(self, test_client, admin_auth_headers):
        """Test create user with correct input by ADMIN."""
        payload = {
            "account": "user_1",
            "email_address": "test@fareastone.com.tw",
            "additional_info": "str"
        }
        response = test_client.post(
            f"{self.api_version}/user",
            json=payload,
            headers=admin_auth_headers
        )
        response_json = response.json()
        assert response.status_code == 200
        assert response_json["account"] == "user_1"

    def test_get_users_and_update_ok(self, test_client, admin_auth_headers):
        """Test get user with correct input by MEMBER_USER i."""
        response = test_client.get(
            f"{self.api_version}/user/all",
            headers=admin_auth_headers
        )
        assert response.status_code == 200

        response_json = response.json()
        # find id which account is "user_1"
        user_id = None
        for user in response_json:
            if user["account"] == "user_1":
                user_id = user["id"]
                break

        payload = {
            "account": "user_1",
            "email_address": "test@fareastone.com.tw",
            "additional_info": "new_info"
        }
        response = test_client.put(
            f"{self.api_version}/user/{user_id}",
            json=payload,
            headers=admin_auth_headers
        )

        response_json = response.json()
        assert response.status_code == 200
        assert response_json["additional_info"] == "new_info"

    def test_get_user_with_existing_email_address(self):
        """Test get an existing user with email address successfully."""
        user_service = UserService()
        email_address = email_address="test@fareastone.com.tw"
        get_user_result = user_service.get_user_by_email_address(email_address)
        assert get_user_result.account == "user_1"

    def test_delete_user_ok(self, test_client, admin_auth_headers):
        """Test delete user with correct input by ADMIN."""
        response = test_client.get(
            f"{self.api_version}/user/all",
            headers=admin_auth_headers
        )
        response_json = response.json()
        # find id which account is "user_1"
        user_id = None
        for user in response_json:
            if user["account"] == "user_1":
                user_id = user["id"]
                break

        response = test_client.delete(
            f"{self.api_version}/user/{user_id}",
            headers=admin_auth_headers
        )
        assert response.status_code == 200






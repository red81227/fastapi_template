"""This file is for testing auth APIs."""
#pylint: disable=no-self-use, duplicate-code

class TestAuth:
    # pylint: disable=too-few-public-methods
    """Pytest class, test for auth module."""
    @classmethod
    def setup_class(cls):
        """Setup for testing"""
        cls.api_version = f"/craftsman/v1"
    
    def test_change_password_ok(self, test_client, admin_auth_headers):
        """Test change password with correct input by MEMBER_USER."""
        change_password_request = {
            "current_password": "secret",
            "new_password": "Newpassword1"
        }
        response = test_client.post(
            f"{self.api_version}/auth/change_password",
            json=change_password_request,
            headers=admin_auth_headers
        )
        assert response.status_code == 200

    def test_logout_ok(self, test_client, admin_auth_headers):
        """Test logout with correct authorization."""
        response = test_client.post(
            f"{self.api_version}/auth/logout",
            headers=admin_auth_headers
        )
        assert response.status_code == 200

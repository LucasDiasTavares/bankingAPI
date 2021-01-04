from .test_setup import TestSetUp
from ..models import User


class TestViews(TestSetUp):

    def test_user_cant_register_with_no_data(self):
        response = self.client.post(self.register_url)
        self.assertEqual(response.status_code, 400)

    def test_user_can_register(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.data['email'], self.user_data['email'])
        self.assertEqual(response.data['username'], self.user_data['username'])
        self.assertEqual(response.status_code, 201)

    def test_user_cant_login_with_unverified_email(self):
        self.client.post(self.register_url, self.user_data, format='json')
        response = self.client.post(self.login_url, self.user_data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_user_can_login_with_verified_email(self):
        res = self.client.post(self.register_url, self.user_data, format='json')
        email = res.data['email']
        user = User.objects.get(email=email)
        user.is_verified = True
        user.save()
        response = self.client.post(self.login_url, self.user_data, format='json')
        self.assertEqual(response.status_code, 200)

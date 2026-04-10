from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('register')

    def test_register_page_loads(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Create account')

    def test_register_success(self):
        r = self.client.post(self.url, {
            'username': 'testuser', 'email': 'test@example.com', 'password': 'pass1234'
        })
        self.assertEqual(r.status_code, 302)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_register_duplicate_username(self):
        User.objects.create_user('taken', 'a@a.com', 'pass')
        r = self.client.post(self.url, {
            'username': 'taken', 'email': 'b@b.com', 'password': 'pass1234'
        })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'already taken')

    def test_register_duplicate_email(self):
        User.objects.create_user('user1', 'same@mail.com', 'pass')
        r = self.client.post(self.url, {
            'username': 'user2', 'email': 'same@mail.com', 'password': 'pass1234'
        })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'already registered')

    def test_register_missing_fields(self):
        r = self.client.post(self.url, {'username': '', 'email': '', 'password': ''})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'required')

    def test_register_redirects_if_logged_in(self):
        User.objects.create_user('u', 'u@u.com', 'pass')
        self.client.login(username='u', password='pass')
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 302)


class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('login')
        self.user = User.objects.create_user('loginuser', 'l@l.com', 'securepass')

    def test_login_page_loads(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Sign in')

    def test_login_success(self):
        r = self.client.post(self.url, {'username': 'loginuser', 'password': 'securepass'})
        self.assertEqual(r.status_code, 302)
        self.assertRedirects(r, reverse('predict'))

    def test_login_wrong_password(self):
        r = self.client.post(self.url, {'username': 'loginuser', 'password': 'wrong'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Invalid')

    def test_login_nonexistent_user(self):
        r = self.client.post(self.url, {'username': 'ghost', 'password': 'pass'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Invalid')

    def test_login_redirects_if_logged_in(self):
        self.client.login(username='loginuser', password='securepass')
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 302)


class LogoutViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('logoutuser', 'lo@lo.com', 'pass')
        self.client.login(username='logoutuser', password='pass')

    def test_logout_redirects_home(self):
        r = self.client.get(reverse('logout'))
        self.assertRedirects(r, reverse('home'))

    def test_logout_clears_session(self):
        self.client.get(reverse('logout'))
        r = self.client.get(reverse('predict'))
        self.assertEqual(r.status_code, 302)
        self.assertIn('/accounts/login/', r['Location'])

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Profile
import json
import re


def make_user(username='tester', password='pass123'):
    u = User.objects.create_user(username, f'{username}@t.com', password)
    Profile.objects.get_or_create(user=u)
    return u


VALID_PAYLOAD = {
    'brand': 'Honda',
    'model': 'City',
    'year': '2015',
    'location': 'Mumbai',
    'kilometers_driven': '45000',
    'fuel_type': 'Petrol',
    'transmission': 'Manual',
    'owner_type': 'First',
    'mileage': '18.4',
    'engine': '1494.0',
    'power': '110.6',
    'seats': '5',
}


class HomeTests(TestCase):
    def test_home_loads(self):
        r = self.client.get(reverse('home'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Car Value Predictor')

    def test_home_arrow_points_to_login_when_anonymous(self):
        r = self.client.get(reverse('home'))
        self.assertContains(r, '/accounts/login/')

    def test_home_arrow_points_to_predict_when_logged_in(self):
        make_user('homeuser')
        self.client.login(username='homeuser', password='pass123')
        r = self.client.get(reverse('home'))
        self.assertContains(r, '/predict/')


class PredictPageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user()

    def test_predict_page_requires_login(self):
        r = self.client.get(reverse('predict'))
        self.assertEqual(r.status_code, 302)

    def test_predict_page_loads_when_logged_in(self):
        self.client.login(username='tester', password='pass123')
        r = self.client.get(reverse('predict'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Car Value Predictor')

    def test_predict_shows_username(self):
        self.client.login(username='tester', password='pass123')
        r = self.client.get(reverse('predict'))
        self.assertContains(r, 'tester')

    def test_predict_page_has_brands(self):
        self.client.login(username='tester', password='pass123')
        r = self.client.get(reverse('predict'))
        for brand in ['Honda', 'Toyota', 'BMW', 'Maruti']:
            self.assertContains(r, brand)

    def test_models_api_returns_json(self):
        r = self.client.get(reverse('get_models'), {'brand': 'Honda'})
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.content)
        self.assertIn('models', data)
        self.assertIn('City', data['models'])

    def test_models_api_unknown_brand(self):
        r = self.client.get(reverse('get_models'), {'brand': 'UnknownBrand'})
        data = json.loads(r.content)
        self.assertEqual(data['models'], [])

    def test_models_api_no_brand(self):
        r = self.client.get(reverse('get_models'))
        data = json.loads(r.content)
        self.assertEqual(data['models'], [])


class PredictResultTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user('predictor')
        self.client.login(username='predictor', password='pass123')

    def test_result_valid_prediction(self):
        r = self.client.post(reverse('predict_result'), VALID_PAYLOAD)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Honda')
        self.assertContains(r, 'City')

    def test_result_has_price_elements(self):
        r = self.client.post(reverse('predict_result'), VALID_PAYLOAD)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'price-value')
        self.assertContains(r, 'price-rupee')
        self.assertContains(r, 'Lakh')

    def test_result_requires_login(self):
        self.client.logout()
        r = self.client.post(reverse('predict_result'), VALID_PAYLOAD)
        self.assertEqual(r.status_code, 302)

    def test_result_get_redirects(self):
        r = self.client.get(reverse('predict_result'))
        self.assertRedirects(r, reverse('predict'))

    def test_result_different_brands(self):
        for brand, model in [('Maruti', 'Swift'), ('BMW', 'X5'), ('Tata', 'Nano')]:
            payload = {**VALID_PAYLOAD, 'brand': brand, 'model': model}
            r = self.client.post(reverse('predict_result'), payload)
            self.assertEqual(r.status_code, 200)
            self.assertContains(r, brand)

    def test_result_shows_input_details(self):
        r = self.client.post(reverse('predict_result'), VALID_PAYLOAD)
        self.assertContains(r, 'Mumbai')
        self.assertContains(r, 'Petrol')
        self.assertContains(r, 'Manual')
        self.assertContains(r, 'First')

    def test_result_all_years(self):
        for year in ['1998', '2005', '2015', '2019']:
            payload = {**VALID_PAYLOAD, 'year': year}
            r = self.client.post(reverse('predict_result'), payload)
            self.assertEqual(r.status_code, 200)

    def test_result_all_fuel_types(self):
        for fuel in ['Petrol', 'Diesel', 'CNG', 'LPG', 'Electric']:
            payload = {**VALID_PAYLOAD, 'fuel_type': fuel}
            r = self.client.post(reverse('predict_result'), payload)
            self.assertEqual(r.status_code, 200)

    def test_result_all_transmissions(self):
        for t in ['Manual', 'Automatic']:
            payload = {**VALID_PAYLOAD, 'transmission': t}
            r = self.client.post(reverse('predict_result'), payload)
            self.assertEqual(r.status_code, 200)

    def test_result_all_owner_types(self):
        for o in ['First', 'Second', 'Third', 'Fourth & Above']:
            payload = {**VALID_PAYLOAD, 'owner_type': o}
            r = self.client.post(reverse('predict_result'), payload)
            self.assertEqual(r.status_code, 200)

    def test_result_km_formatting(self):
        payload = {**VALID_PAYLOAD, 'kilometers_driven': '100000'}
        r = self.client.post(reverse('predict_result'), payload)
        self.assertContains(r, '100,000')


class NavbarTests(TestCase):
    def setUp(self):
        self.user = make_user('navuser', 'pass1234')

    def test_navbar_shows_login_when_anonymous(self):
        r = self.client.get(reverse('home'))
        self.assertContains(r, 'Login')

    def test_navbar_shows_username_when_authenticated(self):
        self.client.login(username='navuser', password='pass1234')
        r = self.client.get(reverse('predict'))
        self.assertContains(r, 'navuser')

    def test_navbar_shows_logout_when_authenticated(self):
        self.client.login(username='navuser', password='pass1234')
        r = self.client.get(reverse('predict'))
        self.assertContains(r, 'Logout')

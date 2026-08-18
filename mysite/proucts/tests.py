from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import resolve
from .models import Phone,Category
# Create your tests here.


class CartTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="testuser",
            password="12345"
        )

        self.category = Category.objects.create(
            name="Smartphones"
        )

        self.phone = Phone.objects.create(
            brand='Apple',
            model="iphone",
            category=self.category,
            price=5000,
            stock=2,
            author=self.user
        )

    def test_cannot_add_more_than_stock(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            "/api/cart-items/",
            {
                "phone":self.phone.id,
                "quantity": 3
            },
            format="json"
        )

        print(response.status_code)
        print(response.data)

       
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
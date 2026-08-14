from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Phone,Category
# Create your tests here.


class CartTest(APITestCase):
    def setUp(self):
        pass
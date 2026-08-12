from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import *


router = DefaultRouter()
router.register("phones",PhoneViewSet)
router.register("category",CategoryViewSet)
router.register("favorite",FavoriteViewSet,basename="favorite"),
router.register("reviews",ReviewViewSet,basename="review"),
router.register("cart",CartvViewSet,basename="cart")
router.register("cart-items",CartItemViewSet,basename="cart-item")
router.register("orders",OrderViewSet,basename="orders")

urlpatterns =  [
    path("",include(router.urls)),
]
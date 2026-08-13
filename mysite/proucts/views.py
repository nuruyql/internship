
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly,IsReviewOwnerOrReadOnly
from .serializers import *
from .models import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.db.models import  Avg
from django.db import transaction
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
# Create your views here.

class PhoneViewSet(ModelViewSet):
    queryset = Phone.objects.select_related("category","author").annotate(average_rating_value=Avg("reviews__rating")).order_by("id")
    serializer_class = PhoneSerializers
    filter_backends = [
                       SearchFilter,
                       DjangoFilterBackend,
                       OrderingFilter
                       ]
    permission_classes = [IsOwnerOrReadOnly]
    search_fields = ["brand","model","description"]
    ordering_fields = ["price","created_at"]
    filterset_fields = ['category','stock']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializers
    permission_classes = [IsAdminOrReadOnly]


class FavoriteViewSet(ModelViewSet):
    serializer_class = FavoriteSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.select_related("phone").filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.select_related("user","phone")
    serializer_class=ReviewSerializers
    permission_classes = [IsReviewOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["phone","rating"]

    def perform_create(self,serializer):
        serializer.save(user=self.request.user)


class CartvViewSet(ModelViewSet):
    serializer_class=CartSerializers
    permission_classes=[IsAdminOrReadOnly]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self,serializer):
        serializer.save(user=self.request.user)


class CartItemViewSet(ModelViewSet):
    serializer_class=CartItemSerializers
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(
            cart__user=self.request.user
        )

    def perform_create(self, serializer):
        cart,created = Cart.objects.get_or_create(
            user=self.request.user
        )
        serializer.save(cart=cart)


class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializers
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related("items")

    @transaction.atomic
    def perform_create(self,serializer):
        try:
            cart = Cart.objects.get(
                user=self.request.user
            )

        except Cart.DoesNotExist:
            raise ValidationError(
                "there is no cart"
            )
        cart_items = cart.items.select_related("phone")


        if not cart_items.exists():
            raise ValidationError(
                "empty cart"
            )
        for item in cart_items:
            if item.quantity > item.phone.stock:
                raise ValidationError({
                    "stock": (
                        f"{item.phone}: in a garage",
                        f"{item.phone.stock} stock"
                    )
                })

        order = serializer.save(
                user=self.request.user
            )


        for item in cart_items:
                phone  = item.phone


                OrderItem.objects.create(
                    order=order,
                    phone=phone,
                    quantity=item.quantity,
                    price=phone.price
                )

                phone.stock -= item.quantity
                phone.save()



        cart_items.delete()



class PaymentViewSet(ModelViewSet):
    serializer_class= PaymentSerializers
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(
            order__user=self.request.user
        ).select_related("order")

    def perform_create(self, serializer):
        order = serializer.validated_data["order"]

        if order.user != self.request.user:
            raise ValidationError(
                "It is not your order"
            )

        serializer.save()


    @action(
            detail=True,
            methods=["post"]
        )
    def pay(self,request,pk=None):
            payment = self.get_object()

            if payment.status == "paid":
                raise ValidationError(
                "Payment is alread paid"
                )
            payment.status = "paid"
            payment.paid_at = timezone.now()

            payment.save(
                update_fields=["status","paid_at"]
            )

            return Response(
                self.get_serializer(payment).data,
                status=status.HTTP_200_OK
            )
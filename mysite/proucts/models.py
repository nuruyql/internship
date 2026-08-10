from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.validators import MinValueValidator,MaxValueValidator
# Create your models here.

User = get_user_model()

class  Category(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

class Phone(models.Model):
    brand = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.PositiveBigIntegerField()
    img = models.ImageField(upload_to="phones/",null=True,blank=True)
    description = models.CharField(max_length=255,blank=True,null=True)
    stock = models.PositiveBigIntegerField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    author = models.ForeignKey(User,on_delete=models.CASCADE,related_name="phones",blank=True,null=True)

    def __str__(self):
        return  f"{self.brand} {self.model}"


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="favorites")
    phone = models.ForeignKey(Phone,on_delete=models.CASCADE,related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints  = [
            models.UniqueConstraint(
                fields=["user","phone"],
                name="unique_user_phone_favorite"
            )
        ]

        def __str__(self):
            return f"{self.user}-{self.phone}"
        
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="reviews")
    phone = models.ForeignKey(Phone,on_delete=models.CASCADE,related_name="reviews")
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )
    comments = models.TextField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user","phone"],
                name="unique_user_phone_review"
            )
        ]

class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="cart"
    )
    def __str__(self):
        return f"Cart of {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="items")
    phone = models.ForeignKey(Phone,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


    def __str__(self):
        return f"{self.phone.brand} x {self.quantity}"
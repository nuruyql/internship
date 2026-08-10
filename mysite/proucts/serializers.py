from rest_framework import serializers
from .models import *

class PhoneSerializers(serializers.ModelSerializer):

    average_rating = serializers.SerializerMethodField()

    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )
    class Meta:
        model = Phone
        fields = "__all__"
        read_only_fields = ["author"]

    def get_average_rating(self,obj):
            average = getattr(obj,"average_rating_value",None)
            if average is None:
                return 0
            return round(average , 1)
    
    def validate_price(self,value):
        if value < 0:
            raise serializers.ValidationError("Cannot be lower that 0")
        
        return value
        

class CategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class FavoriteSerializers(serializers.ModelSerializer):
    user  = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Favorite
        fields = "__all__"
        read_only_fields = ["user","created_at"]


    def validate(self,attrs):
        user = self.context["request"].user
        phone = attrs.get("phone")

        if Favorite.objects.filter(
            user=user,
            phone=phone
        ).exists():
            raise serializers.ValidationError("Already in your favorites")


class ReviewSerializers(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ["user","created_at"]

class CartItemSerializers(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()



    class Meta:
        model = CartItem
        fields="__all__"
        read_only_fields = ["cart"]



    def get_total_price(self,obj):
        return obj.phone.price * obj.quantity
    
class CartSerializers(serializers.ModelSerializer):


    items = CartItemSerializers(
        many=True,
        read_only=True
    )



    total_price = serializers.SerializerMethodField()


    class Meta:
        model = CartItem
        fields = "__all__"

        read_only_fields = ["user"]



    def get_total_price(self,obj):
        return  sum(
            item.phone.price * item.quantity
            for item in obj.items.all( )
        )
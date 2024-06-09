from rest_framework import serializers
from decimal import Decimal
from store.models import Product,Collection, Review


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields =['id','title','products_count']
    
    products_count = serializers.IntegerField(read_only = True)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','title','slug','descriptiom','inventory','price','price_with_tax','collection']
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
   

    def calculate_tax (self, product):
        return product.price * Decimal(1.1)
    
    # def validate(self, data):
    #     if data['password'] != data['confirm_password']:
    #         return serializers.ValidationError('Passwords do not match')
    #     return data

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id','date','name','description']

    def create(self, validated_data):
       product_id = self.context['product_id']
       return Review.objects.create(product_id=product_id, **validated_data) 


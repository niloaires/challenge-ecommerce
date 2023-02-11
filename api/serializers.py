from shop.models import *
from rest_framework import serializers
from decimal import Decimal


class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductsModel
        fields = ['name', 'price', 'score']


class ItensCartSerializer(serializers.ModelSerializer):
    products = ProductsSerializer(read_only=True)

    class Meta:
        model = ItensCart
        fields = ['id', 'products', 'qtd']


class CartSerializer(serializers.ModelSerializer):
    itens_cart = ItensCartSerializer(many=True, read_only=True)
    count_itens = serializers.SerializerMethodField()
    amount_value = serializers.SerializerMethodField()
    ship_value = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()

    class Meta:
        model = CartsModel
        fields = ['code', 'ativo',  'itens_cart', 'count_itens', 'amount_value', 'ship_value', 'amount']

    def get_count_itens(self, obj):
        return obj.count_itens()

    def get_amount_value(self, obj):
        return "$ {}".format(obj.accumulated_value_products())

    def get_ship_value(self, obj):
        return "$ {}".format(obj.ship_value())

    def get_amount(self, obj):
        return "$ {}".format(obj.amount())


class OrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderClients
        fields = '__all__'

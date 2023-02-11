from django.contrib import admin
from shop.models import *
# Register your models here.

admin.site.register(ProductsModel)
admin.site.register(CartsModel)
admin.site.register(ItensCart)
admin.site.register(OrderClients)
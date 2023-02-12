from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from api.views import *

urlpatterns = [
    path('login/', login_api_view),
    path('products/', ProdutosView.as_view({'get': 'list'})),
    path('products/<int:pk>', ProdutosView.as_view({'get': 'retrieve'})),
    path('cart/', CarrinhoView.as_view({'get': 'list', 'post': 'create'})),
    path('add-product-cart/<int:pk>', add_item_to_cart),
    path('remove-product-cart/<int:pk>', remove_item_cart),
    path('checkout/', checkout),
    path('orders/', OrdersViews.as_view({'get': 'list'}))
]

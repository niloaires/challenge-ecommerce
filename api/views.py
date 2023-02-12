from datetime import datetime
from django.contrib.auth import authenticate, login
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from api.serializers import *
from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status


# Create your views here.


@api_view(['POST'])
def login_api_view(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        response = {
            'message': "O usuário {} está logado!".format(user)
        }
        return Response(response, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


class ProdutosView(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProductsSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['name', 'price', 'score']

    def get_queryset(self):
        return ProductsModel.objects.all().order_by('name')

    def get_object(self, *args, **kwargs):
        return get_object_or_404(ProductsModel, pk=self.kwargs.get("pk"))


class CarrinhoView(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_object(self, *args, **kwargs):
        qs = CartsModel.objects.filter(pk=self.kwargs.get("pk")).latest('pk')
        if not qs:
            response = {
                'message': 'Você não possui carrinho'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            response = {
                'object': CartSerializer(qs, many=True)
            }
            return Response(response, status=status.HTTP_200_OK)

    def get_queryset(self, *args, **kwargs):
        return CartsModel.objects.filter(user=self.request.user).order_by('created_date')

    def create(self, request, *args, **kwargs):
        serializer = CartSerializer(request.data)
        if serializer.is_valid():
            serializer.save()
        else:
            response = {
                'message': serializer.error_messages
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


"""
A função a seguir, deverá verificar inicialmente se o usuário já possui um carro de compras ativo, 
caso contrário criará um novo carro de compras; em seguida verificará se o produto já existe no carro, caso existe, irá
incrementar mais um no atributo 'qtd'.
"""


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def add_item_to_cart(request, pk):
    user = request.user
    item = get_object_or_404(ProductsModel, pk=pk)
    # cart = CartsModel.objects.get_or_create(user=user, ativo=True)
    cart = CartsModel.objects.filter(user=user, ativo=True)
    if not cart:
        CartsModel.objects.create(user=user)
        cart = CartsModel.objects.filter(user=user, ativo=True).latest('pk')
        OrderClients.objects.create(
            client=user,
            cart=cart
        )
    cart = CartsModel.objects.filter(user=user, ativo=True).latest('pk')
    item_cart = ItensCart.objects.filter(cart=cart, products=item)
    if item_cart.exists():
        instancia = item_cart.latest('pk')
        instancia.qtd += 1
        instancia.save()
        response = {
            'message': "O produto {} teve sua quantidade alterada".format(instancia.products.name)
        }
        return Response(response, status=status.HTTP_200_OK)
    else:
        ItensCart.objects.create(cart=cart, products=item, qtd=1)
        item_cart = ItensCart.objects.filter(cart=cart, products=item).latest('pk')
        response = {
            'message': "O produto {} foi adicionado ao carrinho".format(item_cart.products.name)
        }
        return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def remove_item_cart(request, pk):
    user = request.user
    item = get_object_or_404(ItensCart, pk=pk)
    proprietario = item.carrinho.user
    if proprietario != user:
        content = {
            'message': "Você não pode exluir um item que não pertece ao seu carrinho"
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    item.delete()
    content = {
        'message': "O item removido do Carrinnho"
    }

    return Response(content, status=status.HTTP_200_OK)


class ItensCartsView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ItensCartSerializer

    def get_queryset(self):
        return ItensCart.objects.all()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def checkout(request):
    user = request.user
    cart = CartsModel.objects.filter(ativo=True, user=user)
    if cart.exists():
        last_cart = cart.latest('pk')
        order = last_cart.orders_cart
        order.value_itens = last_cart.accumulated_value_products()
        order.value_addition = last_cart.ship_value()
        order.amount = last_cart.amount()
        order.status_order = 'finalizado'
        order.checkout_date = datetime.datetime.now()
        order.save()
        last_cart.ativo = False
        last_cart.save()
        content = {
            'message': "Checkout realizado com sucesso"
        }

        return Response(content, status=status.HTTP_200_OK)
    else:
        content = {
            'message': "Não existe um carro de compras válido"
        }

        return Response(content, status=status.HTTP_400_BAD_REQUEST)


class OrdersViews(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrdersSerializer

    def get_queryset(self):
        return OrderClients.objects.filter(client=self.request.user)


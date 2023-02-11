import decimal

from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
import datetime
from django.dispatch import receiver
from django.db.models.signals import post_save

"""
CONSIDERAÇÕES AO AVALIADOR

Este código foi produzido inicialmente em Português, no entanto, visto que o modelo de Produtos está em inglês, decici
por padronizar em um único idiona, dessa forma, somente as constantes e títulos de campos no model continuam
em português.

Nilo Aires Jr.
"""

# Constantes
STATUS_PEDIDOS = (
    ('pendente', 'Pendente'),
    ('finalizado', 'Finalizado'),
    ('outros', 'Outros')
)
VALOR_FRETE_UNITARIO = 10.0


class ProductsModel(models.Model):
    name = models.CharField(max_length=200, verbose_name='Product Name', blank=False, null=False)
    price = models.DecimalField(max_digits=13, decimal_places=2, default=Decimal('0.00'), verbose_name='Preço')
    score = models.PositiveSmallIntegerField(blank=False, null=False, verbose_name='Score')
    image = models.ImageField(upload_to='imagens_products', blank=True, null=True, verbose_name='Imagem')

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

    def __str__(self):
        return self.name


class CartsModel(models.Model):
    code = models.CharField(max_length=50, unique=True, blank=True, null=False,
                            default=datetime.datetime.now().strftime("%d%m%Y/%H%M%S"),
                            verbose_name='Código do carrinho')
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='carrinhos_compra')
    ativo = models.BooleanField(default=True, verbose_name='Carrinho ativo')
    created_date = models.DateTimeField(auto_now=True, verbose_name='Data de criação')

    def count_itens(self):
        total = 0
        for item in self.itens_cart.all():
            total += item.qtd
        return total

    def accumulated_value_products(self):
        total = 0
        for i in self.itens_cart.all():
            qtd = i.qtd
            valor_unit = i.products.price
            total = total + (valor_unit * qtd)
        return Decimal(total)

    def ship_value(self):
        total = 0
        count_products = self.itens_cart.all().count()
        ship_products = (VALOR_FRETE_UNITARIO * count_products)
        if self.accumulated_value_products() > Decimal(250.00):
            return 0
        else:
            total = total + ship_products
            return Decimal(total)

    def amount(self):
        return Decimal(self.accumulated_value_products() + self.ship_value())

    class Meta:
        verbose_name = 'Carrinho de compra'
        verbose_name_plural = 'Carrinhos de compra'

    def __str__(self):
        return "{user} - {code}".format(user=self.user.username, code=self.code)

    def itens(self):
        return self.itens_cart.all()


class ItensCart(models.Model):
    cart = models.ForeignKey(CartsModel, on_delete=models.PROTECT, related_name='itens_cart')
    products = models.ForeignKey(ProductsModel, on_delete=models.PROTECT, related_name='itens_cart_p')
    qtd = models.PositiveSmallIntegerField(default=1)


class OrderClients(models.Model):
    client = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders_client')
    cart = models.OneToOneField(CartsModel, on_delete=models.PROTECT, related_name='orders_cart')
    status_order = models.CharField(max_length=10, choices=STATUS_PEDIDOS, blank=True, null=False,
                                    verbose_name='Status do Pedido', default='pendente')
    value_itens = models.DecimalField(max_digits=13, decimal_places=2, default=Decimal('0.00'),
                                      verbose_name='Valor dos Itens')
    value_addition = models.DecimalField(max_digits=13, decimal_places=2, default=Decimal('0.00'),
                                         verbose_name='Valor de acrescimo')
    amount = models.DecimalField(max_digits=13, decimal_places=2, default=Decimal('0.00'),
                                 verbose_name='Valor total')
    register_date = models.DateTimeField(auto_now=True)
    checkout_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return "{cliente} - {status} - {register_date} R$ {valor}".format(cliente=self.client.username,
                                                                          status=self.get_status_order_display,
                                                                          register_date=self.register_date,
                                                                          valor=self.amount)

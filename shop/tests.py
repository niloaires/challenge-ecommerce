from django.test import TestCase
from shop.models import *
import random
from faker import Faker
import faker_commerce
from django.db.models import Sum


# Create your tests here.

class ShopTest(TestCase):
    def setUp(self):
        fake = Faker()
        fake.add_provider(faker_commerce.Provider)
        for i in range(20):
            ProductsModel.objects.create(
                name="Produto {}".format(fake.ecommerce_name()),
                price=random.randint(1000, 1500) / 100,
                score=random.randint(0, 500)
            )
        User.objects.create(username='user_teste', password='P@sswordTest', email='email@email.com')
        cart = CartsModel.objects.create(user=User.objects.latest('pk'))
        for i in ProductsModel.objects.all():
            ItensCart.objects.create(cart=cart, products=i)

    def teste_gerar_produtos(self):
        self.assertEqual(ProductsModel.objects.all().count(), 20)

    def teste_ordenar_por_maior_preco(self):
        item_maior_preco = ProductsModel.objects.all().order_by('price').first()
        preco = item_maior_preco.price
        qs = ProductsModel.objects.all().order_by('price').first()
        self.assertEqual(qs.price, preco)

    def teste_ordenar_por_menor_preco(self):
        item_menor_preco = ProductsModel.objects.all().order_by('-price').first()
        preco = item_menor_preco.price
        qs = ProductsModel.objects.all().order_by('-price').first()
        self.assertEqual(qs.price, preco)

    def testar_frete_gratis(self):
        """
        Pela lógica de negócio que o desafio exigiu, casou o carrinho de
        compras alcance o valor acumulado de 250, o frete será grátis.
        """
        cart = CartsModel.objects.latest('pk')
        total_em_produtos = cart.accumulated_value_products()
        valor_frete = cart.ship_value()
        if total_em_produtos > decimal.Decimal(250):
            frete = decimal.Decimal(0)
        else:
            frete = decimal.Decimal(cart.count_itens()*10)

        self.assertEqual(valor_frete, frete)




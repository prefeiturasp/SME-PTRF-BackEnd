from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.users.models import AcessoConcedidoSme

fake = Faker("pt_BR")


class AcessoConcedidoSmeFactory(DjangoModelFactory):
    class Meta:
        model = AcessoConcedidoSme

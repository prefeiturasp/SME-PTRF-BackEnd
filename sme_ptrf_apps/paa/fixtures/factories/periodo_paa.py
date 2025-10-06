
from factory.django import DjangoModelFactory
from factory import LazyFunction, LazyAttribute
from faker import Faker
from sme_ptrf_apps.paa.models import PeriodoPaa
from datetime import timedelta

fake = Faker("pt_BR")


class PeriodoPaaFactory(DjangoModelFactory):
    class Meta:
        model = PeriodoPaa

    referencia = fake.unique.name()
    # gera uma data inicial aleatória dentro de um intervalo
    data_inicial = LazyFunction(lambda: fake.date_between(start_date="-2y", end_date="today"))

    # data final sempre após a inicial
    data_final = LazyAttribute(
        lambda obj: obj.data_inicial + timedelta(days=fake.random_int(min=30, max=365))
    )

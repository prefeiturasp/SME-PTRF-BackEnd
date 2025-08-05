from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.paa.models import PeriodoPaa

fake = Faker("pt_BR")


class PeriodoPaaFactory(DjangoModelFactory):
    class Meta:
        model = PeriodoPaa

    referencia = fake.unique.name()

from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.paa.models import ModeloCargaPaa
from sme_ptrf_apps.paa.enums import TipoCargaPaaEnum

fake = Faker("pt_BR")


class ModeloCargaPaaFactory(DjangoModelFactory):
    class Meta:
        model = ModeloCargaPaa

    tipo_carga = TipoCargaPaaEnum.MODELO_PLANO_ANUAL.name
    arquivo = None

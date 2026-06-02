from factory import SubFactory
from factory.django import DjangoModelFactory
from faker import Faker

from sme_ptrf_apps.receitas.models import DetalheTipoReceita

from .tipo_receita_factory import TipoReceitaFactory

fake = Faker("pt_BR")


class DetalheTipoReceitaFactory(DjangoModelFactory):
    class Meta:
        model = DetalheTipoReceita

    nome = fake.unique.word()
    tipo_receita = SubFactory(TipoReceitaFactory)

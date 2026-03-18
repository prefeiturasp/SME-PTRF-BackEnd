from factory.django import DjangoModelFactory
from sme_ptrf_apps.receitas.models import Receita


class ReceitaFactory(DjangoModelFactory):
    class Meta:
        model = Receita

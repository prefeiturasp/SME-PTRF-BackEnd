from factory import SubFactory, Sequence
from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.paa.models import ReceitaPrevistaPaa
from sme_ptrf_apps.core.fixtures.factories.acao_associacao_factory import AcaoAssociacaoFactory
from sme_ptrf_apps.paa.fixtures.factories.paa import (
    PaaFactory)
fake = Faker("pt_BR")


class ReceitaPrevistaPaaFactory(DjangoModelFactory):
    class Meta:
        model = ReceitaPrevistaPaa

    paa = SubFactory(PaaFactory)
    acao_associacao = SubFactory(AcaoAssociacaoFactory)
    previsao_valor_custeio = Sequence(lambda n: fake.random_number(digits=3))
    previsao_valor_capital = Sequence(lambda n: fake.random_number(digits=3))
    previsao_valor_livre = Sequence(lambda n: fake.random_number(digits=3))

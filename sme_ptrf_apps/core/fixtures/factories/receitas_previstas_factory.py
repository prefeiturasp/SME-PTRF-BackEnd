from factory import DjangoModelFactory, SubFactory, Sequence
from faker import Faker
from sme_ptrf_apps.core.models import ReceitaPrevistaPaa
from .acao_associacao_factory import AcaoAssociacaoFactory

fake = Faker("pt_BR")


class ReceitaPrevistaPaaFactory(DjangoModelFactory):
    class Meta:
        model = ReceitaPrevistaPaa

    acao_associacao = SubFactory(AcaoAssociacaoFactory)
    previsao_valor_custeio = Sequence(lambda n: fake.random_number(digits=3))
    previsao_valor_capital = Sequence(lambda n: fake.random_number(digits=3))
    previsao_valor_livre = Sequence(lambda n: fake.random_number(digits=3))

from factory import DjangoModelFactory, SubFactory, Sequence
from faker import Faker
from sme_ptrf_apps.paa.models import ReceitaPrevistaPdde
from sme_ptrf_apps.paa.fixtures.factories.acao_pdde_factory import (
    AcaoPddeFactory)
from sme_ptrf_apps.paa.fixtures.factories.paa import (
    PaaFactory)

fake = Faker("pt_BR")


class ReceitaPrevistaPddeFactory(DjangoModelFactory):
    class Meta:
        model = ReceitaPrevistaPdde

    paa = SubFactory(PaaFactory)
    acao_pdde = SubFactory(AcaoPddeFactory)
    previsao_valor_custeio = Sequence(lambda n: fake.random_number(digits=3))
    previsao_valor_capital = Sequence(lambda n: fake.random_number(digits=3))
    previsao_valor_livre = Sequence(lambda n: fake.random_number(digits=3))
    saldo_custeio = Sequence(lambda n: fake.random_number(digits=3))
    saldo_capital = Sequence(lambda n: fake.random_number(digits=3))
    saldo_livre = Sequence(lambda n: fake.random_number(digits=3))

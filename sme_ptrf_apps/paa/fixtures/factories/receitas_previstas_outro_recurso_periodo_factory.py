from factory import SubFactory, Sequence
from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.paa.models import ReceitaPrevistaOutroRecursoPeriodo
from sme_ptrf_apps.paa.fixtures.factories import OutroRecursoPeriodoFactory, PaaFactory

fake = Faker("pt_BR")


class ReceitaPrevistaOutroRecursoPeriodoFactory(DjangoModelFactory):
    class Meta:
        model = ReceitaPrevistaOutroRecursoPeriodo

    paa = SubFactory(PaaFactory)
    outro_recurso_periodo = SubFactory(OutroRecursoPeriodoFactory)

    previsao_valor_custeio = Sequence(lambda n: fake.random_number(digits=3))
    previsao_valor_capital = Sequence(lambda n: fake.random_number(digits=3))
    previsao_valor_livre = Sequence(lambda n: fake.random_number(digits=3))
    saldo_custeio = Sequence(lambda n: fake.random_number(digits=3))
    saldo_capital = Sequence(lambda n: fake.random_number(digits=3))
    saldo_livre = Sequence(lambda n: fake.random_number(digits=3))

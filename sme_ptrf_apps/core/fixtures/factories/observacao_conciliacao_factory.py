from factory import SubFactory, Sequence
from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.core.fixtures.factories.associacao_factory import AssociacaoFactory
from sme_ptrf_apps.core.fixtures.factories.periodo_factory import PeriodoFactory
from sme_ptrf_apps.core.fixtures.factories.conta_associacao_factory import ContaAssociacaoFactory
from sme_ptrf_apps.core.models.observacao_conciliacao import ObservacaoConciliacao

fake = Faker("pt_BR")


class ObservacaoConciliacaoFactory(DjangoModelFactory):
    class Meta:
        model = ObservacaoConciliacao

    periodo = SubFactory(PeriodoFactory)
    associacao = SubFactory(AssociacaoFactory)
    conta_associacao = SubFactory(ContaAssociacaoFactory)
    texto = Sequence(lambda n: fake.sentences(5))
    data_extrato = Sequence(lambda n: fake.date(pattern="%Y-%m-%d"))
    saldo_extrato = Sequence(lambda n: fake.random_number(digits=6))

from factory import SubFactory, LazyFunction
from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.receitas.models.repasse import Repasse, StatusRepasse
from sme_ptrf_apps.core.fixtures.factories.associacao_factory import AssociacaoFactory
from sme_ptrf_apps.core.fixtures.factories.conta_associacao_factory import ContaAssociacaoFactory
from sme_ptrf_apps.core.fixtures.factories.acao_associacao_factory import AcaoAssociacaoFactory
from sme_ptrf_apps.core.fixtures.factories.periodo_factory import PeriodoFactory

fake = Faker("pt_BR")


class RepasseFactory(DjangoModelFactory):
    class Meta:
        model = Repasse

    associacao = SubFactory(AssociacaoFactory)
    conta_associacao = SubFactory(ContaAssociacaoFactory)
    acao_associacao = SubFactory(AcaoAssociacaoFactory)
    periodo = SubFactory(PeriodoFactory)

    valor_capital = LazyFunction(lambda: fake.pydecimal(left_digits=6, right_digits=2, positive=True))
    valor_custeio = LazyFunction(lambda: fake.pydecimal(left_digits=6, right_digits=2, positive=True))
    valor_livre = LazyFunction(lambda: fake.pydecimal(left_digits=6, right_digits=2, positive=True))

    status = StatusRepasse.PENDENTE.name

    realizado_capital = False
    realizado_custeio = False
    realizado_livre = False

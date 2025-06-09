from factory import DjangoModelFactory, SubFactory
from faker import Faker
from sme_ptrf_apps.core.fixtures.factories.acao_factory import AcaoFactory
from sme_ptrf_apps.core.fixtures.factories.associacao_factory import AssociacaoFactory
from sme_ptrf_apps.core.models.acao_associacao import AcaoAssociacao

fake = Faker("pt_BR")


class AcaoAssociacaoFactory(DjangoModelFactory):
    class Meta:
        model = AcaoAssociacao

    associacao = SubFactory(AssociacaoFactory)
    acao = SubFactory(AcaoFactory)
    status = "ATIVA"

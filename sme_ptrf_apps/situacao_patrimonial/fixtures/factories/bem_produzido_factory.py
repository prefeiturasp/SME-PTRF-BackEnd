from factory import DjangoModelFactory, SubFactory
from faker import Faker
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido
from sme_ptrf_apps.core.fixtures.factories.associacao_factory import AssociacaoFactory

fake = Faker("pt_BR")


class BemProduzidoFactory(DjangoModelFactory):
    class Meta:
        model = BemProduzido

    associacao = SubFactory(AssociacaoFactory)
    status = BemProduzido.STATUS_INCOMPLETO

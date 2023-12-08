from factory import DjangoModelFactory, SubFactory
from faker import Faker
from sme_ptrf_apps.core.fixtures.factories.acao_associacao_factory import AcaoAssociacaoFactory
from sme_ptrf_apps.core.fixtures.factories.associacao_factory import AssociacaoFactory
from sme_ptrf_apps.core.fixtures.factories.conta_associacao_factory import ContaAssociacaoFactory

from sme_ptrf_apps.despesas.fixtures.factories.despesa_factory import DespesaFactory
from sme_ptrf_apps.despesas.models.rateio_despesa import RateioDespesa
from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CHOICES


fake = Faker()

class RateioDespesaFactory(DjangoModelFactory):
    class Meta:
        model = RateioDespesa

    despesa = SubFactory(DespesaFactory)
    associacao = SubFactory(AssociacaoFactory)
    conta_associacao = SubFactory(ContaAssociacaoFactory)
    acao_associacao = SubFactory(AcaoAssociacaoFactory)
    aplicacao_recurso = fake.random_element(elements=[choice[0] for choice in APLICACAO_CHOICES])
    
    # TODO adicionar outros campos

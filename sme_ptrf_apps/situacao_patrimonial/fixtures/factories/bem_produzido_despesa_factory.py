from factory import DjangoModelFactory, SubFactory
from faker import Faker
from sme_ptrf_apps.despesas.fixtures.factories.despesa_factory import DespesaFactory
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzidoDespesa
from sme_ptrf_apps.situacao_patrimonial.fixtures.factories import BemProduzidoFactory

fake = Faker("pt_BR")


class BemProduzidoDespesaFactory(DjangoModelFactory):
    class Meta:
        model = BemProduzidoDespesa

    bem_produzido = SubFactory(BemProduzidoFactory)
    despesa = SubFactory(DespesaFactory)

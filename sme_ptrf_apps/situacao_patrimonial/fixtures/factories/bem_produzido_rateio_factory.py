from factory import DjangoModelFactory, SubFactory, Sequence
from faker import Faker
from sme_ptrf_apps.despesas.fixtures.factories.rateio_despesa_factory import RateioDespesaFactory
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzidoRateio
from sme_ptrf_apps.situacao_patrimonial.fixtures.factories import BemProduzidoDespesaFactory

fake = Faker("pt_BR")


class BemProduzidoRateioFactory(DjangoModelFactory):
    class Meta:
        model = BemProduzidoRateio

    bem_produzido_despesa = SubFactory(BemProduzidoDespesaFactory)
    rateio = SubFactory(RateioDespesaFactory)
    valor_utilizado = Sequence(lambda n: fake.random_number(digits=3))

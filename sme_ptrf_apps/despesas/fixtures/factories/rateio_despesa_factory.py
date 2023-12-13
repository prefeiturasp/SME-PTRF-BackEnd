from factory import DjangoModelFactory, SubFactory
from faker import Faker
from sme_ptrf_apps.despesas.models import RateioDespesa
from sme_ptrf_apps.core.fixtures.factories import AssociacaoFactory
from .despesa_factory import DespesaFactory
from .especificacao_material_servico_factory import EspecificacaoMaterialServicoFactory
from .tipo_custeio_factory import TipoCusteioFactory

fake = Faker("pt_BR")

class RateioDespesaFactory(DjangoModelFactory):
    class Meta:
        model = RateioDespesa

    despesa = SubFactory(DespesaFactory)
    associacao = SubFactory(AssociacaoFactory)
    especificacao_material_servico = SubFactory(EspecificacaoMaterialServicoFactory)
    tipo_custeio = SubFactory(TipoCusteioFactory)

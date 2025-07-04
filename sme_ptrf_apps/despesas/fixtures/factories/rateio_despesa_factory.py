from factory import DjangoModelFactory, SubFactory, Sequence
from faker import Faker
from sme_ptrf_apps.core.fixtures.factories.acao_associacao_factory import AcaoAssociacaoFactory
from sme_ptrf_apps.core.fixtures.factories.associacao_factory import AssociacaoFactory
from sme_ptrf_apps.core.fixtures.factories.conta_associacao_factory import ContaAssociacaoFactory
from sme_ptrf_apps.despesas.fixtures.factories.despesa_factory import DespesaFactory
from sme_ptrf_apps.despesas.models.rateio_despesa import RateioDespesa
from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CHOICES
from .especificacao_material_servico_factory import EspecificacaoMaterialServicoFactory
from .tipo_custeio_factory import TipoCusteioFactory
fake = Faker("pt_BR")


class RateioDespesaFactory(DjangoModelFactory):
    class Meta:
        model = RateioDespesa

    despesa = SubFactory(DespesaFactory)
    associacao = SubFactory(AssociacaoFactory)
    conta_associacao = SubFactory(ContaAssociacaoFactory)
    acao_associacao = SubFactory(AcaoAssociacaoFactory)
    aplicacao_recurso = fake.random_element(elements=[choice[0] for choice in APLICACAO_CHOICES])
    especificacao_material_servico = SubFactory(EspecificacaoMaterialServicoFactory)
    tipo_custeio = SubFactory(TipoCusteioFactory)
    numero_processo_incorporacao_capital = Sequence(lambda n: fake.text(max_nb_chars=100))
    quantidade_itens_capital = Sequence(lambda n: fake.random_int(min=1, max=9))
    valor_item_capital = Sequence(lambda n: fake.random_int(min=100, max=999))
    valor_rateio = Sequence(lambda n: fake.random_int(min=100, max=999))

from factory import DjangoModelFactory, SubFactory, LazyAttribute
from faker import Faker
from sme_ptrf_apps.despesas.fixtures.factories.despesa_factory import DespesaFactory
from sme_ptrf_apps.despesas.fixtures.factories.especificacao_material_servico_factory import EspecificacaoMaterialServicoFactory
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzidoItem
from sme_ptrf_apps.situacao_patrimonial.fixtures.factories import BemProduzidoFactory

fake = Faker("pt_BR")


class BemProduzidoItemFactory(DjangoModelFactory):
    class Meta:
        model = BemProduzidoItem

    bem_produzido = SubFactory(BemProduzidoFactory)
    especificacao_do_bem = SubFactory(EspecificacaoMaterialServicoFactory)
    num_processo_incorporacao = LazyAttribute(lambda _: fake.bothify(text='????-########'))
    quantidade = LazyAttribute(lambda _: fake.random_number(digits=2))
    valor_individual = LazyAttribute(lambda _: fake.pydecimal(left_digits=4, right_digits=2, positive=True))
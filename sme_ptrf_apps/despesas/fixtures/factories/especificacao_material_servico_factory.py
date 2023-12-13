from factory import DjangoModelFactory, Sequence
from faker import Faker
from sme_ptrf_apps.despesas.models.especificacao_material_servico import EspecificacaoMaterialServico

fake = Faker("pt_BR")

class EspecificacaoMaterialServicoFactory(DjangoModelFactory):
    class Meta:
        model = EspecificacaoMaterialServico


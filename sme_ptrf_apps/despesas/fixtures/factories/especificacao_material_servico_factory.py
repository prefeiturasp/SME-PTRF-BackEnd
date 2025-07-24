from factory import Sequence
from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.despesas.models.especificacao_material_servico import EspecificacaoMaterialServico

fake = Faker("pt_BR")


class EspecificacaoMaterialServicoFactory(DjangoModelFactory):
    class Meta:
        model = EspecificacaoMaterialServico

    descricao = Sequence(lambda n: fake.text(max_nb_chars=200))

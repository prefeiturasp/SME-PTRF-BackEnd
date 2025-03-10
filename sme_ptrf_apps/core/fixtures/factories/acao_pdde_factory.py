from factory import DjangoModelFactory, Sequence, SubFactory
from faker import Faker
from sme_ptrf_apps.core.models.acao_pdde import AcaoPdde
from .categoria_pdde_factory import CategoriaPddeFactory

fake = Faker("pt_BR")


class AcaoPddeFactory(DjangoModelFactory):
    class Meta:
        model = AcaoPdde

    nome = Sequence(lambda n: fake.unique.name())
    categoria = SubFactory(CategoriaPddeFactory)

from factory import DjangoModelFactory, SubFactory, Sequence
from sme_ptrf_apps.users.fixtures.factories.visao_factory import VisaoFactory
from sme_ptrf_apps.users.models import Grupo
from faker import Faker

fake = Faker("pt_BR")

class GrupoAcessoFactory(DjangoModelFactory):
    class Meta:
        model = Grupo

    name = Sequence(lambda n: fake.unique.name())
    descricao = Sequence(lambda n: fake.paragraph(nb_sentences=3))

    @classmethod
    def create(cls, **kwargs):
        visoes = kwargs.pop('visoes', None)
        grupo = super().create(**kwargs)

        if visoes is not None:
            grupo.visoes.set(visoes)
            
        return grupo
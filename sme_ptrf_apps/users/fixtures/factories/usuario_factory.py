from factory import DjangoModelFactory, SubFactory, Sequence
from faker import Faker
from sme_ptrf_apps.users.fixtures.factories.grupo_acesso_factory import GrupoAcessoFactory
from sme_ptrf_apps.users.models import User

fake = Faker("pt_BR")

class UsuarioFactory(DjangoModelFactory):
    class Meta:
        model = User

    name = Sequence(lambda n: fake.unique.name().upper())

    @classmethod
    def create(cls, **kwargs):
        grupos = kwargs.pop('grupos', None)
        user = super().create(**kwargs)

        if grupos is not None:
            user.grupos.set(grupos)
            
        return user
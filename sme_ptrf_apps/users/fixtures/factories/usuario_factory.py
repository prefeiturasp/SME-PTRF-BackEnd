from factory import DjangoModelFactory, Sequence
from faker import Faker
from sme_ptrf_apps.users.models import User

fake = Faker("pt_BR")


class UsuarioFactory(DjangoModelFactory):
    class Meta:
        model = User

    name = Sequence(lambda n: fake.unique.name().upper())
    username = Sequence(lambda n: str(fake.unique.random_int(min=100000, max=999999)))

    @classmethod
    def create(cls, **kwargs):
        grupos = kwargs.pop('grupos', None)
        unidades = kwargs.pop('unidades', None)
        user = super().create(**kwargs)

        if grupos is not None:
            user.grupos.set(grupos)

        if unidades is not None:
            user.unidades.set(unidades)

        return user

from factory import Sequence, LazyFunction
from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.core.models.tipo_conta import TipoConta
from sme_ptrf_apps.core.models.recurso import Recurso

fake = Faker("pt_BR")


class TipoContaFactory(DjangoModelFactory):
    class Meta:
        model = TipoConta

    nome = Sequence(lambda n: f"{fake.word()}_{n:06d}")
    banco_nome = Sequence(lambda n: f"Banco {fake.first_name()} {n:04d}")
    agencia = Sequence(lambda n: f"{(n % 9000) + 1000:04d}-{n % 10}")
    numero_conta = Sequence(lambda n: f"{(n % 90) + 10:02d}.{(n % 900) + 100:03d}-{n % 10}")
    recurso = LazyFunction(lambda: Recurso.objects.get(legado=True))

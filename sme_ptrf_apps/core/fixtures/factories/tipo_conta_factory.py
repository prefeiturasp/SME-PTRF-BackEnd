from factory import DjangoModelFactory, Sequence
from faker import Faker
from sme_ptrf_apps.core.models.tipo_conta import TipoConta

fake = Faker("pt_BR")

class TipoContaFactory(DjangoModelFactory):
    class Meta:
        model = TipoConta
        
    nome = Sequence(lambda n: fake.unique.word())
    banco_nome = Sequence(lambda n: f"Banco {fake.unique.name()}")
    agencia = Sequence(lambda n: f"{str(fake.unique.random_int(min=1000, max=9999))}-{fake.random_number(digits=1)}")
    numero_conta = Sequence(lambda n: f"{str(fake.unique.random_int(min=10, max=99))}.{str(fake.unique.random_int(min=100, max=999))}-{fake.random_number(digits=1)}")
        
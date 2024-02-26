from factory import DjangoModelFactory, Sequence
from faker import Faker
from sme_ptrf_apps.mandatos.models import OcupanteCargo
from ..providers.ocupante_cargo_provider import provider_representacao
import random

fake = Faker("pt_BR")
fake.add_provider(provider_representacao)


class OcupanteCargoFactory(DjangoModelFactory):
    class Meta:
        model = OcupanteCargo

    nome = Sequence(lambda n: f"{fake.unique.name()}")
    codigo_identificacao = Sequence(lambda n: str(fake.unique.random_int(min=100000, max=999999)))
    cargo_educacao = Sequence(lambda n: random.choice(["Professor I", "Professor II", "Professor III", "Diretor"]))
    representacao = fake.provider_representacao()
    email = Sequence(lambda n: fake.unique.email())
    cpf_responsavel = Sequence(lambda n: str(fake.unique.random_int(min=100000, max=999999)))
    telefone = Sequence(lambda n: fake.unique.phone_number())
    cep = Sequence(lambda n: str(fake.unique.random_int(min=10000000, max=99999999)))
    bairro = Sequence(lambda n: f"{fake.unique.name()}")
    endereco = Sequence(lambda n: f"{fake.address()}")

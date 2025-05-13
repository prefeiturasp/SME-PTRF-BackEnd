from faker import Faker
from factory import DjangoModelFactory, SubFactory, Sequence
from factory.fuzzy import FuzzyChoice
from sme_ptrf_apps.core.models.membro_associacao import MembroAssociacao
from sme_ptrf_apps.core.choices.membro_associacao import MembroEnum, RepresentacaoCargo

fake = Faker("pt_BR")


class MembroAssociacaoFactory(DjangoModelFactory):
    class Meta:
        model = MembroAssociacao

    nome = Sequence(lambda n: fake.name())
    associacao = SubFactory("sme_ptrf_apps.core.fixtures.factories.associacao_factory.AssociacaoFactory")

    cargo_associacao = FuzzyChoice([e.value for e in MembroEnum])
    cargo_educacao = Sequence(lambda n: fake.job())

    representacao = FuzzyChoice([e.name for e in RepresentacaoCargo])
    codigo_identificacao = Sequence(lambda n: str(fake.random_number(digits=6, fix_len=True)))
    email = Sequence(lambda n: fake.unique.email())
    cpf = Sequence(lambda n: fake.unique.cpf())
    telefone = Sequence(lambda n: fake.phone_number())
    cep = Sequence(lambda n: fake.postcode())
    bairro = Sequence(lambda n: fake.bairro())
    endereco = Sequence(lambda n: fake.street_address())

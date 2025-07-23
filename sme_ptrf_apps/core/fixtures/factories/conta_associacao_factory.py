from factory import SubFactory, Sequence
from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.core.models.conta_associacao import ContaAssociacao
from sme_ptrf_apps.core.fixtures.factories.associacao_factory import AssociacaoFactory
from sme_ptrf_apps.core.fixtures.factories.tipo_conta_factory import TipoContaFactory

fake = Faker("pt_BR")


class ContaAssociacaoFactory(DjangoModelFactory):
    class Meta:
        model = ContaAssociacao

    associacao = SubFactory(AssociacaoFactory)
    tipo_conta = SubFactory(TipoContaFactory)
    banco_nome = Sequence(lambda n: f"Banco {fake.unique.name()}")
    agencia = Sequence(lambda n: f"{str(fake.unique.random_int(min=1000, max=9999))}-{fake.random_number(digits=1)}")
    numero_conta = Sequence(
        lambda n: f"{str(fake.unique.random_int(min=10, max=99))}.{str(fake.unique.random_int(min=100, max=999))}-{fake.random_number(digits=1)}")
    data_inicio = Sequence(lambda n: fake.date(pattern="%Y-%m-%d"))

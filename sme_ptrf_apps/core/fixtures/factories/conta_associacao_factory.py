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
    banco_nome = Sequence(lambda n: f"Banco {fake.first_name()} {n:04d}")
    agencia = Sequence(lambda n: f"{(n % 9000) + 1000:04d}-{n % 10}")
    numero_conta = Sequence(lambda n: f"{(n % 90) + 10:02d}.{(n % 900) + 100:03d}-{n % 10}")
    data_inicio = Sequence(lambda n: fake.date(pattern="%Y-%m-%d"))

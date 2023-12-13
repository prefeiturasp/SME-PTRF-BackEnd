from factory import DjangoModelFactory, Sequence, SubFactory
from faker import Faker
from sme_ptrf_apps.despesas.models.despesa import Despesa
from .tipo_transacao_factory import TipoTransacaoFactory
from .tipo_documento_factory import TipoDocumentoFactory
from sme_ptrf_apps.core.fixtures.factories import AssociacaoFactory

fake = Faker("pt_BR")

class DespesaFactory(DjangoModelFactory):
    class Meta:
        model = Despesa

    associacao = SubFactory(AssociacaoFactory)
    cpf_cnpj_fornecedor = Sequence(lambda n: fake.unique.cnpj())
    nome_fornecedor = Sequence(lambda n: fake.name())
    numero_documento = Sequence(lambda n: f"{str(fake.unique.random_int(min=10000, max=99999))}")
    documento_transacao = Sequence(lambda n: f"{str(fake.unique.random_int(min=10000, max=99999))}")
    tipo_transacao = SubFactory(TipoTransacaoFactory)
    tipo_documento = SubFactory(TipoDocumentoFactory)
    data_documento = Sequence(lambda n: fake.unique.date())
    data_transacao = Sequence(lambda n: fake.unique.date())
    valor_total = Sequence(lambda n: fake.random_number(digits=3))

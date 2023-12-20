from factory import DjangoModelFactory, SubFactory, Sequence
from faker import Faker

from sme_ptrf_apps.core.fixtures.factories.associacao_factory import AssociacaoFactory
from sme_ptrf_apps.despesas.models.despesa import Despesa

from .tipo_transacao_factory import TipoTransacaoFactory
from .tipo_documento_factory import TipoDocumentoFactory

fake = Faker("pt_BR")

class DespesaFactory(DjangoModelFactory):
    class Meta:
        model = Despesa

    associacao = SubFactory(AssociacaoFactory)
    cpf_cnpj_fornecedor = Sequence(lambda n: fake.unique.cnpj())
    nome_fornecedor = fake.company()
    numero_documento = Sequence(lambda n: f"{str(fake.unique.random_int(min=10000, max=99999))}")
    documento_transacao = Sequence(lambda n: f"{str(fake.unique.random_int(min=10000, max=99999))}")
    tipo_transacao = SubFactory(TipoTransacaoFactory)
    tipo_documento = SubFactory(TipoDocumentoFactory)
    data_documento = fake.date_this_year()
    data_transacao = fake.date_this_year()
    valor_total = Sequence(lambda n: fake.random_number(digits=3))

    eh_despesa_sem_comprovacao_fiscal = fake.pybool()
    eh_despesa_reconhecida_pela_associacao = fake.pybool()
    numero_boletim_de_ocorrencia = Sequence(lambda n: f"BO-{n}")

    # TODO adicionar outros campos

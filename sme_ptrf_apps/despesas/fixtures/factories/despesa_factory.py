from factory import DjangoModelFactory, SubFactory, Sequence
from faker import Faker

from sme_ptrf_apps.core.fixtures.factories.associacao_factory import AssociacaoFactory
from sme_ptrf_apps.despesas.models.despesa import Despesa


fake = Faker("pt_BR")

class DespesaFactory(DjangoModelFactory):
    class Meta:
        model = Despesa

    associacao = SubFactory(AssociacaoFactory)
    numero_documento = Sequence(lambda n: f"DOC-{n}")
    data_documento = fake.date_this_year()
    cpf_cnpj_fornecedor = Sequence(lambda n: fake.unique.cnpj())
    nome_fornecedor = fake.company()
    documento_transacao = Sequence(lambda n: f"TRAN-{n}")
    data_transacao = fake.date_this_year()
    eh_despesa_sem_comprovacao_fiscal = fake.pybool()
    eh_despesa_reconhecida_pela_associacao = fake.pybool()
    numero_boletim_de_ocorrencia = Sequence(lambda n: f"BO-{n}")

    # TODO adicionar outros campos
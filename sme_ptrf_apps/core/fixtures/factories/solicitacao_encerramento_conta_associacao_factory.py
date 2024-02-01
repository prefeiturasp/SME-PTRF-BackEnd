from factory import DjangoModelFactory, SubFactory, Sequence
from faker import Faker
from sme_ptrf_apps.core.fixtures.factories.conta_associacao_factory import ContaAssociacaoFactory
from sme_ptrf_apps.core.models.solicitacao_encerramento_conta_associacao import SolicitacaoEncerramentoContaAssociacao
from ..providers.solicitacao_encerramento_conta_associacao_provider import provider_status_solicitacao_encerramento_conta_associacao

fake = Faker("pt_BR")
fake.add_provider(provider_status_solicitacao_encerramento_conta_associacao)


class SolicitacaoEncerramentoContaAssociacaoFactory(DjangoModelFactory):
    class Meta:
        model = SolicitacaoEncerramentoContaAssociacao

    conta_associacao = SubFactory(ContaAssociacaoFactory)
    status = fake.provider_status_solicitacao_encerramento_conta_associacao()
    data_de_encerramento_na_agencia = fake.past_date()
    # TODO adicionar campos restantes

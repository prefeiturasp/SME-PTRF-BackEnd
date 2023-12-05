from faker.providers import DynamicProvider
from sme_ptrf_apps.core.models.solicitacao_encerramento_conta_associacao import SolicitacaoEncerramentoContaAssociacao

provider_status_solicitacao_encerramento_conta_associacao = DynamicProvider(
     provider_name="provider_status_solicitacao_encerramento_conta_associacao",
     elements=[choice[0] for choice in SolicitacaoEncerramentoContaAssociacao.STATUS_CHOICES]
)
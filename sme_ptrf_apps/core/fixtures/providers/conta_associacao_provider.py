from faker.providers import DynamicProvider
from sme_ptrf_apps.core.models.conta_associacao import ContaAssociacao

provider_status_conta_associacao = DynamicProvider(
     provider_name="provider_status_conta_associacao",
     elements=ContaAssociacao.STATUS_CHOICES
)
from faker.providers import DynamicProvider
from sme_ptrf_apps.core.models.arquivo import Arquivo

provider_tipo_carga_arquivo = DynamicProvider(
     provider_name="provider_tipo_carga_arquivo",
     elements=[choice[0] for choice in Arquivo.CARGA_CHOICES]
)
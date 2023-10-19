from faker.providers import DynamicProvider
from sme_ptrf_apps.core.choices.tipos_unidade import TIPOS_CHOICE

provider_tipos_de_unidades_desconsiderando_tipo_dre = DynamicProvider(
     provider_name="provider_tipos_de_unidades_desconsiderando_tipo_dre",
     elements=[choice[0] for choice in TIPOS_CHOICE if choice[0] != 'DRE']
)

provider_anos_dre_designacao_ano = DynamicProvider(
     provider_name="provider_anos_dre_designacao_ano",
     elements=['2016','2017','2019','2020','2022']
)
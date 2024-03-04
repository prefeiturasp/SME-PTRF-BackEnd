from faker.providers import DynamicProvider
from sme_ptrf_apps.mandatos.models.cargo_composicao import CargoComposicao


provider_cargo_associacao = DynamicProvider(
    provider_name="provider_cargo_associacao",
    elements=[choice[0] for choice in CargoComposicao.CARGO_ASSOCIACAO_CHOICES]
)

from faker.providers import DynamicProvider
from sme_ptrf_apps.mandatos.models.ocupante_cargo import OcupanteCargo


provider_representacao = DynamicProvider(
    provider_name="provider_representacao",
    elements=[choice[0] for choice in OcupanteCargo.REPRESENTACAO_CARGO_CHOICES]
)

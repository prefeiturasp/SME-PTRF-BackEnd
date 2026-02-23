import pytest

from sme_ptrf_apps.core.models import Recurso


@pytest.fixture(autouse=True)
def recurso_legado_setup(db):
    Recurso.objects.get_or_create(
        nome="Programa de Transferência de Recursos Financeiros - PTRF",
        defaults={
            "nome_exibicao": "PTRF",
            "cor": "#01585E",
            "legado": True,
        },
    )

import pytest
from sme_ptrf_apps.despesas.api.serializers.motivo_pagamento_antecipado_serializer import (
    MotivoPagamentoAntecipadoSerializer
)
from ...models.motivo_pagamento_antecipado import MotivoPagamentoAntecipado

pytestmark = pytest.mark.django_db


def test_serializer(motivo_pagamento_adiantado_01):

    serializer = MotivoPagamentoAntecipadoSerializer(motivo_pagamento_adiantado_01)

    assert serializer.data['id']
    assert serializer.data['motivo']


def test_create_motivo_pagamento_antecipado_success():
    """
    Testa a criação de um MotivoPagamentoAntecipado com dados válidos.
    """
    data = {
        "motivo": "Motivo Teste",
    }

    serializer = MotivoPagamentoAntecipadoSerializer(data=data)
    assert serializer.is_valid(), f"Erros: {serializer.errors}"

    motivo_pagamento_antecipado = serializer.save()
    assert motivo_pagamento_antecipado.motivo == data["motivo"]
    assert MotivoPagamentoAntecipado.objects.count() == 1


def test_update_motivo_pagamento_antecipado_success(motivo_pagamento_antecipado):
    """
    Testa a atualização de um MotivoPagamentoAntecipado com um nome novo.
    """
    data = {
        "motivo": "Motivo Atualizado",
    }

    serializer = MotivoPagamentoAntecipadoSerializer(instance=motivo_pagamento_antecipado, data=data, partial=True)
    assert serializer.is_valid(), f"Erros: {serializer.errors}"

    motivo_pagamento_antecipado_atualizado = serializer.save()
    assert motivo_pagamento_antecipado_atualizado.motivo == "Motivo Atualizado"

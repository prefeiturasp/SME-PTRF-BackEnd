import pytest

from sme_ptrf_apps.despesas.api.serializers.motivo_pagamento_antecipado_serializer import MotivoPagamentoAntecipadoSerializer

pytestmark = pytest.mark.django_db


def test_serializer(motivo_pagamento_adiantado_01):

    serializer = MotivoPagamentoAntecipadoSerializer(motivo_pagamento_adiantado_01)

    assert serializer.data['id']
    assert serializer.data['motivo']

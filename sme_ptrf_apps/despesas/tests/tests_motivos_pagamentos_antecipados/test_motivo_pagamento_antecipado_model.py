import pytest
from django.contrib import admin
from sme_ptrf_apps.despesas.models import MotivoPagamentoAntecipado

pytestmark = pytest.mark.django_db


def test_model_instance(motivo_pagamento_adiantado_01):
    model = motivo_pagamento_adiantado_01

    assert isinstance(model, MotivoPagamentoAntecipado)


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[MotivoPagamentoAntecipado]


def test_srt_model(motivo_pagamento_adiantado_01):
    assert motivo_pagamento_adiantado_01.__str__() == 'Motivo de pagamento adiantado 01'


def test_meta_modelo(motivo_pagamento_adiantado_01):
    assert motivo_pagamento_adiantado_01._meta.verbose_name == 'Motivo de pagamento antecipado'
    assert motivo_pagamento_adiantado_01._meta.verbose_name_plural == 'Motivos de pagamento antecipado'


def test_audit_log(motivo_pagamento_adiantado_01):
    assert motivo_pagamento_adiantado_01.history.count() == 1  # Um log de inclusão
    assert motivo_pagamento_adiantado_01.history.latest().action == 0  # 0-Inclusão

    motivo_pagamento_adiantado_01.motivo = "TESTE"
    motivo_pagamento_adiantado_01.save()
    assert motivo_pagamento_adiantado_01.history.count() == 2  # Um log de inclusão e outro de edição
    assert motivo_pagamento_adiantado_01.history.latest().action == 1  # 1-Edição

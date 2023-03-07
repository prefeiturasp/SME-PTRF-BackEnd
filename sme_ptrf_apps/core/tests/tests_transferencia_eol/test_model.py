import pytest
from django.contrib import admin

from ...models import TransferenciaEol

pytestmark = pytest.mark.django_db


def test_model_transferencia_eol(transferencia_eol):
    model = transferencia_eol
    assert model.eol_transferido
    assert model.eol_historico
    assert model.tipo_nova_unidade
    assert model.data_inicio_atividades
    assert model.tipo_conta_transferido
    assert model.status_processamento
    assert model.log_execucao


def test_transferencia_eol_admin():
    # pylint: disable=W0212
    assert admin.site._registry[TransferenciaEol]

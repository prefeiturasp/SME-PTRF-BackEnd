import pytest

from freezegun import freeze_time

from ....core.models import Notificacao, Periodo
from ....core.services.notificacao_services import notificar_inicio_periodo_prestacao_de_contas

pytestmark = pytest.mark.django_db


@freeze_time("2021-06-17")
def test_deve_notificar_usuarios(periodo_2021_3_pc_2021_06_12_a_2021_06_17, usuario_notificavel):
    assert not Notificacao.objects.exists()
    notificar_inicio_periodo_prestacao_de_contas()
    assert Notificacao.objects.count() == 1


@freeze_time("2021-06-17")
def test_nao_deve_notificar_usuarios_sem_permissao(periodo_2021_3_pc_2021_06_12_a_2021_06_17, usuario_nao_notificavel):
    assert not Notificacao.objects.exists()
    notificar_inicio_periodo_prestacao_de_contas()
    assert Notificacao.objects.count() == 0


@freeze_time("2021-06-17")
def test_nao_deve_notificar_usuarios_periodo_invalido(periodo_2021_4_pc_2021_06_18_a_2021_06_30, usuario_notificavel):
    assert not Notificacao.objects.exists()
    notificar_inicio_periodo_prestacao_de_contas()
    assert Notificacao.objects.count() == 0


@freeze_time("2021-06-17")
def test_deve_flagar_periodo_como_notificado(periodo_2021_3_pc_2021_06_12_a_2021_06_17, usuario_notificavel):
    assert not periodo_2021_3_pc_2021_06_12_a_2021_06_17.notificacao_inicio_periodo_pc_realizada
    notificar_inicio_periodo_prestacao_de_contas()
    periodo = Periodo.objects.get(referencia="2021.3")
    assert periodo.notificacao_inicio_periodo_pc_realizada

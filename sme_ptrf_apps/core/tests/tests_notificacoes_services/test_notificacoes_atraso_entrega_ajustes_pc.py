import pytest

from freezegun import freeze_time

from ....core.models import Notificacao
from ....core.services.notificacao_services import notificar_atraso_entrega_ajustes_prestacao_de_contas
from ....core.services.notificacao_services import formata_data_dd_mm_yyyy

pytestmark = pytest.mark.django_db


@freeze_time("2021-06-19")
def test_deve_notificar_usuarios(devolucao_notifica_atraso_entrega_ajustes_pc, usuario_notificavel, associacao_a):
    assert not Notificacao.objects.exists()
    notificar_atraso_entrega_ajustes_prestacao_de_contas(enviar_email=False)
    assert Notificacao.objects.count() == 1
    notificacao = Notificacao.objects.first()

    assert notificacao.tipo == Notificacao.TIPO_NOTIFICACAO_ALERTA
    assert notificacao.categoria == Notificacao.CATEGORIA_NOTIFICACAO_ANALISE_PC
    assert notificacao.remetente == Notificacao.REMETENTE_NOTIFICACAO_SISTEMA
    assert notificacao.titulo == f"Devolução de ajustes na PC atrasada {devolucao_notifica_atraso_entrega_ajustes_pc.prestacao_conta.periodo.referencia} | Prazo: {formata_data_dd_mm_yyyy(devolucao_notifica_atraso_entrega_ajustes_pc.data_limite_ue)}"
    assert notificacao.descricao == f"Sua unidade ainda não enviou os ajustes solicitados pela DRE em sua prestação de contas do período {devolucao_notifica_atraso_entrega_ajustes_pc.prestacao_conta.periodo.referencia}. O seu prazo era {formata_data_dd_mm_yyyy(devolucao_notifica_atraso_entrega_ajustes_pc.data_limite_ue)}"
    assert notificacao.usuario == usuario_notificavel


@freeze_time("2021-06-19")
def test_nao_deve_notificar_usuarios_sem_permissao(devolucao_notifica_atraso_entrega_ajustes_pc, usuario_nao_notificavel, associacao_a):
    assert not Notificacao.objects.exists()
    notificar_atraso_entrega_ajustes_prestacao_de_contas()
    assert Notificacao.objects.count() == 0


@freeze_time("2021-06-15")
def test_nao_deve_notificar_usuarios_data_invalida(devolucao_notifica_atraso_entrega_ajustes_pc, usuario_notificavel, associacao_a):
    assert not Notificacao.objects.exists()
    notificar_atraso_entrega_ajustes_prestacao_de_contas()
    assert Notificacao.objects.count() == 0


@freeze_time("2021-06-17")
def test_nao_deve_notificar_usuarios_pc_em_analise(devolucao_notifica_atraso_entrega_ajustes_pc, usuario_notificavel, associacao_a):
    assert not Notificacao.objects.exists()
    notificar_atraso_entrega_ajustes_prestacao_de_contas()
    assert Notificacao.objects.count() == 0

import pytest

from freezegun import freeze_time

from ....core.models import Notificacao
from ....core.services.notificacao_services import notificar_proximidade_fim_prazo_ajustes_prestacao_de_contas

pytestmark = pytest.mark.django_db


@freeze_time("2021-06-21")
def test_deve_notificar_usuarios_5_dias_antes(
    associacao_a,
    usuario_notificavel,
    usuario_nao_notificavel,
    devolucao_notifica_proximidade_fim_entrega_ajustes_pc,
    parametro_proximidade_fim_entrega_ajustes_5_dias,
):

    assert not Notificacao.objects.exists()

    notificar_proximidade_fim_prazo_ajustes_prestacao_de_contas()

    assert Notificacao.objects.count() == 1

    notificacao = Notificacao.objects.first()

    assert notificacao.tipo == Notificacao.TIPO_NOTIFICACAO_INFORMACAO
    assert notificacao.categoria == Notificacao.CATEGORIA_NOTIFICACAO_ANALISE_PC
    assert notificacao.remetente == Notificacao.REMETENTE_NOTIFICACAO_SISTEMA
    assert notificacao.titulo == f"O prazo para envio dos ajustes da PC está se aproximando {devolucao_notifica_proximidade_fim_entrega_ajustes_pc.prestacao_conta.periodo.referencia}"
    assert notificacao.descricao == f"Faltam apenas 5 dia(s) para o fim do prazo de envio dos ajustes de sua prestações de contas de {devolucao_notifica_proximidade_fim_entrega_ajustes_pc.prestacao_conta.periodo.referencia}. Fique atento para não perder o prazo e realize os ajustes solicitados."
    assert notificacao.usuario == usuario_notificavel


@freeze_time("2021-06-26")
def test_deve_notificar_usuarios_no_dia(
    associacao_a,
    usuario_notificavel,
    usuario_nao_notificavel,
    devolucao_notifica_proximidade_fim_entrega_ajustes_pc,
    parametro_proximidade_fim_entrega_ajustes_5_dias,
):

    assert not Notificacao.objects.exists()

    notificar_proximidade_fim_prazo_ajustes_prestacao_de_contas()

    assert Notificacao.objects.count() == 1


@freeze_time("2021-06-21")
def test_nao_deve_notificar_usuarios_sem_permissao(
    associacao_a,
    usuario_nao_notificavel,
    devolucao_notifica_proximidade_fim_entrega_ajustes_pc,
    parametro_proximidade_fim_entrega_ajustes_5_dias,
):
    assert not Notificacao.objects.exists()
    notificar_proximidade_fim_prazo_ajustes_prestacao_de_contas()
    assert Notificacao.objects.count() == 0


@freeze_time("2021-06-15")
def test_nao_deve_notificar_usuarios_data_invalida(
    associacao_a,
    usuario_notificavel,
    usuario_nao_notificavel,
    devolucao_notifica_proximidade_fim_entrega_ajustes_pc,
    parametro_proximidade_fim_entrega_ajustes_5_dias,
):
    assert not Notificacao.objects.exists()
    notificar_proximidade_fim_prazo_ajustes_prestacao_de_contas()
    assert Notificacao.objects.count() == 0


@freeze_time("2021-06-21")
def test_nao_deve_notificar_usuarios_pc_em_analise(
    devolucao_nao_notifica_proximidade_fim_entrega_ajustes_pc_em_analise,
    usuario_notificavel,
    associacao_a
):
    assert not Notificacao.objects.exists()
    notificar_proximidade_fim_prazo_ajustes_prestacao_de_contas()
    assert Notificacao.objects.count() == 0

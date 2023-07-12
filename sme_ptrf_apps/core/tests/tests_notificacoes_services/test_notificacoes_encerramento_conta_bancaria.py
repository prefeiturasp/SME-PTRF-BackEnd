import pytest

from ....core.models import Notificacao
from sme_ptrf_apps.core.services.notificacao_services import notificar_encerramento_conta_bancaria

pytestmark = pytest.mark.django_db


def test_deve_notificar_usuarios_encerramento_conta(
    fechamento_periodo_2021_1_encerramento_conta,
    fechamento_periodo_2020_2_encerramento_conta,
    parametro_numero_periodos_consecutivos,
    conta_associacao_encerramento_conta,
    usuario_notificavel
):
    assert not Notificacao.objects.exists()
    notificar_encerramento_conta_bancaria(enviar_email=False)
    assert Notificacao.objects.count() == 1
    notificacao = Notificacao.objects.first()

    assert notificacao.tipo == Notificacao.TIPO_NOTIFICACAO_AVISO
    assert notificacao.categoria == Notificacao.CATEGORIA_NOTIFICACAO_ENCERRAMENTO_CONTA_BANCARIA
    assert notificacao.remetente == Notificacao.REMETENTE_NOTIFICACAO_SISTEMA
    assert notificacao.titulo == "Encerramento de Conta Bancária"
    assert notificacao.descricao == f"O saldo da conta bancária {conta_associacao_encerramento_conta.tipo_conta.nome} está zerada, caso deseje, o encerramento da conta pode ser solicitada. Acesse a página Dados das contas para validar."
    assert notificacao.usuario == usuario_notificavel


def test_nao_deve_notificar_usuarios_sem_permissao_encerramento_conta(
    usuario_nao_notificavel
):
    assert not Notificacao.objects.exists()
    notificar_encerramento_conta_bancaria(enviar_email=False)
    assert Notificacao.objects.count() == 0


def test_nao_deve_notificar_usuarios_que_tipo_conta_nao_permite_inativacao(
    fechamento_periodo_2021_1_encerramento_conta,
    fechamento_periodo_2020_2_encerramento_conta,
    parametro_numero_periodos_consecutivos,
    conta_associacao_encerramento_conta,
    conta_associacao_sem_permissao_encerramento_conta,
    usuario_notificavel
):
    assert not Notificacao.objects.exists()
    notificar_encerramento_conta_bancaria(enviar_email=False)
    # Apenas uma das contas tem permissão de inativação
    assert Notificacao.objects.count() == 1


def test_nao_deve_notificar_associacoes_que_parametro_e_maior_que_periodos_da_associacao(
    fechamento_periodo_2021_1_encerramento_conta,
    fechamento_periodo_2020_2_encerramento_conta,
    parametro_numero_periodos_consecutivos_02,
    conta_associacao_encerramento_conta,
    conta_associacao_sem_permissao_encerramento_conta,
    usuario_notificavel
):
    assert not Notificacao.objects.exists()
    notificar_encerramento_conta_bancaria(enviar_email=False)
    assert Notificacao.objects.count() == 0


def test_nao_deve_notificar_associacoes_que_periodos_consecutivos_nao_estao_zerados(
    fechamento_periodo_2021_1_encerramento_conta_com_valores,
    fechamento_periodo_2020_2_encerramento_conta,
    parametro_numero_periodos_consecutivos,
    conta_associacao_encerramento_conta,
    conta_associacao_sem_permissao_encerramento_conta,
    usuario_notificavel
):
    assert not Notificacao.objects.exists()
    notificar_encerramento_conta_bancaria(enviar_email=False)
    assert Notificacao.objects.count() == 0


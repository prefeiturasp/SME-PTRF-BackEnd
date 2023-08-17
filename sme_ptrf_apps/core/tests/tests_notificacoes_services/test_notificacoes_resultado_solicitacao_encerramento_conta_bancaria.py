import pytest

from ....core.models import Notificacao
from sme_ptrf_apps.core.services.notificacao_services import notificar_resultado_solicitacao_encerramento_conta_bancaria

pytestmark = pytest.mark.django_db


def test_deve_notificar_usuarios_aprovacao_solicitacao_encerramento_conta(
    conta_associacao_encerramento_conta,
    solicitacao_encerramento_conta_aprovada,
    usuario_notificavel
):
    assert not Notificacao.objects.exists()

    notificar_resultado_solicitacao_encerramento_conta_bancaria(
        conta_associacao=conta_associacao_encerramento_conta, resultado=solicitacao_encerramento_conta_aprovada.status
    )

    assert Notificacao.objects.count() == 1

    notificacao = Notificacao.objects.first()

    descricao = f"A {conta_associacao_encerramento_conta.associacao.unidade.nome_dre} " \
                f"aprovou a sua solicitação de encerramento de sua conta bancária " \
                f"{conta_associacao_encerramento_conta.tipo_conta.nome}. Sua conta já está encerrada."

    assert notificacao.tipo == Notificacao.TIPO_NOTIFICACAO_AVISO
    assert notificacao.categoria == Notificacao.CATEGORIA_NOTIFICACAO_ENCERRAMENTO_CONTA_BANCARIA
    assert notificacao.remetente == Notificacao.REMETENTE_NOTIFICACAO_DRE
    assert notificacao.titulo == "Aprovação de solicitação de encerramento de conta bancária"
    assert notificacao.descricao == descricao
    assert notificacao.usuario == usuario_notificavel


def test_deve_notificar_usuarios_rejeicao_solicitacao_encerramento_conta(
    conta_associacao_encerramento_conta,
    solicitacao_encerramento_conta_rejeitada,
    usuario_notificavel
):
    assert not Notificacao.objects.exists()

    notificar_resultado_solicitacao_encerramento_conta_bancaria(
        conta_associacao=conta_associacao_encerramento_conta, resultado=solicitacao_encerramento_conta_rejeitada.status
    )

    assert Notificacao.objects.count() == 1

    notificacao = Notificacao.objects.first()

    descricao = f"A {conta_associacao_encerramento_conta.associacao.unidade.nome_dre} " \
                f"rejeitou a sua solicitação de encerramento de sua conta bancária " \
                f"{conta_associacao_encerramento_conta.tipo_conta.nome}. Sua conta continua ativa."

    assert notificacao.tipo == Notificacao.TIPO_NOTIFICACAO_AVISO
    assert notificacao.categoria == Notificacao.CATEGORIA_NOTIFICACAO_ENCERRAMENTO_CONTA_BANCARIA
    assert notificacao.remetente == Notificacao.REMETENTE_NOTIFICACAO_DRE
    assert notificacao.titulo == "Rejeição de solicitação de encerramento de conta bancária"
    assert notificacao.descricao == descricao
    assert notificacao.usuario == usuario_notificavel


def test_nao_deve_notificar_usuarios_resultado_encerramento_conta_pendente(
    conta_associacao_encerramento_conta,
    solicitacao_encerramento_conta_pendente,
    usuario_notificavel
):
    assert not Notificacao.objects.exists()
    notificar_resultado_solicitacao_encerramento_conta_bancaria(
        conta_associacao=conta_associacao_encerramento_conta, resultado=solicitacao_encerramento_conta_pendente.status
    )
    assert Notificacao.objects.count() == 0


def test_nao_deve_notificar_usuarios_que_nao_sao_dessa_associacao(
    conta_associacao_encerramento_conta,
    solicitacao_encerramento_conta_aprovada,
    usuario_notificavel_que_nao_possui_unidade_encerramento_conta
):
    # Este usuário não possui vinculo com a associação que solicitou o encerramento
    assert not Notificacao.objects.exists()
    notificar_resultado_solicitacao_encerramento_conta_bancaria(
        conta_associacao=conta_associacao_encerramento_conta, resultado=solicitacao_encerramento_conta_aprovada.status
    )
    assert Notificacao.objects.count() == 0


def test_nao_deve_notificar_usuarios_sem_permissao_resultado_encerramento_conta(
    conta_associacao_encerramento_conta,
    solicitacao_encerramento_conta_rejeitada,
    usuario_nao_notificavel
):
    assert not Notificacao.objects.exists()
    notificar_resultado_solicitacao_encerramento_conta_bancaria(
        conta_associacao=conta_associacao_encerramento_conta, resultado=solicitacao_encerramento_conta_rejeitada.status
    )
    assert Notificacao.objects.count() == 0

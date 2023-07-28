import pytest

from ....core.models import Notificacao
from sme_ptrf_apps.core.services.notificacao_services import notificar_solicitacao_encerramento_conta_bancaria

pytestmark = pytest.mark.django_db


def test_deve_notificar_usuario_solicitacao_encerramento_conta_que_eh_membro_comissao_contas(
    conta_associacao_encerramento_conta,
    usuario_notificavel,
    parametro_comissao_exame_conta,
    membro_jaozin_comissao_a,
    usuario_notificavel_que_nao_pertence_a_comissao_contas,
    membro_pedrin_comissao_b
):
    # Apenas o membro_jaozin_comissao_a pertence a comissao de contas

    assert not Notificacao.objects.exists()
    notificar_solicitacao_encerramento_conta_bancaria(conta_associacao=conta_associacao_encerramento_conta)
    assert Notificacao.objects.count() == 1
    notificacao = Notificacao.objects.first()

    descricao = f"A Associação da {conta_associacao_encerramento_conta.associacao.unidade.nome_com_tipo} " \
                f"solicitou o encerramento da conta bancária " \
                f"{conta_associacao_encerramento_conta.tipo_conta.nome}. " \
                f"Acesse a página da Associação na Consulta de Associações para validar."

    assert notificacao.tipo == Notificacao.TIPO_NOTIFICACAO_AVISO
    assert notificacao.categoria == Notificacao.CATEGORIA_NOTIFICACAO_ENCERRAMENTO_CONTA_BANCARIA
    assert notificacao.remetente == Notificacao.REMETENTE_NOTIFICACAO_ASSOCIACAO
    assert notificacao.titulo == "Solicitação de encerramento de conta bancária"
    assert notificacao.descricao == descricao
    assert notificacao.usuario == usuario_notificavel


def test_nao_deve_notificar_usuario_solicitacao_encerramento_conta_que_nao_eh_membro_comissao_contas(
    conta_associacao_encerramento_conta,
    parametro_comissao_exame_conta,
    usuario_notificavel_que_nao_pertence_a_comissao_contas,
    membro_pedrin_comissao_b
):
    # O membro_pedrin_comissao_b não pertence a comissao de contas

    assert not Notificacao.objects.exists()
    notificar_solicitacao_encerramento_conta_bancaria(conta_associacao=conta_associacao_encerramento_conta)
    assert Notificacao.objects.count() == 0


def test_nao_deve_notificar_usuarios_sem_permissao_solicitacao_encerramento_conta(
    usuario_nao_notificavel,
    conta_associacao_encerramento_conta,
    membro_jaozin_comissao_a,
    parametro_comissao_exame_conta
):
    assert not Notificacao.objects.exists()
    notificar_solicitacao_encerramento_conta_bancaria(conta_associacao=conta_associacao_encerramento_conta)
    assert Notificacao.objects.count() == 0


def test_nao_deve_notificar_membro_comissao_de_contas_que_nao_eh_usuario_sistema(
    membro_ramonzin_comissao_a,
    conta_associacao_encerramento_conta,
    parametro_comissao_exame_conta
):
    assert not Notificacao.objects.exists()
    notificar_solicitacao_encerramento_conta_bancaria(conta_associacao=conta_associacao_encerramento_conta)
    assert Notificacao.objects.count() == 0


def test_nao_deve_notificar_usuarios_membros_comissao_de_contas_de_outra_dre(
    conta_associacao_encerramento_conta,
    membro_thiaguin_comissao_a,
    usuario_notificavel_que_pertence_a_comissao_contas_em_outra_dre,
    parametro_comissao_exame_conta
):
    # O membro_thiaguin_comissao_a pertence a comissão de contas de
    # uma DRE diferente da conta_associacao_encerramento_conta

    assert not Notificacao.objects.exists()
    notificar_solicitacao_encerramento_conta_bancaria(conta_associacao=conta_associacao_encerramento_conta)
    assert Notificacao.objects.count() == 0

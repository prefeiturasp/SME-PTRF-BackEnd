import pytest

from ....core.models import Notificacao
from ....core.services.notificacao_services import notificar_prestacao_de_contas_reprovada

pytestmark = pytest.mark.django_db


def test_deve_notificar_usuarios(prestacao_notifica_pc_reprovada, motivo_reprovacao_x, usuario_notificavel, associacao_a):
    assert not Notificacao.objects.exists()
    motivos = f" {motivo_reprovacao_x.motivo} \n"
    outros_motivos = 'Esse é o outro motivo de reprovação'
    notificar_prestacao_de_contas_reprovada(prestacao_notifica_pc_reprovada, motivo_reprovacao_x.motivo, outros_motivos, enviar_email=False)
    assert Notificacao.objects.count() == 1
    notificacao = Notificacao.objects.first()

    assert notificacao.tipo == Notificacao.TIPO_NOTIFICACAO_INFORMACAO
    assert notificacao.categoria == Notificacao.CATEGORIA_NOTIFICACAO_REPROVACAO_PC
    assert notificacao.remetente == Notificacao.REMETENTE_NOTIFICACAO_SISTEMA
    assert notificacao.titulo == f"A PC do período {prestacao_notifica_pc_reprovada.periodo.referencia} foi reprovada pela DRE"
    assert notificacao.descricao == f"A prestação de contas referente ao período {prestacao_notifica_pc_reprovada.periodo.referencia} foi reprovada pelos seguintes motivos: {motivos} {outros_motivos}"
    assert notificacao.usuario == usuario_notificavel


def test_nao_deve_notificar_usuarios_sem_permissao(prestacao_notifica_pc_reprovada, motivo_reprovacao_x, usuario_nao_notificavel, associacao_a):
    assert not Notificacao.objects.exists()
    outros_motivos = 'Esse é o outro motivo de aprovação com ressalvas'
    notificar_prestacao_de_contas_reprovada(prestacao_notifica_pc_reprovada, motivo_reprovacao_x.motivo, outros_motivos)
    assert Notificacao.objects.count() == 0


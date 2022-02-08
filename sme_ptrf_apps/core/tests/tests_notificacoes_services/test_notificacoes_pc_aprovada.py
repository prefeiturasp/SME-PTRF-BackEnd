import pytest

from ....core.models import Notificacao
from ....core.services.notificacao_services import notificar_prestacao_de_contas_aprovada

pytestmark = pytest.mark.django_db


def test_deve_notificar_usuarios(prestacao_notifica_pc_aprovada, usuario_notificavel, associacao_a):
    assert not Notificacao.objects.exists()
    notificar_prestacao_de_contas_aprovada(prestacao_notifica_pc_aprovada, enviar_email=False)
    assert Notificacao.objects.count() == 1
    notificacao = Notificacao.objects.first()

    assert notificacao.tipo == Notificacao.TIPO_NOTIFICACAO_INFORMACAO
    assert notificacao.categoria == Notificacao.CATEGORIA_NOTIFICACAO_APROVACAO_PC
    assert notificacao.remetente == Notificacao.REMETENTE_NOTIFICACAO_SISTEMA
    assert notificacao.titulo == f"A PC do período {prestacao_notifica_pc_aprovada.periodo.referencia} foi aprovada pela DRE"
    assert notificacao.descricao == f"A prestação de contas referente ao período {prestacao_notifica_pc_aprovada.periodo.referencia} foi aprovada"
    assert notificacao.usuario == usuario_notificavel


def test_nao_deve_notificar_usuarios_sem_permissao(prestacao_notifica_pc_aprovada, usuario_nao_notificavel, associacao_a):
    assert not Notificacao.objects.exists()
    notificar_prestacao_de_contas_aprovada(prestacao_notifica_pc_aprovada)
    assert Notificacao.objects.count() == 0


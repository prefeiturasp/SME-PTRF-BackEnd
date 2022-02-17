import pytest

import datetime
from ....core.services.notificacao_services.formata_data_dd_mm_yyyy import formata_data_dd_mm_yyyy

from ....core.models import Notificacao
from ....core.services.notificacao_services import notificar_prestacao_de_contas_devolvida_para_acertos

pytestmark = pytest.mark.django_db


def test_deve_notificar_usuarios(prestacao_notifica_pc_devolvida_para_acertos, usuario_notificavel, associacao_a):
    assert not Notificacao.objects.exists()
    data_limite_ue = datetime.date(2020, 6, 17)
    notificar_prestacao_de_contas_devolvida_para_acertos(prestacao_notifica_pc_devolvida_para_acertos, data_limite_ue, enviar_email=False)
    assert Notificacao.objects.count() == 1
    notificacao = Notificacao.objects.first()

    assert notificacao.tipo == Notificacao.TIPO_NOTIFICACAO_ALERTA
    assert notificacao.categoria == Notificacao.CATEGORIA_NOTIFICACAO_DEVOLUCAO_PC
    assert notificacao.remetente == Notificacao.REMETENTE_NOTIFICACAO_DRE
    assert notificacao.titulo == f"Ajustes necessários na PC | Prazo: {formata_data_dd_mm_yyyy(data_limite_ue)}"
    assert notificacao.descricao == f"A DRE solicitou alguns ajustes em sua prestação de contas do período {prestacao_notifica_pc_devolvida_para_acertos.periodo.referencia}. O seu prazo para envio das mudanças é {formata_data_dd_mm_yyyy(data_limite_ue)}"
    assert notificacao.usuario == usuario_notificavel


def test_nao_deve_notificar_usuarios_sem_permissao(prestacao_notifica_pc_devolvida_para_acertos, usuario_nao_notificavel, associacao_a):
    assert not Notificacao.objects.exists()
    data_limite_ue = datetime.date(2020, 6, 17)
    notificar_prestacao_de_contas_devolvida_para_acertos(prestacao_notifica_pc_devolvida_para_acertos, data_limite_ue)
    assert Notificacao.objects.count() == 0


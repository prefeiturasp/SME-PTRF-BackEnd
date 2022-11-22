import pytest

from freezegun import freeze_time

from ....core.models import Notificacao
from ....core.services.notificacao_services import notificar_prazo_para_acerto_apos_vencimento

pytestmark = pytest.mark.django_db


@freeze_time("2022-11-22")
def test_deve_notificar_tecnico_dre(usuario_tecnico_notificavel, associacao_a, consolidado_dre_devolucao_apos_acertos):
    assert not Notificacao.objects.exists()
    notificar_prazo_para_acerto_apos_vencimento(enviar_email=True)
    notificacao = Notificacao.objects.first()
    assert Notificacao.objects.count() == 1
    assert notificacao.tipo == Notificacao.TIPO_NOTIFICACAO_ALERTA
    assert notificacao.categoria == Notificacao.CATEGORIA_NOTIFICACAO_DEVOLUCAO_CONSOLIDADO_APOS_PRAZO_VENCIMENTO
    assert notificacao.remetente == Notificacao.REMETENTE_NOTIFICACAO_SISTEMA
    assert notificacao.titulo == f'Devolução para acertos no relatório consolidado de {consolidado_dre_devolucao_apos_acertos.periodo.referencia}'
    assert notificacao.descricao == f"O prazo para acerto da Publicação {consolidado_dre_devolucao_apos_acertos.referencia} {consolidado_dre_devolucao_apos_acertos.periodo.referencia} expirou. Favor verificar os acertos solicitados e regularizar a situação."
    assert notificacao.usuario == usuario_tecnico_notificavel


@freeze_time("2022-11-22")
def test_nao_deve_notificar_pois_nao_tem_acerto_fora_prazo(periodo_2021_4_pc_2021_06_18_a_2021_06_30, usuario_notificavel, associacao_a, consolidado_dre_devolucao_apos_acertos_dentro_do_prazo):
    assert not Notificacao.objects.exists()
    notificar_prazo_para_acerto_apos_vencimento(enviar_email=True)
    assert Notificacao.objects.count() == 0


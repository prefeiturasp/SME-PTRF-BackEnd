import pytest

from freezegun import freeze_time

from .....core.models import Notificacao
from .....dre.services.notificacao_service.notificacao_prazo_para_acerto_consolidado_devolucao import NotificacaoConsolidadoPrazoAcertoVencimento


pytestmark = pytest.mark.django_db


@freeze_time("2022-11-22")
def test_deve_notificar_tecnico_dre_pois_foi_devolvida(usuario_tecnico_notificavel, associacao_a, consolidado_dre_devolucao_apos_acertos_dentro_do_prazo):
    assert not Notificacao.objects.exists()
    NotificacaoConsolidadoPrazoAcertoVencimento(
        enviar_email=True
    ).notificar_prazo_para_acerto_antes_vencimento()
    notificacao = Notificacao.objects.first()
    assert Notificacao.objects.count() == 1
    assert notificacao.tipo == Notificacao.TIPO_NOTIFICACAO_ALERTA
    assert notificacao.categoria == Notificacao.CATEGORIA_NOTIFICACAO_DEVOLUCAO_CONSOLIDADO
    assert notificacao.remetente == Notificacao.REMETENTE_NOTIFICACAO_SISTEMA
    assert notificacao.titulo == f'Devolução para acertos no relatório consolidado de {consolidado_dre_devolucao_apos_acertos_dentro_do_prazo.periodo.referencia}'
    assert notificacao.descricao == f"A SME solicitou acertos relativos à Publicação {consolidado_dre_devolucao_apos_acertos_dentro_do_prazo.referencia} {consolidado_dre_devolucao_apos_acertos_dentro_do_prazo.periodo.referencia}. O seu prazo para envio dos acertos é {consolidado_dre_devolucao_apos_acertos_dentro_do_prazo.analise_atual.data_limite.strftime('%d/%m/%Y')}"
    assert notificacao.usuario == usuario_tecnico_notificavel


@freeze_time("2022-11-22")
def test_nao_deve_notificar_pois_nao_tem_acerto_fora_prazo(periodo_2021_4_pc_2021_06_18_a_2021_06_30, usuario_notificavel, associacao_a, consolidado_dre_devolucao_apos_acertos_em_analise):
    assert not Notificacao.objects.exists()
    NotificacaoConsolidadoPrazoAcertoVencimento(
        enviar_email=True
    ).notificar_prazo_para_acerto_antes_vencimento()
    assert Notificacao.objects.count() == 0

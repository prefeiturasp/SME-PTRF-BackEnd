import logging
from datetime import date
from sme_ptrf_apps.core.models import Notificacao
from sme_ptrf_apps.dre.models import ConsolidadoDRE
from .formata_data_dd_mm_yyyy import formata_data_dd_mm_yyyy
from django.contrib.auth import get_user_model


logger = logging.getLogger(__name__)


def notificar_prazo_para_acerto_antes_vencimento(enviar_email=True):
    logger.info(f'Notificar prazo para acerto antes vencimento service')

    data_de_hoje = date.today()
    consolidados_devolvida_para_acerto_prazo = ConsolidadoDRE.objects.filter(
        status_sme='DEVOLVIDO'
    )

    for consolidado in consolidados_devolvida_para_acerto_prazo:
        for tecnico in consolidado.dre.tecnicos_da_dre.all():
            User = get_user_model()
            user = User.objects.filter(username=tecnico.rf).first()
            if user:
                Notificacao.notificar(
                    tipo=Notificacao.TIPO_NOTIFICACAO_ALERTA,
                    categoria=Notificacao.CATEGORIA_NOTIFICACAO_DEVOLUCAO_CONSOLIDADO,
                    remetente=Notificacao.REMETENTE_NOTIFICACAO_SISTEMA,
                    titulo=f"Devolução para acertos no relatório consolidado de {consolidado.periodo.referencia}",
                    descricao=f"A SME solicitou acertos relativos à Publicação {consolidado.referencia} {consolidado.periodo.referencia}. O seu prazo para envio dos acertos é {formata_data_dd_mm_yyyy(consolidado.analise_atual.data_limite)}",
                    usuario=user,
                    renotificar=False,
                    enviar_email=enviar_email,
                )

    logger.info(f'Notificação para devolução do consolidado realizado com sucesso.')

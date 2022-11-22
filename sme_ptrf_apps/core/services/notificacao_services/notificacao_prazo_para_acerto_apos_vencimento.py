import logging
from datetime import date
from sme_ptrf_apps.core.models import Periodo, Notificacao, Associacao, PrestacaoConta
from sme_ptrf_apps.dre.models import ConsolidadoDRE
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


def notificar_prazo_para_acerto_apos_vencimento(enviar_email=True):
    logger.info(f'Notificar prazo para acerto apos vencimento service')

    data_de_hoje = date.today()
    consolidados_devolvida_para_acerto_prazo = ConsolidadoDRE.objects.filter(
        status_sme='DEVOLVIDO',
        analise_atual__data_limite__lt=data_de_hoje
    )

    for consolidado in consolidados_devolvida_para_acerto_prazo:
        for tecnico in consolidado.dre.tecnicos_da_dre.all():
            User = get_user_model()
            user = User.objects.filter(username=tecnico.rf).first()
            if user:
                Notificacao.notificar(
                    tipo=Notificacao.TIPO_NOTIFICACAO_ALERTA,
                    categoria=Notificacao.CATEGORIA_NOTIFICACAO_DEVOLUCAO_CONSOLIDADO_APOS_PRAZO_VENCIMENTO,
                    remetente=Notificacao.REMETENTE_NOTIFICACAO_SISTEMA,
                    titulo=f"Devolução para acertos no relatório consolidado de {consolidado.periodo.referencia}",
                    descricao=f"O prazo para acerto da Publicação {consolidado.referencia} {consolidado.periodo.referencia} expirou. Favor verificar os acertos solicitados e regularizar a situação.",
                    usuario=user,
                    renotificar=False,
                    enviar_email=enviar_email,
                )

    logger.info(f'Notificação para vencimento do prazo realizado com sucesso.')

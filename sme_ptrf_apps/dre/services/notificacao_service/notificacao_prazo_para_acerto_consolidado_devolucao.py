import logging
from datetime import date
from ....core.services.notificacao_services import formata_data_dd_mm_yyyy
from sme_ptrf_apps.core.models import Periodo, Notificacao, Associacao, PrestacaoConta
from sme_ptrf_apps.dre.models import ConsolidadoDRE
from django.contrib.auth import get_user_model


logger = logging.getLogger(__name__)


class NotificacaoConsolidadoPrazoAcertoVencimento():

    def __init__(self, enviar_email=True):
        self.enviar_email = enviar_email

    def notificar_prazo_para_acerto_apos_vencimento(self):
        logger.info(f'Notificar prazo para acerto apos vencimento service')

        data_de_hoje = date.today()
        consolidados_devolvida_para_acerto_prazo = ConsolidadoDRE.objects.filter(
            status_sme='DEVOLVIDO',
            analise_atual__data_limite__lt=data_de_hoje
        )

        User = get_user_model()
        for consolidado in consolidados_devolvida_para_acerto_prazo:
            for tecnico in consolidado.dre.tecnicos_da_dre.all():
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
                        enviar_email=self.enviar_email,
                    )

        logger.info(f'Notificação para vencimento do prazo realizado com sucesso.')

    def notificar_prazo_para_acerto_antes_vencimento(self):
        logger.info(f'Notificar prazo para acerto antes vencimento service')

        consolidados_devolvida_para_acerto_prazo = ConsolidadoDRE.objects.filter(
            status_sme='DEVOLVIDO',
        )

        User = get_user_model()
        for consolidado in consolidados_devolvida_para_acerto_prazo:
            for tecnico in consolidado.dre.tecnicos_da_dre.all():
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
                    enviar_email=self.enviar_email,
                )

        logger.info(f'Notificação para vencimento do prazo realizado com sucesso.')

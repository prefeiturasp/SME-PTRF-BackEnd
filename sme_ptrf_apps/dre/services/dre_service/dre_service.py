import logging

from sme_ptrf_apps.core.models import Unidade
from sme_ptrf_apps.dre.models import ParametrosDre, MembroComissao

logger = logging.getLogger(__name__)


class DreServiceException(Exception):
    pass


class DreService:
    def __init__(self, dre: Unidade):
        if not isinstance(dre, Unidade) or dre.tipo_unidade != 'DRE':
            raise DreServiceException('O serviço precisa ser iniciado informando uma DRE válida.')

        self.dre = dre

    def get_comissao_exame_contas(self):
        comissao_exame_contas = ParametrosDre.get().comissao_exame_contas
        membros_comissao = MembroComissao.objects.filter(
            dre=self.dre,
            comissoes=comissao_exame_contas
        )
        return membros_comissao

    def notificar_devolucao_consolidado(self, consolidado_dre, enviar_email=True):
        from django.contrib.auth import get_user_model
        from sme_ptrf_apps.core.models import Notificacao

        logger.info(
            f'Notificando a devolução para acertos do consolidado da DRE  {consolidado_dre.dre.nome} ref {consolidado_dre.periodo.referencia}.')

        comissao_contas = self.get_comissao_exame_contas()

        user_model = get_user_model()
        for membro in comissao_contas:
            if not user_model.objects.filter(username=membro.rf).exists():
                continue

            usuario = user_model.objects.filter(username=membro.rf).first()

            logger.info(
                f"Criando notificação para o usuário: {usuario}.")

            Notificacao.notificar(
                tipo=Notificacao.TIPO_NOTIFICACAO_AVISO,
                categoria=Notificacao.CATEGORIA_NOTIFICACAO_DEVOLUCAO_CONSOLIDADO,
                remetente=Notificacao.REMETENTE_NOTIFICACAO_SME,
                titulo=f"Devolução  para acertos do relatório consolidado de {consolidado_dre.periodo.referencia}",
                descricao=f"O relatório de publicação {consolidado_dre.referencia} referente ao período {consolidado_dre.periodo.referencia} foi analisado pela SME e devolvido para acertos. Confira o relatório no SEI e realize os acertos solicitados.",
                usuario=usuario,
                renotificar=True,
                enviar_email=enviar_email,
                unidade=consolidado_dre.dre,
                prestacao_conta=None,
            )

        logger.info(
            f'Concluída notificação de devolução para acertos do consolidado da DRE  {consolidado_dre.dre.nome} ref {consolidado_dre.periodo.referencia}.')

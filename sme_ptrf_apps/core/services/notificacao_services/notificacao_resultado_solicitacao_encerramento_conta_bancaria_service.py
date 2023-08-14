import logging
from sme_ptrf_apps.core.models import Notificacao, SolicitacaoEncerramentoContaAssociacao
from sme_ptrf_apps.users.services.permissions_service import get_users_by_permission
from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)


def notificar_resultado_solicitacao_encerramento_conta_bancaria(conta_associacao, enviar_email=False, resultado=None):
    associacao = conta_associacao.associacao

    logger.info(f'Iniciando serviço de notificação de resultado de '
                f'solicitação de encerramento conta bancaria para a Associação: {associacao}.')

    users = get_users_by_permission('recebe_notificacao_resultado_encerramento_conta')
    users = users.filter(visoes__nome="UE")
    users = users.filter(unidades__codigo_eol=associacao.unidade.codigo_eol)

    if resultado:
        for usuario in users:
            logging.info(f"Gerando notificação de resultado de solicitação de encerramento "
                         f"de conta bancária para o usuário: {usuario}")

            titulo = ""
            descricao = ""

            if resultado == SolicitacaoEncerramentoContaAssociacao.STATUS_APROVADA:
                titulo = "Aprovação de solicitação de encerramento de conta bancária"
                descricao = f"A {associacao.unidade.nome_dre} aprovou a sua solicitação de encerramento " \
                            f"de sua conta bancária {conta_associacao.tipo_conta.nome}. Sua conta já está encerrada."

            elif resultado == SolicitacaoEncerramentoContaAssociacao.STATUS_REJEITADA:
                titulo = "Rejeição de solicitação de encerramento de conta bancária"
                descricao = f"A {associacao.unidade.nome_dre} rejeitou a sua solicitação de encerramento " \
                            f"de sua conta bancária {conta_associacao.tipo_conta.nome}. Sua conta continua ativa."

            Notificacao.notificar(
                tipo=Notificacao.TIPO_NOTIFICACAO_AVISO,
                categoria=Notificacao.CATEGORIA_NOTIFICACAO_ENCERRAMENTO_CONTA_BANCARIA,
                remetente=Notificacao.REMETENTE_NOTIFICACAO_DRE,
                titulo=titulo,
                descricao=descricao,
                usuario=usuario,
                renotificar=True,
                enviar_email=enviar_email
            )

    logger.info(f'Finalizando serviço de notificação de aprovação de solicitação de encerramento conta bancaria.')

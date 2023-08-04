import logging
from sme_ptrf_apps.core.models import Notificacao
from sme_ptrf_apps.users.services.permissions_service import get_users_by_permission
from sme_ptrf_apps.dre.models import MembroComissao
from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)


def notificar_solicitacao_encerramento_conta_bancaria(conta_associacao, enviar_email=False):
    associacao = conta_associacao.associacao

    logger.info(f'Iniciando serviço de notificação de solicitação de encerramento conta bancaria para a Associação: {associacao}.')

    users = get_users_by_permission('recebe_notificacao_encerramento_conta')
    users = users.filter(visoes__nome="DRE")

    for usuario in users:
        membro_comissao = MembroComissao.objects.filter(rf=usuario.username).filter(dre=associacao.unidade.dre).first()

        if not membro_comissao:
            logging.info(f"O usuario {usuario} não é membro de nenhuma comissão da DRE {associacao.unidade.dre}")
            continue

        if not membro_comissao.pertence_a_comissao_exame_contas:
            logging.info(f"O usuario {usuario} não é membro da comissão de exame de contas")
            continue

        logging.info(f"Gerando notificação de solicitação de encerramento de conta bancária para o usuário: {usuario}")

        descricao = f"A Associação da {associacao.unidade.nome_com_tipo} solicitou o encerramento da conta bancária " \
                    f"{conta_associacao.tipo_conta.nome}. " \
                    f"Acesse a página da Associação na Consulta de Associações para validar."

        Notificacao.notificar(
            tipo=Notificacao.TIPO_NOTIFICACAO_AVISO,
            categoria=Notificacao.CATEGORIA_NOTIFICACAO_ENCERRAMENTO_CONTA_BANCARIA,
            remetente=Notificacao.REMETENTE_NOTIFICACAO_ASSOCIACAO,
            titulo=f"Solicitação de encerramento de conta bancária",
            descricao=descricao,
            usuario=usuario,
            renotificar=True,
            enviar_email=enviar_email
        )

    logger.info(f'Finalizando serviço de notificação de solicitação de encerramento conta bancaria.')


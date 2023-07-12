import logging
from sme_ptrf_apps.core.models import Notificacao, Parametros, Associacao
from sme_ptrf_apps.users.services.permissions_service import get_users_by_permission
from sme_ptrf_apps.core.services.painel_resumo_recursos_service import PainelResumoRecursosService

from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)


def notificar_encerramento_conta_bancaria(enviar_email=False):
    logger.info(f'Iniciando serviço de notificação de encerramento conta bancaria.')

    numero_periodos_consecutivos = Parametros.get().numero_periodos_consecutivos

    associacoes = Associacao.objects.all().exclude(cnpj__exact='').order_by('unidade__codigo_eol')
    users = get_users_by_permission('recebe_notificacao_automatica_inativacao_conta')
    users = users.filter(visoes__nome="UE")

    if numero_periodos_consecutivos > 0:
        for associacao in associacoes:
            periodos_da_associacao = list(associacao.periodos_ate_agora_fora_implantacao())

            for conta_associacao in associacao.contas.all():

                if not conta_associacao.tipo_conta.permite_inativacao:
                    # O tipo de conta não permite inativação
                    continue

                if numero_periodos_consecutivos > len(periodos_da_associacao):
                    # O número de periodos consecutivos é maior que o numero de periodos dessa associacao
                    continue

                periodos_consecutivos = periodos_da_associacao[0:numero_periodos_consecutivos]
                periodos_com_saldo_zerado = []

                for periodo in periodos_consecutivos:
                    painel = PainelResumoRecursosService.painel_resumo_recursos(
                        associacao,
                        periodo,
                        conta_associacao
                    )

                    info_conta = painel.info_conta
                    if info_conta.saldo_atual_total == 0:
                        periodos_com_saldo_zerado.append(periodo)

                if periodos_consecutivos == periodos_com_saldo_zerado:
                    """
                        Se as listas forem iguais, significa que
                        o numero de periodos consecutivos com conta zerada,
                        é igual ao numero configurado em parametros (Parametros.get().numero_periodos_consecutivos)
                    """

                    usuarios = users.filter(unidades__codigo_eol=associacao.unidade.codigo_eol)

                    for usuario in usuarios:
                        logging.info(f"Gerando notificação de encerramento de conta bancária para o usuário: {usuario}")

                        Notificacao.notificar(
                            tipo=Notificacao.TIPO_NOTIFICACAO_AVISO,
                            categoria=Notificacao.CATEGORIA_NOTIFICACAO_ENCERRAMENTO_CONTA_BANCARIA,
                            remetente=Notificacao.REMETENTE_NOTIFICACAO_SISTEMA,
                            titulo=f"Encerramento de Conta Bancária",
                            descricao=f"O saldo da conta bancária {conta_associacao.tipo_conta.nome} está zerada, caso deseje, o encerramento da conta pode ser solicitada. Acesse a página Dados das contas para validar.",
                            usuario=usuario,
                            renotificar=True,
                            enviar_email=enviar_email
                        )

    logger.info(f'Finalizando serviço de notificação de encerramento conta bancaria.')

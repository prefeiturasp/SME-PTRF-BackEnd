import logging
from datetime import date
from sme_ptrf_apps.core.models import Periodo, Notificacao, Associacao, PrestacaoConta
from sme_ptrf_apps.users.services.permissions_service import get_users_by_permission

logger = logging.getLogger(__name__)


def notificar_pendencia_envio_prestacao_de_contas(enviar_email=True):
    logger.info(f'Notificar pendência envio prestação de contas service')

    data_de_hoje = date.today()

    periodo = Periodo.objects.filter(
        data_fim_realizacao_despesas__lt=data_de_hoje,
        data_fim_prestacao_contas__lt=data_de_hoje,
        notificacao_pendencia_envio_pc_realizada=False
    ).first()

    associacoes = Associacao.objects.all().exclude(cnpj__exact='').order_by('unidade__codigo_eol')

    users = get_users_by_permission('recebe_notificacao_pendencia_envio_prestacao_de_contas')

    users = users.filter(visoes__nome="UE")

    if periodo:

        for associacao in associacoes:

            if associacao.periodo_inicial and periodo.referencia <= associacao.periodo_inicial.referencia:
                # A Associação está isenta de PC até o seu período inicial (inclusive)
                continue

            prestacao_conta = PrestacaoConta.objects.filter(associacao=associacao, periodo=periodo).first()

            # Devem entrar apenas Prestações de contas não apresentadas ou não recebidas
            if prestacao_conta and prestacao_conta.status != PrestacaoConta.STATUS_NAO_APRESENTADA:
                continue

            usuarios = users.filter(unidades__codigo_eol=associacao.unidade.codigo_eol)

            if usuarios:
                for usuario in usuarios:
                    logger.info(f"Gerando notificação de pendência de envio de PC para o usuario: {usuario} | Período: {periodo.referencia}")

                    Notificacao.notificar(
                        tipo=Notificacao.TIPO_NOTIFICACAO_ALERTA,
                        categoria=Notificacao.CATEGORIA_NOTIFICACAO_ELABORACAO_PC,
                        remetente=Notificacao.REMETENTE_NOTIFICACAO_SISTEMA,
                        titulo=f"Pendência de envio de PC {periodo.referencia}",
                        descricao=f"Terminou o período de prestações de contas para a associação {associacao.unidade.codigo_eol} - {associacao.unidade.nome} e você ainda não enviou sua PC.",
                        usuario=usuario,
                        renotificar=True,
                        enviar_email=enviar_email
                    )

                periodo.notificacao_pendencia_envio_prestacao_de_contas_realizada()

    else:
        logger.info(f"Não foram encontrados períodos a serem notificados sobre pendência de envio de prestação de contas")




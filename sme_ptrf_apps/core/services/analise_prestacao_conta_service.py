import logging
import uuid
import copy
from sme_ptrf_apps.core.services.dados_relatorio_acertos_service import (gerar_dados_relatorio_acertos)
from sme_ptrf_apps.core.services.relatorio_acertos_pdf_service import (gerar_arquivo_relatorio_acertos_pdf)

logger = logging.getLogger(__name__)


def copia_ajustes_entre_analises(analise_origem, analise_destino):
    def copia_analise_lancamento(analise_lancamento_origem):
        nova_analise = copy.deepcopy(analise_lancamento_origem)
        nova_analise.pk = None
        nova_analise.uuid = uuid.uuid4()
        nova_analise.analise_prestacao_conta = analise_destino
        nova_analise.save()
        return nova_analise

    def copia_solicitacao_acerto_lancamento(solicitacao_acerto_lancamento_origem, para):
        nova_solicitacao = copy.deepcopy(solicitacao_acerto_lancamento_origem)
        nova_solicitacao.pk = None
        nova_solicitacao.uuid = uuid.uuid4()
        nova_solicitacao.analise_lancamento = para
        nova_solicitacao.save()
        return nova_solicitacao

    def copia_analises_de_lancamento():
        for analise_lancamento in analise_origem.analises_de_lancamentos.all():
            nova_analise_lancamento = copia_analise_lancamento(analise_lancamento)
            for solicitacao_acerto_lancamento in analise_lancamento.solicitacoes_de_ajuste_da_analise.all():
                copia_solicitacao_acerto_lancamento(solicitacao_acerto_lancamento, para=nova_analise_lancamento)

    def copia_analise_documento(analise_documento_origem):
        nova_analise = copy.deepcopy(analise_documento_origem)
        nova_analise.pk = None
        nova_analise.uuid = uuid.uuid4()
        nova_analise.analise_prestacao_conta = analise_destino
        nova_analise.save()
        return nova_analise

    def copia_solicitacao_acerto_documento(solicitacao_acerto_documento_origem, para):
        nova_solicitacao = copy.deepcopy(solicitacao_acerto_documento_origem)
        nova_solicitacao.pk = None
        nova_solicitacao.uuid = uuid.uuid4()
        nova_solicitacao.analise_documento = para
        nova_solicitacao.save()
        return nova_solicitacao

    def copia_analises_de_documento():
        for analise_documento in analise_origem.analises_de_documento.all():
            nova_analise_documento = copia_analise_documento(analise_documento)
            for solicitacao_acerto_documento in analise_documento.solicitacoes_de_ajuste_da_analise.all():
                copia_solicitacao_acerto_documento(solicitacao_acerto_documento, para=nova_analise_documento)

    copia_analises_de_lancamento()
    copia_analises_de_documento()


def _criar_previa_relatorio_acertos(analise_prestacao_conta, conta_associacao_cheque, conta_associacao_cartao, usuario=""):
    logger.info(f'Gerando prévias do relatorio de acertos.')

    logger.info(f'ESTOU DENTRO DO CRIAR PREVIA {analise_prestacao_conta.status}, {analise_prestacao_conta}')

    _gerar_arquivos_relatorio_acertos(
        analise_prestacao_conta=analise_prestacao_conta,
        conta_associacao_cheque=conta_associacao_cheque,
        conta_associacao_cartao=conta_associacao_cartao,
        previa=True,
        usuario=usuario
    )


def _gerar_arquivos_relatorio_acertos(analise_prestacao_conta, conta_associacao_cheque, conta_associacao_cartao, previa, usuario=""):
    logger.info(f'ESTOU DENTRO DO GERAR ARQUIVOS {analise_prestacao_conta.status}, {analise_prestacao_conta}')

    analise_prestacao_conta.inicia_geracao_arquivo_pdf(previa)

    dados_relatorio_acertos = gerar_dados_relatorio_acertos(
        analise_prestacao_conta=analise_prestacao_conta,
        conta_associacao_cheque=conta_associacao_cheque,
        conta_associacao_cartao=conta_associacao_cartao,
        previa=previa,
        usuario=usuario
    )

    logger.info(f'ESTOU NO FIM DE GERAR ARQUIVOS {analise_prestacao_conta.status}, {analise_prestacao_conta}')

    gerar_arquivo_relatorio_acertos_pdf(dados_relatorio_acertos, analise_prestacao_conta)

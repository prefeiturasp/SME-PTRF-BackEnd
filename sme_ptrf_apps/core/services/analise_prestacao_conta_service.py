import logging
import uuid
import copy
from sme_ptrf_apps.core.services.dados_relatorio_acertos_service import (gerar_dados_relatorio_acertos)
from sme_ptrf_apps.core.services.relatorio_acertos_pdf_service import (gerar_arquivo_relatorio_acertos_pdf)
from sme_ptrf_apps.core.services.dados_relatorio_apos_acertos_service import DadosRelatorioAposAcertosService
from sme_ptrf_apps.core.services.relatorio_apos_acertos_pdf_service import ArquivoRelatorioAposAcertosService

from sme_ptrf_apps.core.models import AnalisePrestacaoConta, AnaliseContaPrestacaoConta

logger = logging.getLogger(__name__)


def copia_ajustes_entre_analises(analise_origem, analise_destino):
    def copia_solicitacao_devolucao_ao_tesouro(da_solicitacao_origem, para_solicitacao_destino):
        nova_solicitacao_devolucao = copy.deepcopy(da_solicitacao_origem.solicitacao_devolucao_ao_tesouro)
        nova_solicitacao_devolucao.pk = None
        nova_solicitacao_devolucao.uuid = uuid.uuid4()
        nova_solicitacao_devolucao.solicitacao_acerto_lancamento = para_solicitacao_destino
        nova_solicitacao_devolucao.save()
        return nova_solicitacao_devolucao

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
        nova_solicitacao.copiado = True
        nova_solicitacao.save()
        if hasattr(solicitacao_acerto_lancamento_origem, 'solicitacao_devolucao_ao_tesouro'):
            copia_solicitacao_devolucao_ao_tesouro(
                da_solicitacao_origem=solicitacao_acerto_lancamento_origem,
                para_solicitacao_destino=nova_solicitacao
            )
        return nova_solicitacao

    def copia_analises_de_lancamento():
        for analise_lancamento in analise_origem.analises_de_lancamentos.all():
            nova_analise_lancamento = copia_analise_lancamento(analise_lancamento)
            for solicitacao_acerto_lancamento in analise_lancamento.solicitacoes_de_ajuste_da_analise.all():
                nova_solicitacao_acerto_lancamento = copia_solicitacao_acerto_lancamento(
                    solicitacao_acerto_lancamento,
                    para=nova_analise_lancamento
                )

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
        nova_solicitacao.copiado = True
        nova_solicitacao.save()
        return nova_solicitacao

    def copia_analises_de_documento():
        for analise_documento in analise_origem.analises_de_documento.all():
            nova_analise_documento = copia_analise_documento(analise_documento)
            for solicitacao_acerto_documento in analise_documento.solicitacoes_de_ajuste_da_analise.all():
                copia_solicitacao_acerto_documento(solicitacao_acerto_documento, para=nova_analise_documento)

    copia_analises_de_lancamento()
    copia_analises_de_documento()


def _criar_previa_relatorio_acertos(analise_prestacao_conta, usuario=""):
    logger.info(f'Gerando prévias do relatorio de acertos.')

    _gerar_arquivos_relatorio_acertos(
        analise_prestacao_conta=analise_prestacao_conta,
        previa=True,
        usuario=usuario
    )


def _criar_documento_final_relatorio_acertos(analise_prestacao_uuid, usuario=""):
    analise_prestacao_conta = AnalisePrestacaoConta.objects.get(uuid=analise_prestacao_uuid)
    logger.info(f'Gerando documento final do relatorio de acertos.')

    analise_prestacao_conta.apaga_arquivo_pdf()

    _gerar_arquivos_relatorio_acertos(
        analise_prestacao_conta=analise_prestacao_conta,
        previa=False,
        usuario=usuario
    )


def _gerar_arquivos_relatorio_acertos(analise_prestacao_conta, previa, usuario=""):
    analise_prestacao_conta.inicia_geracao_arquivo_pdf(previa)

    dados_relatorio_acertos = gerar_dados_relatorio_acertos(
        analise_prestacao_conta=analise_prestacao_conta,
        previa=previa,
        usuario=usuario
    )

    gerar_arquivo_relatorio_acertos_pdf(dados_relatorio_acertos, analise_prestacao_conta)


def criar_previa_relatorio_apos_acertos(analise_prestacao_conta, usuario=""):
    logger.info(f'Gerando prévias do relatorio após acertos.')

    _gerar_arquivos_relatorio_apos_acertos(
        analise_prestacao_conta=analise_prestacao_conta,
        previa=True,
        usuario=usuario
    )


def criar_relatorio_apos_acertos_final(analise_prestacao_conta, usuario=""):
    logger.info(f'Gerando versão final do relatorio após acertos.')

    _gerar_arquivos_relatorio_apos_acertos(
        analise_prestacao_conta=analise_prestacao_conta,
        previa=False,
        usuario=usuario
    )


def _gerar_arquivos_relatorio_apos_acertos(analise_prestacao_conta, previa, usuario=""):
    analise_prestacao_conta.inicia_geracao_arquivo_pdf_relatorio_apos_acertos(previa)

    dados_relatorio_apos_acertos = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta,
        previa=previa,
        usuario=usuario
    )

    ArquivoRelatorioAposAcertosService.gerar_relatorio(analise_prestacao_conta, dados_relatorio_apos_acertos)


def get_ajustes_extratos_bancarios(analise_prestacao, conta_associacao=None):
    from sme_ptrf_apps.core.api.serializers.analise_conta_prestacao_conta_serializer import AnaliseContaPrestacaoContaRetrieveSerializer

    qs = analise_prestacao.analises_de_extratos

    if conta_associacao:
        qs = qs.filter(conta_associacao=conta_associacao).first()

    return AnaliseContaPrestacaoContaRetrieveSerializer(qs, many=not conta_associacao).data if qs else None

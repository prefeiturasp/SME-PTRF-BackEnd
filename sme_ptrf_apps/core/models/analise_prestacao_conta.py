import logging

from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from datetime import datetime
from django.db.models import Q


logger = logging.getLogger(__name__)


class AnalisePrestacaoConta(ModeloBase):
    history = AuditlogHistoryField()

    # Status Choice
    STATUS_EM_ANALISE = 'EM_ANALISE'
    STATUS_DEVOLVIDA = 'DEVOLVIDA'
    STATUS_APROVADA = 'APROVADA'
    STATUS_APROVADA_RESSALVA = 'APROVADA_RESSALVA'
    STATUS_REPROVADA = 'REPROVADA'

    STATUS_NOMES = {
        STATUS_EM_ANALISE: 'Em análise',
        STATUS_DEVOLVIDA: 'Devolvida para acertos',
        STATUS_APROVADA: 'Aprovada',
        STATUS_APROVADA_RESSALVA: 'Aprovada com ressalvas',
        STATUS_REPROVADA: 'Reprovada',
    }

    STATUS_CHOICES = (
        (STATUS_EM_ANALISE, STATUS_NOMES[STATUS_EM_ANALISE]),
        (STATUS_DEVOLVIDA, STATUS_NOMES[STATUS_DEVOLVIDA]),
        (STATUS_APROVADA, STATUS_NOMES[STATUS_APROVADA]),
        (STATUS_APROVADA_RESSALVA, STATUS_NOMES[STATUS_APROVADA_RESSALVA]),
        (STATUS_REPROVADA, STATUS_NOMES[STATUS_REPROVADA]),
    )

    # Versao Choice
    VERSAO_NAO_GERADO = '-'
    VERSAO_FINAL = 'FINAL'
    VERSAO_RASCUNHO = 'RASCUNHO'

    VERSAO_NOMES = {
        VERSAO_NAO_GERADO: '-',
        VERSAO_FINAL: 'final',
        VERSAO_RASCUNHO: 'rascunho',
    }

    VERSAO_CHOICES = (
        (VERSAO_NAO_GERADO, VERSAO_NOMES[VERSAO_NAO_GERADO]),
        (VERSAO_FINAL, VERSAO_NOMES[VERSAO_FINAL]),
        (VERSAO_RASCUNHO, VERSAO_NOMES[VERSAO_RASCUNHO]),
    )

    # Status Choice
    STATUS_NAO_GERADO = 'NAO_GERADO'
    STATUS_EM_PROCESSAMENTO = 'EM_PROCESSAMENTO'
    STATUS_CONCLUIDO = 'CONCLUIDO'

    STATUS_NOMES_CHOICES = {
        STATUS_NAO_GERADO: 'Não gerado',
        STATUS_EM_PROCESSAMENTO: 'Em processamento',
        STATUS_CONCLUIDO: 'Geração concluída',
    }

    STATUS_CHOICES_VERSAO = (
        (STATUS_NAO_GERADO, STATUS_NOMES_CHOICES[STATUS_NAO_GERADO]),
        (STATUS_EM_PROCESSAMENTO, STATUS_NOMES_CHOICES[STATUS_EM_PROCESSAMENTO]),
        (STATUS_CONCLUIDO, STATUS_NOMES_CHOICES[STATUS_CONCLUIDO]),
    )

    prestacao_conta = models.ForeignKey('PrestacaoConta', on_delete=models.CASCADE,
                                        related_name='analises_da_prestacao')

    status = models.CharField(
        'status',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_EM_ANALISE
    )

    devolucao_prestacao_conta = models.ForeignKey(
        'DevolucaoPrestacaoConta',
        on_delete=models.SET_NULL,
        related_name='analises_da_devolucao',
        blank=True, null=True,
    )

    # Relatorio de solicitação de acertos
    arquivo_pdf = models.FileField(blank=True, null=True, verbose_name='Relatório em PDF de solicitação de acertos')

    status_versao = models.CharField(
        'Status da geração do documento de solicitação de acertos',
        max_length=20,
        choices=STATUS_CHOICES_VERSAO,
        default=STATUS_NAO_GERADO
    )

    versao = models.CharField(
        'Versão do documento de solicitação de acertos',
        max_length=20,
        choices=VERSAO_CHOICES,
        default=VERSAO_NAO_GERADO
    )

    arquivo_pdf_criado_em = models.DateTimeField("Arquivo pdf de solicitação de acertos gerado em", null=True)

    # Relatorio de apresentação após acertos
    arquivo_pdf_apresentacao_apos_acertos = models.FileField(
        blank=True, null=True, verbose_name='Relatório em PDF de apresentação após acertos')

    status_versao_apresentacao_apos_acertos = models.CharField(
        'Status da geração do documento de apresentação após acertos',
        max_length=20,
        choices=STATUS_CHOICES_VERSAO,
        default=STATUS_NAO_GERADO
    )

    versao_pdf_apresentacao_apos_acertos = models.CharField(
        'Versão do documento de apresentação após acertos',
        max_length=20,
        choices=VERSAO_CHOICES,
        default=VERSAO_NAO_GERADO
    )

    arquivo_pdf_apresentacao_apos_acertos_criado_em = models.DateTimeField(
        "Arquivo pdf apresentação após acertos gerado em", null=True)

    @property
    def requer_alteracao_em_lancamentos(self):
        return self.verifica_se_requer_alteracao_em_lancamentos()

    @property
    def requer_informacao_devolucao_ao_tesouro(self):
        from sme_ptrf_apps.core.models import TipoAcertoLancamento

        return self.analises_de_lancamentos.filter(
            solicitacoes_de_ajuste_da_analise__tipo_acerto__categoria=TipoAcertoLancamento.CATEGORIA_DEVOLUCAO
        ).exists()

    @property
    def tem_acertos_pendentes(self):
        from sme_ptrf_apps.core.models import AnaliseLancamentoPrestacaoConta, AnaliseDocumentoPrestacaoConta

        tem_analises_de_lancamentos_pendentes = self.analises_de_lancamentos.filter(
            resultado=AnaliseLancamentoPrestacaoConta.RESULTADO_AJUSTE).filter(
            Q(status_realizacao=AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE) |
            Q(status_realizacao=AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_REALIZADO_PARCIALMENTE)
        ).exists()

        tem_analises_de_documentos_pendentes = self.analises_de_documento.filter(
            resultado=AnaliseDocumentoPrestacaoConta.RESULTADO_AJUSTE).filter(
            Q(status_realizacao=AnaliseDocumentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE) |
            Q(status_realizacao=AnaliseDocumentoPrestacaoConta.STATUS_REALIZACAO_REALIZADO_PARCIALMENTE)
        ).exists()

        return tem_analises_de_lancamentos_pendentes or tem_analises_de_documentos_pendentes

    def tem_acertos_extratos_bancarios(self, conta_associacao):
        acerto_extrato_bancario = self.analises_de_extratos.filter(conta_associacao=conta_associacao).exists()

        return acerto_extrato_bancario

    def __str__(self):
        return f"{self.prestacao_conta.periodo} - Análise #{self.pk}"

    def get_status(self):
        if not self.arquivo_pdf:
            if self.status_versao == self.STATUS_NAO_GERADO:
                if not self.devolucao_prestacao_conta and self.VERSAO_NOMES[self.versao] == '-':
                    return "Nenhuma prévia gerada."
                elif self.devolucao_prestacao_conta and self.VERSAO_NOMES[self.versao] == '-':
                    return "Nenhum documento gerado."
            elif self.status_versao == self.STATUS_EM_PROCESSAMENTO:
                return f"Relatório sendo gerado..."
            elif self.status_versao == self.STATUS_CONCLUIDO:
                if self.VERSAO_NOMES[self.versao] == 'rascunho':
                    return "Nenhuma prévia gerada."
                else:
                    return "Nenhum documento gerado."
        elif self.arquivo_pdf:
            if self.status_versao == self.STATUS_CONCLUIDO:
                if self.VERSAO_NOMES[self.versao] == 'rascunho':
                    return f"Prévia gerada em {self.arquivo_pdf_criado_em.strftime('%d/%m/%Y às %H:%M')}"
                else:
                    return f"Documento gerado em {self.arquivo_pdf_criado_em.strftime('%d/%m/%Y às %H:%M')}"
            elif self.status_versao == self.STATUS_EM_PROCESSAMENTO:
                return f"Relatório sendo gerado..."
            elif self.status_versao == self.STATUS_NAO_GERADO:
                if self.VERSAO_NOMES[self.versao] == 'rascunho':
                    return "Nenhuma prévia gerada."
                else:
                    return "Nenhum documento gerado."

    def get_status_relatorio_apos_acertos(self):
        if not self.arquivo_pdf_apresentacao_apos_acertos:
            if self.status_versao_apresentacao_apos_acertos == self.STATUS_NAO_GERADO:
                if self.VERSAO_NOMES[self.versao_pdf_apresentacao_apos_acertos] == '-':
                    return "Nenhuma prévia gerada."
            elif self.status_versao_apresentacao_apos_acertos == self.STATUS_EM_PROCESSAMENTO:
                return f"Relatório sendo gerado..."
            elif self.status_versao_apresentacao_apos_acertos == self.STATUS_CONCLUIDO:
                if self.VERSAO_NOMES[self.versao_pdf_apresentacao_apos_acertos] == 'rascunho':
                    return "Nenhuma prévia gerada."
                else:
                    return "Nenhum documento gerado."
        elif self.arquivo_pdf_apresentacao_apos_acertos:
            if self.status_versao_apresentacao_apos_acertos == self.STATUS_CONCLUIDO:
                if self.VERSAO_NOMES[self.versao_pdf_apresentacao_apos_acertos] == 'rascunho':
                    return f"Prévia gerada em {self.arquivo_pdf_apresentacao_apos_acertos_criado_em.strftime('%d/%m/%Y às %H:%M')}"
                else:
                    return f"Documento gerado em {self.arquivo_pdf_apresentacao_apos_acertos_criado_em.strftime('%d/%m/%Y às %H:%M')}"
            elif self.status_versao_apresentacao_apos_acertos == self.STATUS_EM_PROCESSAMENTO:
                return f"Relatório sendo gerado..."
            elif self.status_versao_apresentacao_apos_acertos == self.STATUS_NAO_GERADO:
                if self.VERSAO_NOMES[self.versao_pdf_apresentacao_apos_acertos] == 'rascunho':
                    return "Nenhuma prévia gerada."
                else:
                    return "Nenhum documento gerado."

    def apaga_arquivo_pdf(self):
        self.arquivo_pdf = None
        self.arquivo_pdf_criado_em = None
        self.versao = self.VERSAO_NAO_GERADO
        self.status_versao = self.STATUS_NAO_GERADO
        self.save()

    def inicia_geracao_arquivo_pdf(self, previa):
        self.versao = self.VERSAO_RASCUNHO if previa else self.VERSAO_FINAL
        self.status_versao = self.STATUS_EM_PROCESSAMENTO
        self.save()

    def finaliza_geracao_arquivo_pdf(self, pdf):
        self.arquivo_pdf = pdf
        self.status_versao = self.STATUS_CONCLUIDO
        self.arquivo_pdf_criado_em = datetime.today()
        self.save()

    def cancela_geracao_arquivo_pdf(self):
        logging.info(f'Cancelando geração de arquivo pdf da análise {self.pk}')
        self.arquivo_pdf = None
        self.versao = self.VERSAO_NAO_GERADO
        self.status_versao = self.STATUS_NAO_GERADO
        self.arquivo_pdf_criado_em = None
        self.save()
        logging.info(f'Geração de arquivo pdf da análise {self.pk} cancelada')

    def apaga_arquivo_pdf_relatorio_apos_acertos(self):
        self.arquivo_pdf_apresentacao_apos_acertos = None
        self.arquivo_pdf_apresentacao_apos_acertos_criado_em = None
        self.versao_pdf_apresentacao_apos_acertos = self.VERSAO_NAO_GERADO
        self.status_versao_apresentacao_apos_acertos = self.STATUS_NAO_GERADO
        self.save()

    def inicia_geracao_arquivo_pdf_relatorio_apos_acertos(self, previa):
        self.versao_pdf_apresentacao_apos_acertos = self.VERSAO_RASCUNHO if previa else self.VERSAO_FINAL
        self.status_versao_apresentacao_apos_acertos = self.STATUS_EM_PROCESSAMENTO
        self.save()

    def finaliza_geracao_arquivo_pdf_relatorio_apos_acertos(self, pdf):
        self.arquivo_pdf_apresentacao_apos_acertos = pdf
        self.status_versao_apresentacao_apos_acertos = self.STATUS_CONCLUIDO
        self.arquivo_pdf_apresentacao_apos_acertos_criado_em = datetime.today()
        self.save()

    def cancela_geracao_arquivo_pdf_relatorio_apos_acertos(self):
        logging.info(f'Cancelando geração de arquivo pdf do relatorio após acertos {self.pk}')
        self.arquivo_pdf_apresentacao_apos_acertos = None
        self.arquivo_pdf_apresentacao_apos_acertos_criado_em = None
        self.versao_pdf_apresentacao_apos_acertos = self.VERSAO_NAO_GERADO
        self.status_versao_apresentacao_apos_acertos = self.STATUS_NAO_GERADO
        self.save()
        logging.info(f'Geração de arquivo pdf do relatorio após acertos {self.pk} cancelada')

    def verifica_se_requer_alteracao_em_lancamentos(self, considera_realizacao=True):
        from sme_ptrf_apps.core.models import TipoAcertoDocumento, TipoAcertoLancamento
        from sme_ptrf_apps.core.models import SolicitacaoAcertoLancamento, SolicitacaoAcertoDocumento
        categorias_que_requerem_alteracoes = [
            TipoAcertoLancamento.CATEGORIA_EDICAO_LANCAMENTO,
            TipoAcertoLancamento.CATEGORIA_EXCLUSAO_LANCAMENTO,
            TipoAcertoLancamento.CATEGORIA_CONCILIACAO_LANCAMENTO,
            TipoAcertoLancamento.CATEGORIA_DESCONCILIACAO_LANCAMENTO,
            TipoAcertoDocumento.CATEGORIA_INCLUSAO_GASTO,
            TipoAcertoDocumento.CATEGORIA_INCLUSAO_CREDITO,
            TipoAcertoDocumento.CATEGORIA_EDICAO_INFORMACAO
        ]

        analises_de_lancamentos_requerem_alteracoes = False
        analises_de_lancamento_que_requerem_alteracoes = self.analises_de_lancamentos.filter(
            solicitacoes_de_ajuste_da_analise__tipo_acerto__categoria__in=categorias_que_requerem_alteracoes
        )
        if analises_de_lancamento_que_requerem_alteracoes.exists():
            for analise_de_lancamento in analises_de_lancamento_que_requerem_alteracoes:
                solicitacoes_de_ajuste_da_analise_que_requerem_alteracoes_realizadas = analise_de_lancamento.solicitacoes_de_ajuste_da_analise.filter(
                    tipo_acerto__categoria__in=categorias_que_requerem_alteracoes
                )

                if(considera_realizacao):
                    solicitacoes_de_ajuste_da_analise_que_requerem_alteracoes_realizadas = solicitacoes_de_ajuste_da_analise_que_requerem_alteracoes_realizadas.filter(
                    status_realizacao=SolicitacaoAcertoLancamento.STATUS_REALIZACAO_REALIZADO)

                if solicitacoes_de_ajuste_da_analise_que_requerem_alteracoes_realizadas.exists():
                    analises_de_lancamentos_requerem_alteracoes = True
                    break

        analises_de_documentos_requerem_alteracoes = False
        analises_de_documento_que_requerem_alteracoes = self.analises_de_documento.filter(
            solicitacoes_de_ajuste_da_analise__tipo_acerto__categoria__in=categorias_que_requerem_alteracoes
        )
        if analises_de_documento_que_requerem_alteracoes.exists():
            for analise_de_documento in analises_de_documento_que_requerem_alteracoes:
                solicitacoes_de_ajuste_da_analise_que_requerem_alteracoes_realizadas = analise_de_documento.solicitacoes_de_ajuste_da_analise.filter(tipo_acerto__categoria__in=categorias_que_requerem_alteracoes)

                if(considera_realizacao):
                    solicitacoes_de_ajuste_da_analise_que_requerem_alteracoes_realizadas = solicitacoes_de_ajuste_da_analise_que_requerem_alteracoes_realizadas.filter(status_realizacao=SolicitacaoAcertoDocumento.STATUS_REALIZACAO_REALIZADO)

                if solicitacoes_de_ajuste_da_analise_que_requerem_alteracoes_realizadas.exists():
                    analises_de_documentos_requerem_alteracoes = True
                    break

        logger.info(f'Prestação de conta: {self.prestacao_conta.id}')
        logger.info(f'Análise de Prestação de conta: {self.id}')
        logger.info(f'analises_de_lancamentos_requerem_alteracoes: {analises_de_lancamentos_requerem_alteracoes}')
        logger.info(f'analises_de_documentos_requerem_alteracoes: {analises_de_documentos_requerem_alteracoes}')
        logger.info(f'É necessário recalcular fechamentos e documentos? {analises_de_lancamentos_requerem_alteracoes or analises_de_documentos_requerem_alteracoes}')
        return analises_de_lancamentos_requerem_alteracoes or analises_de_documentos_requerem_alteracoes

    @classmethod
    def editavel(cls, uuid_analise, visao):
        analise = AnalisePrestacaoConta.by_uuid(uuid_analise)
        ultima_analise_pc = analise.prestacao_conta.ultima_analise()

        if visao == "DRE":
            return False

        if ultima_analise_pc == analise:
            return True
        else:
            return False

    class Meta:
        verbose_name = "Análise de prestação de contas"
        verbose_name_plural = "16.0) Análises de prestações de contas"


auditlog.register(AnalisePrestacaoConta)

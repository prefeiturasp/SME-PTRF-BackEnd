from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from ...utils.choices_to_json import choices_to_json
from sme_ptrf_apps.core.models_abstracts import ModeloBase


class AnaliseLancamentoPrestacaoConta(ModeloBase):
    history = AuditlogHistoryField()

    # Status Choice
    RESULTADO_CORRETO = 'CORRETO'
    RESULTADO_AJUSTE = 'AJUSTE'

    RESULTADO_NOMES = {
        RESULTADO_CORRETO: 'Lançamento Correto',
        RESULTADO_AJUSTE: 'Ajuste necessário',
    }

    RESULTADO_CHOICES = (
        (RESULTADO_CORRETO, RESULTADO_NOMES[RESULTADO_CORRETO]),
        (RESULTADO_AJUSTE, RESULTADO_NOMES[RESULTADO_AJUSTE]),
    )

    # Tipo Lançamento Choice
    TIPO_LANCAMENTO_CREDITO = 'CREDITO'
    TIPO_LANCAMENTO_GASTO = 'GASTO'

    TIPO_LANCAMENTO_NOMES = {
        TIPO_LANCAMENTO_CREDITO: 'Crédito',
        TIPO_LANCAMENTO_GASTO: 'Gasto',
    }

    TIPO_LANCAMENTO_CHOICES = (
        (TIPO_LANCAMENTO_CREDITO, TIPO_LANCAMENTO_NOMES[TIPO_LANCAMENTO_CREDITO]),
        (TIPO_LANCAMENTO_GASTO, TIPO_LANCAMENTO_NOMES[TIPO_LANCAMENTO_GASTO]),
    )

    # Status realizacao choices
    STATUS_REALIZACAO_PENDENTE = 'PENDENTE'
    STATUS_REALIZACAO_REALIZADO = 'REALIZADO'
    STATUS_REALIZACAO_JUSTIFICADO = 'JUSTIFICADO'

    STATUS_REALIZACAO_NOMES = {
        STATUS_REALIZACAO_PENDENTE: 'Pendente',
        STATUS_REALIZACAO_REALIZADO: 'Realizado',
        STATUS_REALIZACAO_JUSTIFICADO: 'Justificado'
    }

    STATUS_REALIZACAO_CHOICES = (
        (STATUS_REALIZACAO_PENDENTE, STATUS_REALIZACAO_NOMES[STATUS_REALIZACAO_PENDENTE]),
        (STATUS_REALIZACAO_REALIZADO, STATUS_REALIZACAO_NOMES[STATUS_REALIZACAO_REALIZADO]),
        (STATUS_REALIZACAO_JUSTIFICADO, STATUS_REALIZACAO_NOMES[STATUS_REALIZACAO_JUSTIFICADO])
    )

    analise_prestacao_conta = models.ForeignKey('AnalisePrestacaoConta', on_delete=models.CASCADE,
                                                related_name='analises_de_lancamentos')

    tipo_lancamento = models.CharField(
        'Tipo Lançamento',
        max_length=20,
        choices=TIPO_LANCAMENTO_CHOICES,
        default=TIPO_LANCAMENTO_CREDITO
    )

    despesa = models.ForeignKey('despesas.Despesa', on_delete=models.CASCADE,
                                related_name='analises_de_lancamento_da_despesa', blank=True, null=True)

    receita = models.ForeignKey('receitas.Receita', on_delete=models.CASCADE,
                                related_name='analises_de_lancamento_da_receita', blank=True, null=True)

    resultado = models.CharField(
        'Status',
        max_length=20,
        choices=RESULTADO_CHOICES,
        default=RESULTADO_CORRETO
    )

    status_realizacao = models.CharField(
        'Status de realização',
        max_length=15,
        choices=STATUS_REALIZACAO_CHOICES,
        default=STATUS_REALIZACAO_PENDENTE
    )

    justificativa = models.TextField('Justificativa', max_length=300, blank=True, null=True, default=None)

    devolucao_tesouro_atualizada = models.BooleanField("Devolução ao Tesouro Atualizada?", default=False)

    lancamento_atualizado = models.BooleanField("Lançamento Atualizado?", default=False)

    lancamento_excluido = models.BooleanField("Lançamento Excluído?", default=False)

    esclarecimentos = models.TextField('Esclarecimentos', max_length=300, blank=True, null=True, default=None)

    def __str__(self):
        return f"{self.analise_prestacao_conta} - Resultado:{self.resultado}"

    def altera_status_realizacao(self, novo_status, justificativa=None):
        self.justificativa = justificativa
        self.status_realizacao = novo_status
        self.save()

    @classmethod
    def status_realizacao_choices_to_json(cls):
        return choices_to_json(cls.STATUS_REALIZACAO_CHOICES)

    @property
    def requer_atualizacao_devolucao_ao_tesouro(self):
        from . import TipoAcertoLancamento
        requer = self.solicitacoes_de_ajuste_da_analise.filter(
            tipo_acerto__categoria=TipoAcertoLancamento.CATEGORIA_DEVOLUCAO
        ).exists()
        return requer

    def passar_devolucao_tesouro_para_atualizada(self):
        self.devolucao_tesouro_atualizada = True
        self.save()
        return self

    @property
    def requer_atualizacao_lancamento(self):
        from . import TipoAcertoLancamento
        requer = self.solicitacoes_de_ajuste_da_analise.filter(
            tipo_acerto__categoria=TipoAcertoLancamento.CATEGORIA_EDICAO_LANCAMENTO
        ).exists()
        return requer

    def passar_lancamento_para_atualizado(self):
        self.lancamento_atualizado = True
        self.save()
        return self

    @property
    def requer_exclusao_lancamento(self):
        from . import TipoAcertoLancamento
        requer = self.solicitacoes_de_ajuste_da_analise.filter(
            tipo_acerto__categoria=TipoAcertoLancamento.CATEGORIA_EXCLUSAO_LANCAMENTO
        ).exists()
        return requer

    def passar_lancamento_para_excluido(self):
        self.lancamento_excluido = True
        self.save()
        return self

    @property
    def requer_ajustes_externos(self):
        from . import TipoAcertoLancamento
        requer = self.solicitacoes_de_ajuste_da_analise.filter(
            tipo_acerto__categoria=TipoAcertoLancamento.CATEGORIA_AJUSTES_EXTERNOS
        ).exists()
        return requer

    @property
    def requer_esclarecimentos(self):
        from . import TipoAcertoLancamento
        requer = self.solicitacoes_de_ajuste_da_analise.filter(
            tipo_acerto__categoria=TipoAcertoLancamento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO
        ).exists()
        return requer

    def incluir_esclarecimentos(self, esclarecimentos):
        self.esclarecimentos = esclarecimentos
        self.save()
        return self

    class Meta:
        verbose_name = "Análise de lançamento"
        verbose_name_plural = "16.1) Análises de lançamentos"


auditlog.register(AnaliseLancamentoPrestacaoConta)

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

    def __str__(self):
        return f"{self.analise_prestacao_conta} - Resultado:{self.resultado}"

    def altera_status_realizacao(self, novo_status, justificativa=None):
        self.justificativa = justificativa
        self.status_realizacao = novo_status
        self.save()

    @classmethod
    def status_realizacao_choices_to_json(cls):
        return choices_to_json(cls.STATUS_REALIZACAO_CHOICES)

    class Meta:
        verbose_name = "Análise de lançamento"
        verbose_name_plural = "16.1) Análises de lançamentos"


auditlog.register(AnaliseLancamentoPrestacaoConta)

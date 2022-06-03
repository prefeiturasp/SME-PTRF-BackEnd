from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

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

    analise_prestacao_conta = models.ForeignKey('AnalisePrestacaoConta', on_delete=models.CASCADE,
                                                related_name='analises_de_lancamentos')

    tipo_lancamento = models.CharField(
        'status',
        max_length=20,
        choices=TIPO_LANCAMENTO_CHOICES,
        default=TIPO_LANCAMENTO_CREDITO
    )

    despesa = models.ForeignKey('despesas.Despesa', on_delete=models.CASCADE,
                                related_name='analises_de_lancamento_da_despesa', blank=True, null=True)

    receita = models.ForeignKey('receitas.Receita', on_delete=models.CASCADE,
                                related_name='analises_de_lancamento_da_receita', blank=True, null=True)

    resultado = models.CharField(
        'status',
        max_length=20,
        choices=RESULTADO_CHOICES,
        default=RESULTADO_CORRETO
    )

    def __str__(self):
        return f"{self.analise_prestacao_conta} - Resultado:{self.resultado}"

    class Meta:
        verbose_name = "Análise de lançamento"
        verbose_name_plural = "16.1) Análises de lançamentos"


auditlog.register(AnaliseLancamentoPrestacaoConta)

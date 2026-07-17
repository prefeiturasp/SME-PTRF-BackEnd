"""Módulo de modelos para receitas previstas de outros recursos para um PAA.

Este módulo define a entidade responsável por registrar o saldo e a previsão
financeira de um outro recurso associado a um PAA em um período específico.
"""
from django.db import models
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.paa.models import Paa, OutroRecursoPeriodoPaa


class ReceitaPrevistaOutroRecursoPeriodo(ModeloBase):
    """
    Representa a previsão financeira de um outro recurso para um PAA.

    Essa model armazena saldos e valores previstos de custeio, capital e livre
    aplicação para um recurso de período vinculado a um PAA.
    """
    history = AuditlogHistoryField()
    paa = models.ForeignKey(Paa, on_delete=models.PROTECT,
                            verbose_name="PAA", blank=False, null=True)
    outro_recurso_periodo = models.ForeignKey(OutroRecursoPeriodoPaa, on_delete=models.PROTECT,
                                              verbose_name="Outro Recurso Período", blank=False, null=True)
    saldo_custeio = models.DecimalField('Saldo Custeio', max_digits=20, decimal_places=2, blank=False, null=True)
    saldo_capital = models.DecimalField('Saldo Capital', max_digits=20, decimal_places=2, blank=False, null=True)
    saldo_livre = models.DecimalField('Saldo Livre Aplicação', max_digits=20, decimal_places=2, blank=False, null=True)
    previsao_valor_custeio = models.DecimalField('Previsão Valor Custeio',
                                                 max_digits=20, decimal_places=2, default=0)
    previsao_valor_capital = models.DecimalField('Previsão Valor Capital',
                                                 max_digits=20, decimal_places=2, default=0)
    previsao_valor_livre = models.DecimalField('Previsão Valor Livre Aplicação',
                                               max_digits=20, decimal_places=2, default=0)

    def unidade_nome(self) -> str:
        """Retorna o nome da unidade escolar associada ao PAA."""
        return self.paa.associacao.unidade.nome
    unidade_nome.short_description = "Unidade"

    def outro_recurso_objeto(self) -> "ReceitaPrevistaOutroRecursoPeriodo":
        """Retorna o objeto do outro recurso vinculado ao período."""
        return self.outro_recurso_periodo.outro_recurso

    class Meta:
        verbose_name = "Receita Prevista Outro Recurso Período"
        verbose_name_plural = "Receitas Previstas Outros Recursos Períodos"
        constraints = [
            models.UniqueConstraint(
                fields=['paa', 'outro_recurso_periodo'],
                name='unique_receita_prevista_por_outro_recurso_periodo'
            )
        ]
        ordering = ('outro_recurso_periodo__outro_recurso__nome',)


auditlog.register(ReceitaPrevistaOutroRecursoPeriodo)

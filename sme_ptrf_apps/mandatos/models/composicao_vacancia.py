from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class ComposicaoVacancia(ModeloBase):
    history = AuditlogHistoryField()

    associacao = models.ForeignKey(
        'core.Associacao', verbose_name="Associação",
        on_delete=models.CASCADE, related_name='composicoes_vacancia_da_associacao'
    )
    mandato = models.ForeignKey(
        'Mandato', verbose_name="Mandato",
        on_delete=models.CASCADE, related_name='composicoes_vacancia_do_mandato'
    )

    class Meta:
        verbose_name = 'Composição de Vacância'
        verbose_name_plural = 'Composições de Vacância'
        constraints = [
            models.UniqueConstraint(
                fields=["associacao", "mandato"],
                name="uniq_composicao_vacancia_por_associacao_mandato",
            )
        ]

    def __str__(self):
        associacao_nome = self.associacao.nome if self.associacao and self.associacao.nome else ""
        referencia = self.mandato.referencia_mandato if self.mandato else ""
        return f"{associacao_nome} Período {referencia}"


auditlog.register(ComposicaoVacancia)

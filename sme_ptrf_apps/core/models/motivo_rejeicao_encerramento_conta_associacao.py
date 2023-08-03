from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class MotivoRejeicaoEncerramentoContaAssociacao(ModeloIdNome):
    history = AuditlogHistoryField()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Motivo de rejeição de encerramento de conta de associação"
        verbose_name_plural = "07.5) Motivos de rejeição de encerramento de conta de associação"
        unique_together = ['nome', ]


auditlog.register(MotivoRejeicaoEncerramentoContaAssociacao)

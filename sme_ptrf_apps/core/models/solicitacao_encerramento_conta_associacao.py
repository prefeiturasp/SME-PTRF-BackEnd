from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import pre_delete

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class SolicitacaoEncerramentoContaAssociacao(ModeloBase):
    history = AuditlogHistoryField()

    # Status Choice
    STATUS_PENDENTE = 'PENDENTE'
    STATUS_REJEITADA = 'REJEITADA'
    STATUS_APROVADA = 'APROVADA'

    STATUS_NOMES = {
        STATUS_PENDENTE: 'Pendente',
        STATUS_REJEITADA: 'Rejeitada',
        STATUS_APROVADA: 'Aprovada',
    }

    STATUS_CHOICES = (
        (STATUS_PENDENTE, STATUS_NOMES[STATUS_PENDENTE]),
        (STATUS_REJEITADA, STATUS_NOMES[STATUS_REJEITADA]),
        (STATUS_APROVADA, STATUS_NOMES[STATUS_APROVADA]),
    )

    conta_associacao = models.OneToOneField('ContaAssociacao', on_delete=models.CASCADE,
                                             related_name='solicitacao_encerramento', blank=True, null=True)
    status = models.CharField(
        'status',
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_PENDENTE
    )

    data_de_encerramento_na_agencia = models.DateField(
        'Data de encerramento na agência',
        blank=True,
        null=True,
    )

    def __str__(self):
        status = SolicitacaoEncerramentoContaAssociacao.STATUS_NOMES[self.status]
        return f"Solicitação #{self.id} {status}: {self.conta_associacao.__str__()}"

    @property
    def aprovada(self):
        return self.status == SolicitacaoEncerramentoContaAssociacao.STATUS_APROVADA

    @property
    def rejeitada(self):
        return self.status == SolicitacaoEncerramentoContaAssociacao.STATUS_REJEITADA

    @property
    def pendente(self):
        return self.status == SolicitacaoEncerramentoContaAssociacao.STATUS_PENDENTE

    @property
    def pode_apagar(self):
        return self.pendente

    class Meta:
        verbose_name = "Solicitação de Encerramento de Conta de Associação"
        verbose_name_plural = "07.4) Solicitações de Encerramento de Conta de Associação"

@receiver(post_save, sender=SolicitacaoEncerramentoContaAssociacao)
def on_save(sender, instance, **kwargs):
    if instance.conta_associacao:
        instance.conta_associacao.inativar()

@receiver(pre_delete, sender=SolicitacaoEncerramentoContaAssociacao)
def on_delete(sender, instance, **kwargs):
    if instance.conta_associacao:
        instance.conta_associacao.ativar()

auditlog.register(SolicitacaoEncerramentoContaAssociacao)

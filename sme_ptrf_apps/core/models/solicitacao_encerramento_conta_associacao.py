from datetime import date

from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

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

    motivos_rejeicao = models.ManyToManyField('MotivoRejeicaoEncerramentoContaAssociacao', blank=True)

    data_aprovacao = models.DateField(
        'Data de aprovação',
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

    def notificar_dre(self):
        from sme_ptrf_apps.core.services.notificacao_services import notificar_solicitacao_encerramento_conta_bancaria
        notificar_solicitacao_encerramento_conta_bancaria(conta_associacao=self.conta_associacao)

    def reenviar(self):
        self.status = SolicitacaoEncerramentoContaAssociacao.STATUS_PENDENTE
        self.motivos_rejeicao.clear()
        self.save()

    def aprovar(self):
        self.status = SolicitacaoEncerramentoContaAssociacao.STATUS_APROVADA
        self.motivos_rejeicao.clear()
        self.data_aprovacao = date.today()
        self.save()

    def reprovar(self):
        self.status = SolicitacaoEncerramentoContaAssociacao.STATUS_REJEITADA
        self.save()


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

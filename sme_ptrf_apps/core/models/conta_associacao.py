from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class ContaAssociacao(ModeloBase):
    history = AuditlogHistoryField()

    # Status Choice
    STATUS_ATIVA = 'ATIVA'
    STATUS_INATIVA = 'INATIVA'

    STATUS_NOMES = {
        STATUS_ATIVA: 'Ativa',
        STATUS_INATIVA: 'Inativa',
    }

    STATUS_CHOICES = (
        (STATUS_ATIVA, STATUS_NOMES[STATUS_ATIVA]),
        (STATUS_INATIVA, STATUS_NOMES[STATUS_INATIVA]),
    )

    associacao = models.ForeignKey('Associacao', on_delete=models.CASCADE, related_name='contas', blank=True, null=True)
    tipo_conta = models.ForeignKey('TipoConta', on_delete=models.PROTECT, blank=True, null=True)
    status = models.CharField(
        'status',
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_ATIVA
    )
    banco_nome = models.CharField('Nome do banco', max_length=50, blank=True, default='')
    agencia = models.CharField('Nº agência',  max_length=15, blank=True, default='')
    numero_conta = models.CharField('Nº conta', max_length=30, blank=True, default='')
    numero_cartao = models.CharField('Nº do cartão', max_length=80, blank=True, default='')


    def __str__(self):
        associacao = self.associacao.nome if self.associacao else 'ACM indefinida'
        tipo_conta = self.tipo_conta.nome if self.tipo_conta else 'Tipo de conta indefinido'
        status = ContaAssociacao.STATUS_NOMES[self.status]
        return f"{associacao} - Conta {tipo_conta} - {status}"

    @classmethod
    def get_valores(cls, user=None, associacao_uuid=None):
        query = cls.objects.filter(status=cls.STATUS_ATIVA)
        if user:
            query = query.filter(associacao__uuid=associacao_uuid)
        return query.all()

    class Meta:
        verbose_name = "Conta de Associação"

        verbose_name_plural = "07.1) Contas de Associações"

@receiver(pre_save, sender=ContaAssociacao)
def conta_associacao_pre_save(instance, **kwargs):
    if instance.tipo_conta.banco_nome and not instance.banco_nome:
        instance.banco_nome = instance.tipo_conta.banco_nome

    if instance.tipo_conta.agencia and not instance.agencia:
        instance.agencia = instance.tipo_conta.agencia

    if instance.tipo_conta.numero_conta and not instance.numero_conta:
        instance.numero_conta = instance.tipo_conta.numero_conta

    if instance.tipo_conta.numero_cartao and not instance.numero_cartao:
        instance.numero_cartao = instance.tipo_conta.numero_cartao


auditlog.register(ContaAssociacao)

from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch import receiver

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class ContasAtivasComSolicitacaoEmAberto(models.Manager):
    def get_queryset(self):
        from ..models import SolicitacaoEncerramentoContaAssociacao
        return super(ContasAtivasComSolicitacaoEmAberto, self).get_queryset().filter(Q(status=ContaAssociacao.STATUS_ATIVA) |
                                                               Q(solicitacao_encerramento__status=SolicitacaoEncerramentoContaAssociacao.STATUS_PENDENTE) |
                                                               Q(solicitacao_encerramento__status=SolicitacaoEncerramentoContaAssociacao.STATUS_REJEITADA))

class ContasEncerradas(models.Manager):
    def get_queryset(self):
        from ..models import SolicitacaoEncerramentoContaAssociacao
        return super(ContasEncerradas, self).get_queryset().filter(Q(status=ContaAssociacao.STATUS_INATIVA) &
                                                                 Q(solicitacao_encerramento__isnull=False)  &
                                                                 Q(solicitacao_encerramento__status=SolicitacaoEncerramentoContaAssociacao.STATUS_APROVADA))


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

    objects = models.Manager()
    ativas_com_solicitacao_em_aberto = ContasAtivasComSolicitacaoEmAberto()
    encerradas = ContasEncerradas()

    def __str__(self):
        associacao = self.associacao.nome if self.associacao else 'ACM indefinida'
        tipo_conta = self.tipo_conta.nome if self.tipo_conta else 'Tipo de conta indefinido'
        status = ContaAssociacao.STATUS_NOMES[self.status]
        return f"{associacao} - Conta {tipo_conta} - {status}"

    def inativar(self):
        self.status = self.STATUS_INATIVA
        self.save()

    def ativar(self):
        self.status = self.STATUS_ATIVA
        self.save()

    @property
    def inativa(self):
        return self.status == self.STATUS_INATIVA

    def pode_encerrar(self, data_encerramento):
        from sme_ptrf_apps.core.services.encerramento_conta_associacao_service import ValidaDataDeEncerramento

        validacao = ValidaDataDeEncerramento(associacao=self.associacao, data_de_encerramento=data_encerramento)
        return validacao.pode_encerrar

    def get_saldo_atual_conta(self):
        from sme_ptrf_apps.core.services.info_por_acao_services import info_conta_associacao_no_periodo
        from sme_ptrf_apps.core.models import Periodo
        periodo = Periodo.periodo_atual()
        saldos_conta = info_conta_associacao_no_periodo(self, periodo=periodo)
        saldo_conta = saldos_conta['saldo_atual_custeio'] + saldos_conta['saldo_atual_capital'] + saldos_conta['saldo_atual_livre']

        return saldo_conta

    def ativa_no_periodo(self, periodo):
        from sme_ptrf_apps.core.models import SolicitacaoEncerramentoContaAssociacao

        if hasattr(self, 'solicitacao_encerramento'):
            if self.solicitacao_encerramento.status != SolicitacaoEncerramentoContaAssociacao.STATUS_REJEITADA:
                data_encerramento = self.solicitacao_encerramento.data_de_encerramento_na_agencia

                if data_encerramento < periodo.data_inicio_realizacao_despesas:
                    return False

                return True
        else:
            return True


    @classmethod
    def get_valores(cls, user=None, associacao_uuid=None):
        query = cls.objects.all()
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

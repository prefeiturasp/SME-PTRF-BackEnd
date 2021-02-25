from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from .fornecedor import Fornecedor
from .validators import cpf_cnpj_validation
from ..status_cadastro_completo import STATUS_CHOICES, STATUS_COMPLETO, STATUS_INCOMPLETO
from ...core.models import Associacao


class Despesa(ModeloBase):
    history = AuditlogHistoryField()

    associacao = models.ForeignKey(Associacao, on_delete=models.PROTECT, related_name='despesas', blank=True,
                                   null=True)

    numero_documento = models.CharField('Nº do documento', max_length=100, default='', blank=True)

    tipo_documento = models.ForeignKey('TipoDocumento', on_delete=models.PROTECT, blank=True, null=True)

    data_documento = models.DateField('Data do documento', blank=True, null=True)

    cpf_cnpj_fornecedor = models.CharField(
        "CPF / CNPJ", max_length=20, validators=[cpf_cnpj_validation]
        , blank=True, null=True, default=""
    )

    nome_fornecedor = models.CharField("Nome do fornecedor", max_length=100, default='', blank=True)

    tipo_transacao = models.ForeignKey('TipoTransacao', on_delete=models.PROTECT, blank=True, null=True)

    documento_transacao = models.CharField('Nº doc transação', max_length=100, default='', blank=True)

    data_transacao = models.DateField('Data da transacao', blank=True, null=True)

    valor_total = models.DecimalField('Valor Total', max_digits=8, decimal_places=2, default=0)

    valor_recursos_proprios = models.DecimalField('Valor pago com recursos próprios', max_digits=8, decimal_places=2,
                                                  default=0)

    valor_original = models.DecimalField('Valor original', max_digits=8, decimal_places=2, default=0)

    status = models.CharField(
        'status',
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_INCOMPLETO
    )

    @property
    def valor_ptrf(self):
        return self.valor_total - self.valor_recursos_proprios

    @property
    def conferido(self):
        return not self.rateios.filter(conferido=False).exists()

    valor_ptrf.fget.short_description = 'Valor coberto pelo PTRF'

    def __str__(self):
        return f"{self.numero_documento} - {self.data_documento} - {self.valor_total:.2f}"

    def cadastro_completo(self):
        completo = self.tipo_documento and \
                   self.data_documento and \
                   self.cpf_cnpj_fornecedor and \
                   self.nome_fornecedor and \
                   self.tipo_transacao and \
                   self.data_transacao and \
                   self.valor_total > 0

        if completo and self.tipo_transacao.tem_documento:
            completo = completo and self.documento_transacao

        if completo and self.tipo_documento.numero_documento_digitado:
            completo = completo and self.numero_documento

        if completo:
            for rateio in self.rateios.all():
                completo = completo and rateio.status == STATUS_COMPLETO

        return completo

    def atualiza_status(self):
        cadastro_completo = self.cadastro_completo()
        status_completo = self.status == STATUS_COMPLETO
        if cadastro_completo != status_completo:
            self.save()  # Força um rec'alculo do status.

    @classmethod
    def by_documento(cls, tipo_documento, numero_documento, cpf_cnpj_fornecedor, associacao__uuid):
        return cls.objects.filter(associacao__uuid=associacao__uuid).filter(
            cpf_cnpj_fornecedor=cpf_cnpj_fornecedor).filter(tipo_documento=tipo_documento).filter(
            numero_documento=numero_documento).first()
    class Meta:
        verbose_name = "Despesa"
        verbose_name_plural = "Despesas"


@receiver(pre_save, sender=Despesa)
def proponente_pre_save(instance, **kwargs):
    instance.status = STATUS_COMPLETO if instance.cadastro_completo() else STATUS_INCOMPLETO


@receiver(post_save, sender=Despesa)
def rateio_post_save(instance, created, **kwargs):
    # Existe um motivo para o fornecedor não ser uma FK nesse modelo e ele ser atualizado indiretamente
    # A existência da tabela de fornecedores é apenas para facilitar o preenchimento da despesa pelas associações
    # Alterações feitas por uma associação no nome de um fornecedor não deve alterar diretamente as despesas de outras
    if instance and instance.cpf_cnpj_fornecedor and instance.nome_fornecedor:
        Fornecedor.atualiza_ou_cria(cpf_cnpj=instance.cpf_cnpj_fornecedor, nome=instance.nome_fornecedor)


auditlog.register(Despesa)

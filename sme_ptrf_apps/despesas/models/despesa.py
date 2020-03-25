from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from .validators import cpf_cnpj_validation
from ..status_cadastro_completo import STATUS_CHOICES, STATUS_INCOMPLETO, STATUS_COMPLETO
from ...core.models import Associacao


class Despesa(ModeloBase):
    associacao = models.ForeignKey(Associacao, on_delete=models.PROTECT, related_name='despesas', blank=True,
                                   null=True)

    numero_documento = models.CharField('Nº do documento', max_length=100, default='', blank=True)

    tipo_documento = models.ForeignKey('TipoDocumento', on_delete=models.PROTECT, blank=True, null=True)

    data_documento = models.DateField('Data do documento', blank=True, null=True)

    cpf_cnpj_fornecedor = models.CharField(
        "CPF / CNPJ", max_length=20, validators=[cpf_cnpj_validation]
        , blank=True, null=True, default=""
    )

    nome_fornecedor = models.CharField("Nome do fornecedor", max_length=100)

    tipo_transacao = models.ForeignKey('TipoTransacao', on_delete=models.PROTECT, blank=True, null=True)

    data_transacao = models.DateField('Data da transacao', blank=True, null=True)

    valor_total = models.DecimalField('Valor Total', max_digits=8, decimal_places=2, default=0)

    valor_recursos_proprios = models.DecimalField('Valor pago com recursos próprios', max_digits=8, decimal_places=2,
                                                  default=0)

    status = models.CharField(
        'status',
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_INCOMPLETO
    )

    @property
    def valor_ptrf(self):
        return self.valor_total - self.valor_recursos_proprios

    valor_ptrf.fget.short_description = 'Valor coberto pelo PTRF'

    def __str__(self):
        return f"{self.numero_documento} - {self.data_documento} - {self.valor_total:.2f}"

    def cadastro_completo(self):
        completo = self.numero_documento and \
                   self.tipo_documento and \
                   self.data_documento and \
                   self.cpf_cnpj_fornecedor and \
                   self.nome_fornecedor and \
                   self.tipo_transacao and \
                   self.data_transacao and \
                   self.valor_total > 0

        for rateio in self.rateios.all():
            completo = completo and rateio.status == STATUS_COMPLETO

        return completo

    def atualiza_status(self):
        cadastro_completo = self.cadastro_completo()
        status_completo = self.status == STATUS_COMPLETO
        if cadastro_completo != status_completo:
            self.save()  # Força um rec'alculo do status.

    class Meta:
        verbose_name = "Despesa"
        verbose_name_plural = "Despesas"


@receiver(pre_save, sender=Despesa)
def proponente_pre_save(instance, **kwargs):
    instance.status = STATUS_COMPLETO if instance.cadastro_completo else STATUS_INCOMPLETO

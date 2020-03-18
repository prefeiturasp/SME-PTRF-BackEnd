from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase

from ...core.models import Associacao

from .validators import cpf_cnpj_validation


class Despesa(ModeloBase):
    # Status Choice
    STATUS_COMPLETO = 'COMPLETO'
    STATUS_INCOMPLETO = 'INCOMPLETO'

    STATUS_NOMES = {
        STATUS_COMPLETO: 'Completo',
        STATUS_INCOMPLETO: 'Incompleto',
    }

    STATUS_CHOICES = (
        (STATUS_COMPLETO, STATUS_NOMES[STATUS_COMPLETO]),
        (STATUS_INCOMPLETO, STATUS_NOMES[STATUS_INCOMPLETO]),
    )



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

    class Meta:
        verbose_name = "Despesa"
        verbose_name_plural = "Despesas"


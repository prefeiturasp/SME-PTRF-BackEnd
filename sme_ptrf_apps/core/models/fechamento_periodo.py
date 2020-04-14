from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from sme_ptrf_apps.core.models_abstracts import ModeloBase

# Status Choice
STATUS_FECHADO = 'FECHADO'
STATUS_ABERTO = 'ABERTO'

STATUS_NOMES = {
    STATUS_ABERTO: 'Completo',
    STATUS_FECHADO: 'Fechado',
}

STATUS_CHOICES = (
    (STATUS_ABERTO, STATUS_NOMES[STATUS_ABERTO]),
    (STATUS_FECHADO, STATUS_NOMES[STATUS_FECHADO]),
)


class FechamentoPeriodo(ModeloBase):
    periodo = models.ForeignKey('Periodo', on_delete=models.PROTECT, related_name='fechamentos')

    associacao = models.ForeignKey('Associacao', on_delete=models.PROTECT, related_name='fechamentos_associacao',
                                   blank=True, null=True)

    conta_associacao = models.ForeignKey('ContaAssociacao', on_delete=models.PROTECT,
                                         related_name='fechamentos_da_conta', blank=True, null=True)

    acao_associacao = models.ForeignKey('AcaoAssociacao', on_delete=models.PROTECT,
                                        related_name='fechamentos_da_acao', blank=True, null=True)

    fechamento_anterior = models.ForeignKey('FechamentoPeriodo', on_delete=models.PROTECT,
                                            related_name='proximo_fechamento', null=True, blank=True)

    total_receitas_capital = models.DecimalField('Total Receitas (capital)', max_digits=12, decimal_places=2, default=0)
    total_repasses_capital = models.DecimalField('Total Repasses (capital)', max_digits=12, decimal_places=2, default=0)
    total_despesas_capital = models.DecimalField('Total Despesas (capital)', max_digits=12, decimal_places=2, default=0)

    saldo_reprogramado_capital = models.DecimalField('Saldo Reprogramado (capital)', max_digits=12, decimal_places=2,
                                                     default=0)

    total_receitas_custeio = models.DecimalField('Total Receitas (custeio)', max_digits=12, decimal_places=2, default=0)
    total_repasses_custeio = models.DecimalField('Total Repasses (custeio)', max_digits=12, decimal_places=2, default=0)
    total_despesas_custeio = models.DecimalField('Total Despesas (custeio)', max_digits=12, decimal_places=2, default=0)

    saldo_reprogramado_custeio = models.DecimalField('Saldo Reprogramado (custeio)', max_digits=12, decimal_places=2,
                                                     default=0)

    status = models.CharField(
        'status',
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_ABERTO
    )

    @property
    def total_receitas(self):
        return self.total_receitas_capital + self.total_receitas_custeio

    @property
    def total_despesas(self):
        return self.total_despesas_capital + self.total_despesas_custeio

    @property
    def saldo_reprogramado(self):
        return self.saldo_reprogramado_capital + self.saldo_reprogramado_custeio

    @property
    def saldo_anterior(self):
        return self.fechamento_anterior.saldo_reprogramado if self.fechamento_anterior else 0

    def __str__(self):
        periodo = f"{self.periodo.data_inicio_realizacao_despesas} - {self.periodo.data_fim_realizacao_despesas}"
        return f"{periodo}  - {self.status}"

    def calcula_saldo_reprogramado_capital(self):
        saldo_anterior = self.fechamento_anterior.saldo_reprogramado_capital if self.fechamento_anterior else 0
        return saldo_anterior \
               + self.total_receitas_capital \
               - self.total_despesas_capital

    def calcula_saldo_reprogramado_custeio(self):
        saldo_anterior = self.fechamento_anterior.saldo_reprogramado_custeio if self.fechamento_anterior else 0
        return saldo_anterior \
               + self.total_receitas_custeio \
               - self.total_despesas_custeio

    class Meta:
        verbose_name = "Fechamento de período"
        verbose_name_plural = "Fechamentos de períodos"


@receiver(pre_save, sender=FechamentoPeriodo)
def fechamento_pre_save(instance, **kwargs):
    instance.saldo_reprogramado_capital = instance.calcula_saldo_reprogramado_capital()
    instance.saldo_reprogramado_custeio = instance.calcula_saldo_reprogramado_custeio()

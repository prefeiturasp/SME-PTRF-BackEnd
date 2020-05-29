from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from sme_ptrf_apps.core.models_abstracts import ModeloBase

# Status Choice
STATUS_FECHADO = 'FECHADO'
STATUS_ABERTO = 'ABERTO'
STATUS_IMPLANTACAO = 'IMPLANTACAO'

STATUS_NOMES = {
    STATUS_ABERTO: 'Completo',
    STATUS_FECHADO: 'Fechado',
    STATUS_IMPLANTACAO: 'Implantação'
}

STATUS_CHOICES = (
    (STATUS_ABERTO, STATUS_NOMES[STATUS_ABERTO]),
    (STATUS_FECHADO, STATUS_NOMES[STATUS_FECHADO]),
    (STATUS_IMPLANTACAO, STATUS_NOMES[STATUS_IMPLANTACAO]),
)


class FechamentoPeriodo(ModeloBase):
    prestacao_conta = models.ForeignKey('PrestacaoConta', on_delete=models.CASCADE,
                                        related_name='fechamentos_da_prestacao', blank=True, null=True)

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

    @property
    def saldo_anterior_custeio(self):
        return self.fechamento_anterior.saldo_reprogramado_custeio if self.fechamento_anterior else 0

    @property
    def saldo_anterior_capital(self):
        return self.fechamento_anterior.saldo_reprogramado_capital if self.fechamento_anterior else 0

    def __str__(self):
        return f"{self.periodo} - {self.acao_associacao.acao.nome} - {self.conta_associacao.tipo_conta.nome}  - {self.status}"

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

    @classmethod
    def by_periodo_conta_acao(cls, periodo, conta_associacao, acao_associacao):
        if not periodo:
            return None

        qs = cls.objects.filter(periodo__id=periodo.id,
                                conta_associacao__id=conta_associacao.id,
                                acao_associacao__id=acao_associacao.id)
        if qs.exists():
            return qs.first()
        else:
            return None

    @classmethod
    def fechamentos_da_acao_no_periodo(cls, acao_associacao, periodo):
        return FechamentoPeriodo.objects.filter(acao_associacao=acao_associacao, periodo=periodo).all()

    @classmethod
    def criar(cls,
              prestacao_conta,
              acao_associacao,
              total_receitas_capital,
              total_repasses_capital,
              total_despesas_capital,
              total_receitas_custeio,
              total_repasses_custeio,
              total_despesas_custeio,
              ):
        fechamento_anterior = cls.by_periodo_conta_acao(periodo=prestacao_conta.periodo.periodo_anterior,
                                                        conta_associacao=prestacao_conta.conta_associacao,
                                                        acao_associacao=acao_associacao)
        novo_fechamento = cls.objects.create(
            prestacao_conta=prestacao_conta,
            periodo=prestacao_conta.periodo,
            associacao=prestacao_conta.associacao,
            conta_associacao=prestacao_conta.conta_associacao,
            acao_associacao=acao_associacao,
            total_receitas_capital=total_receitas_capital,
            total_repasses_capital=total_repasses_capital,
            total_despesas_capital=total_despesas_capital,
            total_receitas_custeio=total_receitas_custeio,
            total_repasses_custeio=total_repasses_custeio,
            total_despesas_custeio=total_despesas_custeio,
            fechamento_anterior=fechamento_anterior
        )
        return novo_fechamento

    class Meta:
        verbose_name = "Fechamento de período"
        verbose_name_plural = "Fechamentos de períodos"


@receiver(pre_save, sender=FechamentoPeriodo)
def fechamento_pre_save(instance, **kwargs):
    instance.saldo_reprogramado_capital = instance.calcula_saldo_reprogramado_capital()
    instance.saldo_reprogramado_custeio = instance.calcula_saldo_reprogramado_custeio()

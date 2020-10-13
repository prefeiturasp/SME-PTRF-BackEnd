import logging

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.receitas.tipos_aplicacao_recurso_receitas import APLICACAO_CAPITAL, APLICACAO_CUSTEIO

logger = logging.getLogger(__name__)

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


def get_especificacoes_despesas_default():
    return []


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
    total_receitas_devolucao_capital = models.DecimalField('Total Receitas Devolução (capital)', max_digits=12, decimal_places=2, default=0)
    total_repasses_capital = models.DecimalField('Total Repasses (capital)', max_digits=12, decimal_places=2, default=0)
    total_despesas_capital = models.DecimalField('Total Despesas (capital)', max_digits=12, decimal_places=2, default=0)

    saldo_reprogramado_capital = models.DecimalField('Saldo Reprogramado (capital)', max_digits=12, decimal_places=2,
                                                     default=0)

    total_receitas_custeio = models.DecimalField('Total Receitas (custeio)', max_digits=12, decimal_places=2, default=0)
    total_receitas_devolucao_custeio = models.DecimalField('Total Receitas Devolução (custeio)', max_digits=12, decimal_places=2, default=0)
    total_repasses_custeio = models.DecimalField('Total Repasses (custeio)', max_digits=12, decimal_places=2, default=0)
    total_despesas_custeio = models.DecimalField('Total Despesas (custeio)', max_digits=12, decimal_places=2, default=0)

    saldo_reprogramado_custeio = models.DecimalField('Saldo Reprogramado (custeio)', max_digits=12, decimal_places=2,
                                                     default=0)

    total_receitas_livre = models.DecimalField('Total Receitas (livre)', max_digits=12, decimal_places=2, default=0)
    total_receitas_devolucao_livre = models.DecimalField('Total Receitas Devolução (livre)', max_digits=12, decimal_places=2, default=0)
    total_repasses_livre = models.DecimalField('Total Repasses (livre)', max_digits=12, decimal_places=2, default=0)

    saldo_reprogramado_livre = models.DecimalField('Saldo Reprogramado (livre)', max_digits=12, decimal_places=2,
                                                   default=0)

    total_receitas_nao_conciliadas_capital = models.DecimalField('Receitas não conciliadas (capital)', max_digits=12,
                                                                 decimal_places=2, default=0)
    total_receitas_nao_conciliadas_custeio = models.DecimalField('Receitas não conciliadas (custeio)', max_digits=12,
                                                                 decimal_places=2, default=0)
    total_receitas_nao_conciliadas_livre = models.DecimalField('Receitas não conciliadas (livre)', max_digits=12,
                                                               decimal_places=2, default=0)

    total_despesas_nao_conciliadas_capital = models.DecimalField('Despesas não conciliadas (capital)', max_digits=12,
                                                                 decimal_places=2, default=0)

    total_despesas_nao_conciliadas_custeio = models.DecimalField('Despesas não conciliadas (custeio)', max_digits=12,
                                                                 decimal_places=2, default=0)

    especificacoes_despesas_capital = ArrayField(models.CharField(max_length=200), blank=True,
                                                 verbose_name='especificações das despesas (capital)',
                                                 default=get_especificacoes_despesas_default)

    especificacoes_despesas_custeio = ArrayField(models.CharField(max_length=200), blank=True,
                                                 verbose_name='especificações das despesas (custeio)',
                                                 default=get_especificacoes_despesas_default)
    status = models.CharField(
        'status',
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_ABERTO
    )

    @property
    def total_receitas(self):
        return self.total_receitas_capital + self.total_receitas_custeio + self.total_receitas_livre

    @property
    def total_despesas(self):
        return self.total_despesas_capital + self.total_despesas_custeio

    @property
    def saldo_reprogramado(self):
        return self.saldo_reprogramado_capital + self.saldo_reprogramado_custeio + self.saldo_reprogramado_livre

    @property
    def saldo_anterior(self):
        return self.fechamento_anterior.saldo_reprogramado if self.fechamento_anterior else 0

    @property
    def saldo_anterior_custeio(self):
        return self.fechamento_anterior.saldo_reprogramado_custeio if self.fechamento_anterior else 0

    @property
    def saldo_anterior_capital(self):
        return self.fechamento_anterior.saldo_reprogramado_capital if self.fechamento_anterior else 0

    @property
    def saldo_anterior_livre(self):
        return self.fechamento_anterior.saldo_reprogramado_livre if self.fechamento_anterior else 0

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

    def calcula_saldo_reprogramado_livre(self):
        saldo_anterior = self.fechamento_anterior.saldo_reprogramado_livre if self.fechamento_anterior else 0
        return saldo_anterior \
               + self.total_receitas_livre

    def calcula_saldo_reprogramado(self):

        saldo_reprogramado_custeio = self.calcula_saldo_reprogramado_custeio()
        saldo_reprogramado_capital = self.calcula_saldo_reprogramado_capital()
        saldo_reprogramado_livre = self.calcula_saldo_reprogramado_livre()

        logger.debug(f'Saldo Reprogramado (Custeio) antes de aplicar saldo livre:{saldo_reprogramado_custeio:.2f}')
        logger.debug(f'Saldo Reprogramado (Capital) antes de aplicar saldo livre:{saldo_reprogramado_capital:.2f}')
        logger.debug(f'Saldo Reprogramado (Livre) antes de aplicar saldo livre:{saldo_reprogramado_livre:.2f}')

        if saldo_reprogramado_custeio < 0:
            logger.debug(f'Usado saldo de livre aplicação para cobertura de custeio')
            saldo_reprogramado_livre += saldo_reprogramado_custeio
            saldo_reprogramado_custeio = 0

        if saldo_reprogramado_capital < 0:
            logger.debug(f'Usado saldo de livre aplicação para cobertura de capital')
            saldo_reprogramado_livre += saldo_reprogramado_capital
            saldo_reprogramado_capital = 0

        logger.debug(f'Saldo Reprogramado (Custeio) depois de aplicar saldo livre:{saldo_reprogramado_custeio:.2f}')
        logger.debug(f'Saldo Reprogramado (Capital) depois de aplicar saldo livre:{saldo_reprogramado_capital:.2f}')
        logger.debug(f'Saldo Reprogramado (Livre) depois de aplicar saldo livre:{saldo_reprogramado_livre:.2f}')

        return {
            'CUSTEIO': saldo_reprogramado_custeio,
            'CAPITAL': saldo_reprogramado_capital,
            'LIVRE': saldo_reprogramado_livre,
        }

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
    def fechamentos_da_acao_no_periodo(cls, acao_associacao, periodo, conta_associacao=None):
        qs = FechamentoPeriodo.objects.filter(acao_associacao=acao_associacao, periodo=periodo)

        if conta_associacao:
            qs = qs.filter(conta_associacao=conta_associacao)

        return qs.all()

    @classmethod
    def fechamentos_da_conta_no_periodo(cls, conta_associacao, periodo):
        return FechamentoPeriodo.objects.filter(conta_associacao=conta_associacao, periodo=periodo).all()

    @classmethod
    def criar(cls,
              prestacao_conta,
              acao_associacao,
              conta_associacao,
              total_receitas_capital,
              total_receitas_devolucao_capital,
              total_repasses_capital,
              total_despesas_capital,
              total_receitas_custeio,
              total_receitas_devolucao_custeio,
              total_receitas_devolucao_livre,
              total_repasses_custeio,
              total_despesas_custeio,
              total_receitas_livre,
              total_repasses_livre,
              total_receitas_nao_conciliadas_capital,
              total_receitas_nao_conciliadas_custeio,
              total_receitas_nao_conciliadas_livre,
              total_despesas_nao_conciliadas_capital,
              total_despesas_nao_conciliadas_custeio,
              especificacoes_despesas,
              ):
        fechamento_anterior = cls.by_periodo_conta_acao(periodo=prestacao_conta.periodo.periodo_anterior,
                                                        conta_associacao=conta_associacao,
                                                        acao_associacao=acao_associacao)
        novo_fechamento = cls.objects.create(
            prestacao_conta=prestacao_conta,
            periodo=prestacao_conta.periodo,
            associacao=prestacao_conta.associacao,
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            total_receitas_capital=total_receitas_capital,
            total_receitas_devolucao_capital=total_receitas_devolucao_capital,
            total_repasses_capital=total_repasses_capital,
            total_despesas_capital=total_despesas_capital,
            total_receitas_custeio=total_receitas_custeio,
            total_receitas_devolucao_custeio=total_receitas_devolucao_custeio,
            total_receitas_devolucao_livre=total_receitas_devolucao_livre,
            total_repasses_custeio=total_repasses_custeio,
            total_despesas_custeio=total_despesas_custeio,
            total_receitas_livre=total_receitas_livre,
            total_repasses_livre=total_repasses_livre,
            total_receitas_nao_conciliadas_capital=total_receitas_nao_conciliadas_capital,
            total_receitas_nao_conciliadas_custeio=total_receitas_nao_conciliadas_custeio,
            total_receitas_nao_conciliadas_livre=total_receitas_nao_conciliadas_livre,
            total_despesas_nao_conciliadas_capital=total_despesas_nao_conciliadas_capital,
            total_despesas_nao_conciliadas_custeio=total_despesas_nao_conciliadas_custeio,
            fechamento_anterior=fechamento_anterior,
            especificacoes_despesas_capital=especificacoes_despesas[APLICACAO_CAPITAL],
            especificacoes_despesas_custeio=especificacoes_despesas[APLICACAO_CUSTEIO],
        )
        return novo_fechamento

    @classmethod
    def implanta_saldo(cls, acao_associacao, conta_associacao, aplicacao, saldo):
        total_receitas_field = f'total_receitas_{aplicacao.lower()}'
        fechamento_implantacao = cls.objects.update_or_create(
            periodo=conta_associacao.associacao.periodo_inicial,
            associacao=conta_associacao.associacao,
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            defaults={
                total_receitas_field: saldo,
                'fechamento_anterior': None,
                'status': STATUS_IMPLANTACAO,
            }
        )

        return fechamento_implantacao

    class Meta:
        verbose_name = "Fechamento de período"
        verbose_name_plural = "09.1) Fechamentos de períodos"


@receiver(pre_save, sender=FechamentoPeriodo)
def fechamento_pre_save(instance, **kwargs):
    saldo_reprogramado = instance.calcula_saldo_reprogramado()
    instance.saldo_reprogramado_capital = saldo_reprogramado['CAPITAL']
    instance.saldo_reprogramado_custeio = saldo_reprogramado['CUSTEIO']
    instance.saldo_reprogramado_livre = saldo_reprogramado['LIVRE']

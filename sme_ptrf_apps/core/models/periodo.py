import datetime

from django.db import models
from django.db.models import Q

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class Periodo(ModeloBase):
    history = AuditlogHistoryField()
    referencia = models.CharField('Referência', max_length=7, blank=True, default="")

    data_inicio_realizacao_despesas = models.DateField('Inicio realização de despesas')
    data_fim_realizacao_despesas = models.DateField('Fim realização de despesas', blank=True, null=True)

    data_prevista_repasse = models.DateField('Data prevista do repasse', blank=True, null=True)

    data_inicio_prestacao_contas = models.DateField('Início prestação de contas', blank=True, null=True)
    data_fim_prestacao_contas = models.DateField('Fim prestação de contas', blank=True, null=True)

    periodo_anterior = models.ForeignKey('Periodo', on_delete=models.PROTECT, related_name='periodo_seguinte',
                                         blank=True, null=True)

    notificacao_inicio_periodo_pc_realizada = models.BooleanField('Notificação início período de PC realizada',
                                                                  blank=True, null=True, default=False)

    notificacao_pendencia_envio_pc_realizada = models.BooleanField('Notificação pendência envio PC realizada',
                                                                   blank=True, null=True, default=False)

    notificacao_proximidade_inicio_pc_realizada = models.BooleanField('Notificação proximidade início PC realizada',
                                                                      blank=True, null=True, default=False)

    notificacao_proximidade_fim_pc_realizada = models.BooleanField('Notificação proximidade fim PC realizada',
                                                                      blank=True, null=True, default=False)

    def __str__(self):
        return f"{self.referencia} - {self.data_inicio_realizacao_despesas} a {self.data_fim_realizacao_despesas}"

    @property
    def referencia_por_extenso(self):
        extenso = ""
        if self.referencia:
            ano, parte = self.referencia.split('.')
            if parte == 'u':
                extenso = f"Repasse {ano}"
            else:
                extenso = f"{parte}° repasse de {ano}"

        return extenso

    @property
    def proximo_periodo(self):
        return self.periodo_seguinte.first() if self.periodo_seguinte.exists() else None

    @property
    def encerrado(self):
        return self.data_fim_realizacao_despesas and self.data_fim_realizacao_despesas < datetime.date.today()

    @property
    def editavel(self):
        # O período não pode ser editado pelo usuário se houver um período que o referencia como período anterior
        return not self.periodo_seguinte.exists()

    @classmethod
    def periodo_atual(cls):
        return cls.objects.latest('data_inicio_realizacao_despesas') if cls.objects.exists() else None

    @classmethod
    def da_data(cls, data):
        periodos_da_data = cls.objects.filter(data_inicio_realizacao_despesas__lte=data).filter(
            Q(data_fim_realizacao_despesas__gte=data) | Q(data_fim_realizacao_despesas__isnull=True))
        return periodos_da_data.first() if periodos_da_data else None

    def notificacao_inicio_prestacao_de_contas_realizada(self):
        self.notificacao_inicio_periodo_pc_realizada = True
        self.save()

    def notificacao_pendencia_envio_prestacao_de_contas_realizada(self):
        self.notificacao_pendencia_envio_pc_realizada = True

    def notificacao_proximidade_inicio_prestacao_de_contas_realizada(self):
        self.notificacao_proximidade_inicio_pc_realizada = True
        self.save()

    def notificacao_proximidade_fim_prestacao_de_contas_realizada(self):
        self.notificacao_proximidade_fim_pc_realizada = True
        self.save()

    def get_referencia(self):
        # Necessario para utilizar a função "sorted", que retornará um erro se for um property
        return self.referencia

    class Meta:
        verbose_name = "Período"
        verbose_name_plural = "08.0) Períodos"


class PeriodoPrevia:
    def __init__(self, uuid, referencia, data_inicio, data_fim):
        self.uuid = uuid
        self.referencia = referencia
        self.data_inicio_realizacao_despesas = data_inicio
        self.data_fim_realizacao_despesas = data_fim

    def __str__(self):
        return f"{self.referencia} - {self.data_inicio_realizacao_despesas} a {self.data_fim_realizacao_despesas}"


auditlog.register(Periodo)

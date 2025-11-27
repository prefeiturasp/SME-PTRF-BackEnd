from django.db.models import Sum
from django.db import models
from datetime import datetime
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from ckeditor.fields import RichTextField
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.paa.models.periodo_paa import PeriodoPaa
from sme_ptrf_apps.paa.enums import PaaStatusEnum


class Paa(ModeloBase):
    history = AuditlogHistoryField()
    periodo_paa = models.ForeignKey(PeriodoPaa, on_delete=models.PROTECT, verbose_name='Período PAA',
                                    blank=False, null=True)
    associacao = models.ForeignKey(Associacao, on_delete=models.PROTECT, verbose_name='Associação',
                                   blank=False, null=True)
    saldo_congelado_em = models.DateTimeField(
        verbose_name="Saldo congelado em", blank=True, null=True)
    texto_introducao = RichTextField(null=True, verbose_name='Texto introdução')
    texto_conclusao = RichTextField(null=True, verbose_name='Texto conclusão')
    status = models.CharField(max_length=20, null=True, blank=True,
                              default=PaaStatusEnum.EM_ELABORACAO.name,
                              choices=PaaStatusEnum.choices())
    objetivos = models.ManyToManyField('ObjetivoPaa', related_name='paas', blank=True)
    atividades_estatutarias = models.ManyToManyField(
        'AtividadeEstatutaria', through='AtividadeEstatutariaPaa', related_name='paas', blank=True)

    def periodo_paa_objeto(self):
        return self.periodo_paa

    def set_congelar_saldo(self):
        self.saldo_congelado_em = datetime.now()
        self.save()

    def set_descongelar_saldo(self):
        self.saldo_congelado_em = None
        self.save()

    def get_total_recursos_proprios(self):
        total = self.recursopropriopaa_set.aggregate(total=Sum('valor'))['total']
        return total or 0

    def pode_gerar_documento_final(self):
        if not self.documentopaa_set.exists() and self.objetivos.exists() and self.texto_introducao != "" and self.texto_conclusao != ""

    class Meta:
        verbose_name = 'PAA'
        verbose_name_plural = 'PAA`s'
        unique_together = ('periodo_paa', 'associacao')

    def __str__(self):
        return f'{self.periodo_paa} - {self.associacao}'


auditlog.register(Paa)

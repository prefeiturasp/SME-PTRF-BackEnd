from django.db import models
from ...core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class ConsolidadoDRE(ModeloBase):
    history = AuditlogHistoryField()

    STATUS_NAO_GERADOS = 'NAO_GERADOS'
    STATUS_GERADOS_PARCIAIS = 'GERADOS_PARCIAIS'
    STATUS_GERADOS_TOTAIS = 'GERADOS_TOTAIS'
    STATUS_EM_PROCESSAMENTO = 'EM_PROCESSAMENTO'

    STATUS_NOMES = {
        STATUS_NAO_GERADOS: 'Documentos não gerados',
        STATUS_GERADOS_PARCIAIS: 'Documentos parciais gerados',
        STATUS_GERADOS_TOTAIS: 'Documentos finais gerados',
        STATUS_EM_PROCESSAMENTO: 'Documentos em processamento'
    }

    STATUS_CHOICES = (
        (STATUS_NAO_GERADOS, STATUS_NOMES[STATUS_NAO_GERADOS]),
        (STATUS_GERADOS_PARCIAIS, STATUS_NOMES[STATUS_GERADOS_PARCIAIS]),
        (STATUS_GERADOS_TOTAIS, STATUS_NOMES[STATUS_GERADOS_TOTAIS]),
        (STATUS_EM_PROCESSAMENTO, STATUS_NOMES[STATUS_EM_PROCESSAMENTO]),
    )

    dre = models.ForeignKey('core.Unidade', on_delete=models.PROTECT, related_name='consolidados_dre_da_dre',
                            to_field="codigo_eol", blank=True, null=True, limit_choices_to={'tipo_unidade': 'DRE'})

    periodo = models.ForeignKey('core.Periodo', on_delete=models.PROTECT,
                                related_name='consolidados_dre_do_periodo')

    status = models.CharField(
        'status',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NAO_GERADOS
    )

    class Meta:
        verbose_name = 'Consolidado DRE'
        verbose_name_plural = 'Consolidados DREs'
        unique_together = ['periodo', 'dre']

    def __str__(self):
        if self.status == self.STATUS_EM_PROCESSAMENTO:
            status_str = 'Documentos sendo gerados. Aguarde.'
        elif self.status == self.STATUS_NAO_GERADOS:
            status_str = 'Documentos não gerados'
        else:
            status_str = f"Documentos {'finais' if self.status == 'GERADOS_TOTAIS' else 'parciais'} " \
                         f"gerados dia {self.alterado_em.strftime('%d/%m/%Y %H:%M')}"

        return status_str

    @classmethod
    def criar(cls, dre, periodo):
        consolidado_dre = cls.objects.filter(dre=dre, periodo=periodo).first()

        if not consolidado_dre:
            consolidado_dre = ConsolidadoDRE.objects.create(
                dre=dre,
                periodo=periodo,
                status=cls.STATUS_NAO_GERADOS
            )

        return consolidado_dre

    def passar_para_status_em_processamento(self):
        self.status = self.STATUS_EM_PROCESSAMENTO
        self.save()
        return self

    def passar_para_status_gerado(self, parcial):
        self.status = self.STATUS_GERADOS_TOTAIS if not parcial else self.STATUS_GERADOS_PARCIAIS
        self.save()
        return self

    def get_valor_status_choice(self):
        return self.get_status_display()


auditlog.register(ConsolidadoDRE)

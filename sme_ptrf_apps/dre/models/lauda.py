from django.contrib.auth import get_user_model
from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class Lauda(ModeloBase):
    history = AuditlogHistoryField()

    # Status geração Choice
    STATUS_NAO_GERADA = 'NAO_GERADA'
    STATUS_GERADA_PARCIAL = 'GERADA_PARCIAL'
    STATUS_GERADA_TOTAL = 'GERADA_TOTAL'
    STATUS_EM_PROCESSAMENTO = 'EM_PROCESSAMENTO'

    STATUS_NOMES = {
        STATUS_NAO_GERADA: 'Lauda não gerada',
        STATUS_GERADA_PARCIAL: 'Lauda parcial gerada',
        STATUS_GERADA_TOTAL: 'Lauda final gerada',
        STATUS_EM_PROCESSAMENTO: 'Lauda em processamento',
    }

    STATUS_CHOICES = (
        (STATUS_NAO_GERADA, STATUS_NOMES[STATUS_NAO_GERADA]),
        (STATUS_GERADA_PARCIAL, STATUS_NOMES[STATUS_GERADA_PARCIAL]),
        (STATUS_GERADA_TOTAL, STATUS_NOMES[STATUS_GERADA_TOTAL]),
        (STATUS_EM_PROCESSAMENTO, STATUS_NOMES[STATUS_EM_PROCESSAMENTO]),
    )

    arquivo_lauda_txt = models.FileField(blank=True, null=True, verbose_name='Arquivo Lauda TXT')

    consolidado_dre = models.ForeignKey('ConsolidadoDRE', on_delete=models.CASCADE,
                                        related_name='laudas_do_consolidado_dre',
                                        blank=True, null=True)

    dre = models.ForeignKey('core.Unidade', on_delete=models.PROTECT, related_name='laudas_da_dre',
                            to_field="codigo_eol", blank=True, null=True, limit_choices_to={'tipo_unidade': 'DRE'})

    periodo = models.ForeignKey('core.Periodo', on_delete=models.PROTECT, blank=True, null=True,
                                related_name='laudas_do_periodo')

    tipo_conta = models.ForeignKey('core.TipoConta', on_delete=models.PROTECT, blank=True, null=True,
                                   related_name='laudas_do_tipo_conta')

    usuario = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, default='', blank=True, null=True,
                                related_name='laudas_do_usuario')

    status = models.CharField(
        'status',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NAO_GERADA
    )

    class Meta:
        verbose_name = 'Lauda'
        verbose_name_plural = 'Laudas'

    def __str__(self):
        if self.status == self.STATUS_EM_PROCESSAMENTO:
            status_str = 'Lauda sendo gerada. Aguarde.'
        elif self.status == self.STATUS_NAO_GERADA:
            status_str = 'Lauda não gerada'
        else:
            status_str = f"Lauda {'final' if self.status == 'GERADA_TOTAL' else 'parcial'} " \
                         f"gerada dia {self.alterado_em.strftime('%d/%m/%Y %H:%M')}"

        return status_str

    @classmethod
    def criar_ou_retornar_lauda(cls, consolidado_dre, dre, periodo, usuario):
        lauda, _ = cls.objects.get_or_create(
            consolidado_dre=consolidado_dre,
            dre=dre,
            periodo=periodo,
            usuario=usuario,
            defaults={
                'consolidado_dre': consolidado_dre,
                'dre': dre,
                'periodo': periodo,
                'usuario': usuario,
            },
        )

        return lauda

    def passar_para_status_em_processamento(self):
        self.status = self.STATUS_EM_PROCESSAMENTO
        self.save()
        return self

    def passar_para_status_gerado(self, parcial):
        self.status = self.STATUS_GERADA_TOTAL if not parcial else self.STATUS_GERADA_PARCIAL
        self.save()
        return self


auditlog.register(Lauda)

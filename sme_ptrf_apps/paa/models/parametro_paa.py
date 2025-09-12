from django.db import models
from ckeditor.fields import RichTextField

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase, SingletonModel
from ..choices import Mes


class ParametroPaa(SingletonModel, ModeloBase):
    history = AuditlogHistoryField()
    mes_elaboracao_paa = models.IntegerField(choices=Mes.choices, verbose_name='Mês de elaboração do PAA',
                                             help_text='indica o mês que pode ser iniciada a elaboração do PAA',
                                             blank=False, null=True)

    texto_pagina_paa_ue = RichTextField(null=True, verbose_name='Texto da página de PAA (UE)')
    
    introducao_do_paa_ue_1 = RichTextField(null=True, verbose_name='Introdução do PAA 1')
    
    introducao_do_paa_ue_2 = RichTextField(null=True, verbose_name='Introdução do PAA 2')

    conclusao_do_paa_ue_1 = RichTextField(null=True, verbose_name='Conclusão do PAA 1')
    
    conclusao_do_paa_ue_2 = RichTextField(null=True, verbose_name='Conclusão do PAA 2')
    class Meta:
        verbose_name = 'Parâmetro do PAA'
        verbose_name_plural = 'Parâmetros do PAA'

    def __str__(self):
        return 'Parâmetros do PAA'


auditlog.register(ParametroPaa)

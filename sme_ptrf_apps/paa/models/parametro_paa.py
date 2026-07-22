"""
Módulo de modelos do PAA (Plano Anual de Ação).

Este módulo define a entidade responsável por representar os parâmetros do PAA
e seus atributos de negócio.
"""
from django.db import models
from ckeditor.fields import RichTextField

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase, SingletonModel
from ..choices import Mes


class ParametroPaa(SingletonModel, ModeloBase):
    """
    Representa os parâmetros do PAA (Plano Anual de Ação).

    Essa model armazena os parâmetros que definem o comportamento
    e as características do PAA, incluindo o mês de elaboração,
    textos de introdução e conclusão, e outros elementos de
    conteúdo que são utilizados na geração do PAA.
    """
    history = AuditlogHistoryField()
    mes_elaboracao_paa = models.IntegerField(choices=Mes.choices, verbose_name='Mês de elaboração do PAA',
                                             help_text='indica o mês que pode ser iniciada a elaboração do PAA',
                                             blank=False, null=True)

    texto_pagina_paa_ue = RichTextField(null=True, verbose_name='Texto da página de PAA (UE)', blank=True)

    introducao_do_paa_ue_1 = RichTextField(null=True, verbose_name='Introdução do PAA 1', blank=True)

    introducao_do_paa_ue_2 = RichTextField(null=True, verbose_name='Introdução do PAA 2', blank=True)

    texto_atividades_previstas = RichTextField(null=True, verbose_name='Texto das atividades previstas', blank=True)

    conclusao_do_paa_ue_1 = RichTextField(null=True, verbose_name='Conclusão do PAA 1', blank=True)

    conclusao_do_paa_ue_2 = RichTextField(null=True, verbose_name='Conclusão do PAA 2', blank=True)

    texto_levantamento_prioridades = RichTextField(null=True, verbose_name='Texto do levantamento de prioridades',
                                                   blank=True)

    informe_bloqueio_prioridades = RichTextField(null=True, verbose_name='Informe de bloqueio de prioridades',
                                                 blank=True)

    class Meta:
        verbose_name = 'Parâmetro do PAA'
        verbose_name_plural = 'Parâmetros do PAA'

    def __str__(self) -> str:
        """Retorna uma representação textual do parâmetro do PAA."""
        return 'Parâmetros do PAA'


auditlog.register(ParametroPaa)

from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome


class TipoAcertoLancamento(ModeloIdNome):
    # Categoria Choices
    CATEGORIA_BASICO = 'BASICO'
    CATEGORIA_DEVOLUCAO = 'DEVOLUCAO'

    CATEGORIA_NOMES = {
        CATEGORIA_BASICO: 'Básico',
        CATEGORIA_DEVOLUCAO: 'Devolução'
    }

    CATEGORIA_CHOICES = (
        (CATEGORIA_BASICO, CATEGORIA_NOMES[CATEGORIA_BASICO]),
        (CATEGORIA_DEVOLUCAO, CATEGORIA_NOMES[CATEGORIA_DEVOLUCAO]),
    )

    categoria = models.CharField(
        'status',
        max_length=35,
        choices=CATEGORIA_CHOICES,
        default=CATEGORIA_BASICO
    )

    class Meta:
        verbose_name = "Tipo de acerto em lançamentos"
        verbose_name_plural = "15.1) Tipos de acerto em lançamentos"

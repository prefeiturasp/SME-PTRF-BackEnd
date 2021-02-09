from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.core.choices.tipos_carga import CARGA_CHOICES, CARGA_ASSOCIACOES, CARGA_NOMES


class ModeloCarga(ModeloBase):
    tipo_carga = models.CharField(
        'tipo de carga',
        max_length=35,
        choices=CARGA_CHOICES,
        default=CARGA_ASSOCIACOES,
        unique=True,
    )
    arquivo = models.FileField(blank=True, null=True)

    class Meta:
        verbose_name = "modelo de carga"
        verbose_name_plural = "02.1) Modelos de carga"

    def __str__(self):
        return CARGA_NOMES[self.tipo_carga] if self.tipo_carga else ""

    @classmethod
    def tipos_cargas_to_json(cls):
        return [{
                'id': choice[0],
                'nome': choice[1]
                }
                for choice in CARGA_CHOICES]

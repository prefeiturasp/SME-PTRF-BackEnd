from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase


class MotivoAprovacaoRessalva(ModeloBase):
    lookup_field = 'uuid'
    motivo = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Motivo de aprovação com ressalva'
        verbose_name_plural = 'Motivos de aprovação com ressalva'

    def __str__(self):
        return self.motivo

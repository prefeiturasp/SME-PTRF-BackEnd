from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase


# Status Choice
CARGA_REPASSE_REALIZADO = 'REPASSE_REALIZADO'

CARGA_NOMES = {
    CARGA_REPASSE_REALIZADO: 'Repasse realizado',
}

CARGA_CHOICES = (
    (CARGA_REPASSE_REALIZADO, CARGA_NOMES[CARGA_REPASSE_REALIZADO]),
)


class Arquivo(ModeloBase):
    identificador = models.SlugField(unique=True)
    conteudo = models.FileField(blank=True, null=True)
    tipo_carga = models.CharField(
        'status',
        max_length=35,
        choices=CARGA_CHOICES,
        default=CARGA_REPASSE_REALIZADO
    )

    class Meta:
        verbose_name = "arquivo"
        verbose_name_plural = "arquivos"

    def __str__(self):
        return self.identificador

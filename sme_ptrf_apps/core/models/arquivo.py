from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase

# Status Choice
CARGA_REPASSE_REALIZADO = 'REPASSE_REALIZADO'
CARGA_PERIODO_INICIAL = 'CARGA_PERIODO_INICIAL'
CARGA_REPASSE_PREVISTO = 'REPASSE_PREVISTO'

CARGA_NOMES = {
    CARGA_REPASSE_REALIZADO: 'Repasses realizados',
    CARGA_PERIODO_INICIAL: 'Carga período inicial',
    CARGA_REPASSE_PREVISTO: 'Repasses previstos',
}

CARGA_CHOICES = (
    (CARGA_REPASSE_REALIZADO, CARGA_NOMES[CARGA_REPASSE_REALIZADO]),
    (CARGA_PERIODO_INICIAL, CARGA_NOMES[CARGA_PERIODO_INICIAL]),
    (CARGA_REPASSE_PREVISTO, CARGA_NOMES[CARGA_REPASSE_PREVISTO]),
)


class Arquivo(ModeloBase):
    identificador = models.SlugField(unique=True)
    conteudo = models.FileField(blank=True, null=True)
    tipo_carga = models.CharField(
        'tipo de carga',
        max_length=35,
        choices=CARGA_CHOICES,
        default=CARGA_REPASSE_REALIZADO
    )

    class Meta:
        verbose_name = "arquivo de carga"
        verbose_name_plural = "arquivos de carga"

    def __str__(self):
        return self.identificador

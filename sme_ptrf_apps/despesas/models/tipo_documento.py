from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome


class TipoDocumento(ModeloIdNome):
    apenas_digitos = models.BooleanField("Apenas dígitos?", default=False)
    numero_documento_digitado = models.BooleanField("Número documento será digitado?", default=False)

    class Meta:
        verbose_name = "Tipo de documento"
        verbose_name_plural = "Tipos de documento"

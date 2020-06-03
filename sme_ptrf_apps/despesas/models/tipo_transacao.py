from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome


class TipoTransacao(ModeloIdNome):
    tem_documento = models.BooleanField("Tem documento?", default=False)

    class Meta:
        verbose_name = "Tipo de transação"
        verbose_name_plural = "Tipos de transação"

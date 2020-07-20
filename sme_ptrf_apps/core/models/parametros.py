from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase, SingletonModel
from ckeditor.fields import RichTextField

class Parametros(SingletonModel, ModeloBase):
    permite_saldo_conta_negativo = models.BooleanField('Permite saldo negativo em contas?', default=True)
    fique_de_olho = RichTextField(null=True)

    def __str__(self):
        return 'Parâmetros do PTRF'

    class Meta:
        verbose_name = "Parâmetro"
        verbose_name_plural = "Parâmetros"

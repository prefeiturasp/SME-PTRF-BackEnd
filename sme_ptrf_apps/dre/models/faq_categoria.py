from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase


class FaqCategoria(ModeloBase):
    lookup_field = 'uuid'
    nome = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Faq - Categoria'
        verbose_name_plural = 'Faqs - Categorias'

    def __str__(self):
        return self.nome

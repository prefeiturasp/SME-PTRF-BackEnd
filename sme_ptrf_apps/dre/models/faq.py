from django.db import models
from .faq_categoria import FaqCategoria
from sme_ptrf_apps.core.models_abstracts import ModeloBase


class Faq(ModeloBase):
    lookup_field = 'uuid'
    pergunta = models.CharField(max_length=200)
    resposta = models.TextField()
    categoria = models.ForeignKey(FaqCategoria, on_delete=models.PROTECT, related_name='perguntas')

    class Meta:
        verbose_name = 'Faq - Pergunta e Resposta'
        verbose_name_plural = 'Faqs - Perguntas e Respostas'

    def __str__(self):
        return self.pergunta

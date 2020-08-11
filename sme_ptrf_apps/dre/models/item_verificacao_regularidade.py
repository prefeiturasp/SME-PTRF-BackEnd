from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class ItemVerificacaoRegularidade(ModeloBase):
    descricao = models.TextField('Descrição')
    lista = models.ForeignKey('ListaVerificacaoRegularidade', on_delete=models.CASCADE, related_name="itens_de_verificacao")

    def __str__(self):
        return self.descricao

    class Meta:
        verbose_name = 'Item de verificação de regularidade'
        verbose_name_plural = 'Itens de verificação de regularidade'

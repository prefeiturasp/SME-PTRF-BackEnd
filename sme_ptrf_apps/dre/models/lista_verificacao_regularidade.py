from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class ListaVerificacaoRegularidade(ModeloBase):
    titulo = models.CharField('Título da lista', max_length=100)
    grupo = models.ForeignKey('GrupoVerificacaoRegularidade', on_delete=models.CASCADE, related_name="listas_de_verificacao")

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Lista de verificação de regularidade'
        verbose_name_plural = 'Listas de verificação de regularidade'

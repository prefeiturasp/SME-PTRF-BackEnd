from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class GrupoVerificacaoRegularidade(ModeloBase):
    titulo = models.CharField('Titulo do grupo', max_length=100)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Grupo de verificação de regularidade'
        verbose_name_plural = 'Grupos de verificação de regularidade'

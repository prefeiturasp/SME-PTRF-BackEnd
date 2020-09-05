from django.db import models

from sme_ptrf_apps.core.models import Categoria, Remetente, TipoNotificacao
from sme_ptrf_apps.core.models_abstracts import ModeloBase


class Notificacao(ModeloBase):
    tipo = models.ForeignKey(TipoNotificacao, on_delete=models.PROTECT, blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, blank=True, null=True)
    remetente = models.ForeignKey(Remetente, on_delete=models.PROTECT, blank=True, null=True)
    titulo = models.CharField("Título", max_length=100, default='', blank=True)
    descricao = models.CharField("Descrição", max_length=300, default='', blank=True)
    hora = models.TimeField("Hora", editable=False, auto_now_add=True)
    ativo = models.BooleanField("Foi Lido?", default=False)

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"

    def __str__(self):
        return self.titulo

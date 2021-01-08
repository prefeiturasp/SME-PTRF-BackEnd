from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome


class Acao(ModeloIdNome):
    posicao_nas_pesquisas = models.CharField(
        'posição nas pesquisas',
        max_length=10,
        blank=True,
        default='ZZZZZZZZZZ',
        help_text='A ordem alfabética desse texto definirá a ordem que a ação será exibida nas pesquisas.'
    )

    e_recursos_proprios = models.BooleanField("Recursos Externos", default=False)

    class Meta:
        verbose_name = "Ação"
        verbose_name_plural = "03.0) Ações"

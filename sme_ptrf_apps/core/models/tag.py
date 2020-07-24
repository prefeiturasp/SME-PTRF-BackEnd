from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from sme_ptrf_apps.core.choices import StatusTag


class Tag(ModeloIdNome):
    status = models.CharField(
        'status',
        max_length=60,
        blank=True,
        null=True,
        choices=StatusTag.choices(),
        default=StatusTag.INATIVO.value
    )

    def __str__(self):
        return f"<{self.nome}, {self.status}>"

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

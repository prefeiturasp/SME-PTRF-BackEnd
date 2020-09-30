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

    @classmethod
    def get_valores(cls, user=None, associacao_uuid=None):
        query = cls.objects.filter(status=StatusTag.ATIVO.name)
        return query.all()

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "10.0) Tags"

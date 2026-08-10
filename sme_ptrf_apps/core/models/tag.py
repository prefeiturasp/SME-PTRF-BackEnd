from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from sme_ptrf_apps.core.choices import StatusTag
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class Tag(ModeloIdNome):
    history = AuditlogHistoryField()
    status = models.CharField(
        'status',
        max_length=60,
        blank=True,
        null=True,
        choices=StatusTag.choices(),
        default=StatusTag.INATIVO.value
    )
    recurso = models.ForeignKey(
        "core.Recurso",
        verbose_name="Recurso",
        on_delete=models.PROTECT,
        null=False
    )

    def __str__(self):
        return f"<{self.nome}, {self.status}>"

    @classmethod
    def get_valores(cls, user=None, associacao_uuid=None):
        query = cls.objects.filter(status=StatusTag.ATIVO.name)
        return query.all()

    @classmethod
    def filter_by_recurso(cls, queryset, recurso):
        return queryset.filter(recurso=recurso)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "10.0) Tags"
        unique_together = ['nome', 'recurso']


auditlog.register(Tag)

from html import unescape
from django.db import models
from django.utils.html import strip_tags

from ckeditor.fields import RichTextField

from sme_ptrf_apps.core.models_abstracts import ModeloBase

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.utils.truncate_text import truncate_text


class TipoTextoFiqueDeOlhoChoices(models.TextChoices):
    ASSOCIACOES_PRESTACAO_CONTAS = "associacoes_prestacao_contas", "ASSOCIAÇÕES - Prestação de Contas"
    DIRETORIAS_CONSOLIDADO_DAS_PCS = "diretorias_consolidado_das_pcs", "DIRETORIAS - Consolidado das PCs"


class FiqueDeOlho(ModeloBase):
    history = AuditlogHistoryField()

    texto = RichTextField(null=True, verbose_name='Texto do fique de olho')

    tipo_texto = models.CharField(
        max_length=35,
        choices=TipoTextoFiqueDeOlhoChoices.choices,
        verbose_name="Tipo de texto",
    )

    recurso = models.ForeignKey(
        "core.Recurso",
        on_delete=models.PROTECT,
        verbose_name="Recurso",
    )

    def __str__(self):
        texto_sem_tags = strip_tags(self.texto) if self.texto else ""
        texto_truncado = truncate_text(texto_sem_tags, 50)
        tipo_texto_display = " (" + self.get_tipo_texto_display() + ")"

        return f"{texto_truncado}{tipo_texto_display} - {self.recurso.nome}"

    def delete(self, *args, **kwargs):
        # Impede a exclusão. A não ser que esse método seja implementado.
        pass

    def get_tipo_texto_display(self):
        return TipoTextoFiqueDeOlhoChoices(self.tipo_texto).label

    def get_short_texto(self):
        texto_sem_tags = strip_tags(self.texto) if self.texto else ""

        return truncate_text(unescape(texto_sem_tags), 40)

    @classmethod
    def filter_by_recurso(cls, recurso, qs=None):
        obj = cls.objects

        if qs is not None:
            obj = qs

        return obj.filter(recurso=recurso)

    @classmethod
    def filter_by_tipo_texto(cls, tipo_texto, qs=None):
        obj = cls.objects

        if qs is not None:
            obj = qs

        return obj.filter(tipo_texto=tipo_texto)

    @classmethod
    def get_first_with_recurso_and_tipo_texto(cls, recurso, tipo_texto):
        qs = cls.filter_by_recurso(recurso)
        qs = cls.filter_by_tipo_texto(tipo_texto=tipo_texto, qs=qs)

        return qs.first()

    class Meta:
        verbose_name = "Fique de olho"
        verbose_name_plural = "01.1) Fique de olho"
        unique_together = ("tipo_texto", "recurso")


auditlog.register(FiqueDeOlho)

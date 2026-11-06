from django.conf import settings
from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase


class RecebimentoEmailAlertaPagina(ModeloBase):
    alerta = models.ForeignKey(
        "core.AlertaPagina",
        on_delete=models.CASCADE,
        related_name="recebimentos_email",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recebimentos_email_alertas",
    )
    data_ocorrencia = models.DateField()
    enviado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.enviado_em} - {self.alerta.get_categoria_display()}"

    class Meta:
        verbose_name = "Recebimento de e-mail de alerta"
        verbose_name_plural = "01.3) Recebimentos de e-mails de alertas"
        constraints = [
            models.UniqueConstraint(
                fields=["alerta", "usuario", "data_ocorrencia"],
                name="uniq_email_alerta_usuario_ocorrencia",
            )
        ]
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from ckeditor.fields import RichTextField
from django.core.exceptions import ValidationError
from django.db import models
from ..querysets import AlertaPaginaQuerySet
from ..choices import AlertaPaginaCategoriaChoices

from sme_ptrf_apps.core.models_abstracts import ModeloBase, TemAtivo


class AlertaPagina(TemAtivo, ModeloBase):
    history = AuditlogHistoryField()

    texto = RichTextField(
        verbose_name='Texto',
        help_text='O texto que será exibido no conteúdo do alerta.'
    )

    categoria = models.CharField(
        'Categoria',
        max_length=255,
        choices=AlertaPaginaCategoriaChoices.choices
    )

    data_disparo = models.DateField(
        'Data de disparo',
        help_text='Vale o dia/mês, repetidos todo ano. O ano informado é o primeiro ano em que o alerta passa a valer'
    )

    recurso = models.ForeignKey(
        "core.Recurso",
        on_delete=models.PROTECT,
        verbose_name="Recurso",
        help_text='Recurso ao qual o alerta se refere'
    )

    enviar_email = models.BooleanField(
        'Enviar e-mail?',
        default=False,
        help_text='Define se o alerta será enviado por e-mail. Necessário estar configurado em Periodic tasks.'
    )

    assunto_email = models.CharField(
        'Assunto do e-mail',
        max_length=255,
        blank=True,
        help_text='Assunto do e-mail. Quando "Enviar e-mail?" estiver habilitado.'
    )

    grupos_email = models.ManyToManyField(
        'auth.Group',
        verbose_name='Grupos de usuários',
        help_text=(
            'Grupos com usuários que receberão o e-mail. '
            'Apenas usuários de Associações com o campo Recurso selecionado neste alerta.'
        ),
        blank=True,
        related_name='alertas_paginas',
    )

    ultimo_envio_email_em = models.DateField(
        'Ultimo envio de e-mail',
        blank=True,
        null=True,
        editable=False,
        help_text=(
            'Registra data de envio de e-mail o alerta. '
            'Usado para idempotência(evitar o disparo de e-mails repetidos).'
        )
    )

    objects = AlertaPaginaQuerySet.as_manager()

    def __str__(self):
        return f"{self.get_categoria_display()} - {self.data_disparo:%d/%m} - {self.recurso.nome}"

    def clean(self):
        super().clean()

        if self.enviar_email and not self.assunto_email:
            raise ValidationError({
                'assunto_email': 'O assunto do e-mail deve ser informado.'
            })

    class Meta:
        verbose_name = 'Alerta de pagina'
        verbose_name_plural = '01.2) Alertas de paginas'
        constraints = (
            models.UniqueConstraint(
                fields=['categoria', 'recurso', 'data_disparo'],
                name='uniq_alerta_pagina_categoria_recurso_data_disparo',
                violation_error_message='Já existe um alerta com a mesma categoria, recurso e data de disparo.'
            ),
        )


auditlog.register(AlertaPagina)

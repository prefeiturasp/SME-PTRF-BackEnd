from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.core.exceptions import ValidationError


class Mandato(ModeloBase):
    history = AuditlogHistoryField()
    referencia_mandato = models.CharField('Referência do mandato', max_length=50)
    data_inicial = models.DateField(verbose_name='Data de início do mandato')
    data_final = models.DateField(verbose_name='Data de término do mandato')

    class Meta:
        verbose_name = 'Mandato'
        verbose_name_plural = 'Mandatos'

    def __str__(self):
        return self.referencia_mandato


    def clean(self):
        super().clean()

        # Verificar se a data final é menor que a data inicial
        if self.data_final < self.data_inicial:
            raise ValidationError('A data final não pode ser menor que a data inicial')

        # Verificar se a data inicial está dentro de outro mandato existente
        if self.data_inicial is not None and self.data_final is not None:
            mandatos = Mandato.objects.filter(data_inicial__lte=self.data_inicial, data_final__gte=self.data_inicial)

            if self.pk:
                mandatos = mandatos.exclude(pk=self.pk)  # Excluir o próprio objeto atual ao verificar colisões

            if mandatos.exists():
                raise ValidationError('A data inicial informada é de vigência de outro mandato cadastrado.')

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)


auditlog.register(Mandato)

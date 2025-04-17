from datetime import date

from django.db import models
from django.core.exceptions import ValidationError

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.paa.utils import ajustar_data_inicial_e_final, validar_data_final


class PeriodoPaa(ModeloBase):
    history = AuditlogHistoryField()
    referencia = models.CharField('Referência do período', max_length=150)
    data_inicial = models.DateField(verbose_name='Data de início do período')
    data_final = models.DateField(verbose_name='Data de término do período')

    class Meta:
        verbose_name = 'Período PAA'
        verbose_name_plural = 'Períodos PAA'

    def __str__(self):
        return self.referencia

    @property
    def editavel(self):
        # O período não pode ser editado pelo usuário se houver um período que o referencia como período anterior
        # validação futura quando houve o model de Paa
        return True

    @classmethod
    def periodo_vigente(cls):
        """
        Retornar um período vigente, ou seja, o período que está em vigor no momento atual.
        """
        hoje = date.today()
        return cls.objects.filter(data_inicial__lte=hoje, data_final__gte=hoje).order_by("data_inicial").first()

    def clean(self):
        # Validar se a data final é maior ou igual à data inicial ou se tem o mesmo mês com dias diferentes
        data_final_e_valida, mensagem = validar_data_final(self.data_inicial, self.data_final)
        if not data_final_e_valida:
            raise ValidationError(mensagem)
        if self.data_final < self.data_inicial:
            raise ValidationError('A data final deve ser maior que a data inicial')
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        data_inicial, data_final = ajustar_data_inicial_e_final(self.data_inicial, self.data_final)
        self.data_inicial = data_inicial
        self.data_final = data_final
        return super().save(*args, **kwargs)


auditlog.register(PeriodoPaa)

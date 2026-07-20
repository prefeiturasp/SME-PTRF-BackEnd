"""
Módulo de modelos do PAA (Plano Anual de Ação).

Este módulo define a entidade responsável por
representar os periodos do PAA e seus atributos de negócio.
"""
from datetime import date

from django.db import models
from django.core.exceptions import ValidationError

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.paa.utils import ajustar_data_inicial_e_final, validar_data_final


class PeriodoPaa(ModeloBase):
    """
    Representa um período do PAA (Plano Anual de Ação).

    Essa model armazena informações sobre os períodos do PAA, incluindo referência,
    datas de início e término, e fornece métodos para validação e manipulação desses períodos.
    """
    history = AuditlogHistoryField()
    referencia = models.CharField('Referência do período', max_length=150)
    data_inicial = models.DateField(verbose_name='Data de início do período')
    data_final = models.DateField(verbose_name='Data de término do período')

    class Meta:
        verbose_name = 'Período PAA'
        verbose_name_plural = 'Períodos PAA'
        ordering = ('-data_inicial',)

    def __str__(self) -> str:
        """Retorna uma representação textual do período PAA."""
        return self.referencia

    @property
    def editavel(self) -> bool:
        """Verifica se o período PAA é editável com base na existência de PAAs gerados no período."""
        from sme_ptrf_apps.paa.services import PeriodoPaaService
        return not PeriodoPaaService(self).existe_paas_gerados_no_periodo()

    @property
    def ano_inicial_final(self) -> str | None:
        """Retorna uma string representando o ano inicial e final do período PAA."""
        if not self.data_inicial or not self.data_final:
            return None

        return f"{self.data_inicial.year}/{self.data_final.year}"

    @classmethod
    def periodo_vigente(cls):
        """
        Retornar um período vigente, ou seja, o período que está em vigor no momento atual.
        """
        hoje = date.today()
        return cls.objects.filter(data_inicial__year=hoje.year).order_by("data_inicial").first()

    def clean(self) -> None:
        """Valida os campos do período PAA antes de salvar."""
        # Validar se a data final é maior ou igual à data inicial ou se tem o mesmo mês com dias diferentes
        data_final_e_valida, mensagem = validar_data_final(self.data_inicial, self.data_final)
        if not data_final_e_valida:
            raise ValidationError(mensagem)

        # validar se o período já existe com a referencia, data_inicial e data_final
        if PeriodoPaa.objects.filter(
            referencia=self.referencia,
            data_inicial__year=self.data_inicial.year,
            data_inicial__month=self.data_inicial.month,
            data_final__year=self.data_final.year,
            data_final__month=self.data_final.month,
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Referência do PAA já existe.')
        super().clean()

    def save(self, *args, **kwargs) -> None:
        """Salva o período PAA após validar e ajustar as datas inicial e final."""
        self.full_clean()
        data_inicial, data_final = ajustar_data_inicial_e_final(self.data_inicial, self.data_final)
        self.data_inicial = data_inicial
        self.data_final = data_final
        return super().save(*args, **kwargs)


auditlog.register(PeriodoPaa)

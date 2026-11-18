"""
Módulo de modelos do PAA (Plano Anual de Ação).

Este módulo define a entidade responsável por
representar os periodos do PAA e seus atributos de negócio.
"""
from datetime import date

from django.db import models
from django.core.exceptions import ValidationError
from typing import Optional

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.paa.enums import PaaStatusEnum
from sme_ptrf_apps.paa.utils import ajustar_data_inicial_e_final, validar_data_final
from sme_ptrf_apps.paa import constantes


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
    def periodo_vigente(cls) -> Optional['PeriodoPaa']:
        """Retorna o período vigente na data atual (delega para `vigente_em`)."""
        return cls.vigente_em(date.today())

    @classmethod
    def vigente_em(cls, hoje: date) -> Optional['PeriodoPaa']:
        """Retorna o período vigente na data, conforme o critério configurado em constantes.

        Critério padrão (ano corrente): período cuja data inicial está no ano da data.
        Critério alternativo (janela de datas): período cuja janela contém a data.

        Args:
            hoje: Data de referência.

        Returns:
            O período vigente ou `None` se não houver.
        """
        if constantes.CRITERIO_PERIODO_VIGENTE == constantes.CRITERIO_PERIODO_VIGENTE_JANELA_DE_DATAS:
            return cls.objects.filter(
                data_inicial__lte=hoje, data_final__gte=hoje).order_by('data_inicial').first()
        return cls.objects.filter(data_inicial__year=hoje.year).order_by('data_inicial').first()

    @classmethod
    def proxima_vigencia_em(cls, hoje: date, vigente: Optional['PeriodoPaa'] = None) -> Optional['PeriodoPaa']:
        """Retorna o período da Próxima Vigência: o primeiro que começa depois do fim do vigente.

        Sem período vigente, é o primeiro período que começa depois da data informada.

        Args:
            hoje: Data de referência.
            vigente: Período vigente já conhecido, para evitar nova consulta.

        Returns:
            O período da Próxima Vigência ou `None` se não houver.
        """
        vigente = vigente or cls.vigente_em(hoje)
        limite = vigente.data_final if vigente else hoje
        proximo_periodo = cls.objects.filter(data_inicial__gt=limite).order_by('data_inicial').first()
        return proximo_periodo

    @classmethod
    def vigente_e_proxima_vigencia_em(cls, hoje: date) -> tuple:
        """Retorna o par (vigente, próxima vigência) na data, com duas consultas no máximo."""
        vigente = cls.vigente_em(hoje)
        return vigente, cls.proxima_vigencia_em(hoje, vigente=vigente)

    @staticmethod
    def classificar_vigencia(periodo: 'PeriodoPaa', vigente: Optional['PeriodoPaa'],
                             proxima: Optional['PeriodoPaa'], hoje: date) -> str:
        """Classifica o período como VIGENTE, PROXIMA_VIGENCIA, ENCERRADO ou FUTURO(constantes).

        Args:
            periodo: Período a classificar.
            vigente: Período vigente na data.
            proxima: Período da Próxima Vigência na data.
            hoje: Data de referência.
        """
        if vigente and periodo.pk == vigente.pk:
            return constantes.VIGENCIA_VIGENTE
        if proxima and periodo.pk == proxima.pk:
            return constantes.VIGENCIA_PROXIMA_VIGENCIA
        if periodo.data_final < hoje:
            return constantes.VIGENCIA_ENCERRADO
        return constantes.VIGENCIA_FUTURO

    @classmethod
    def sobrepostos(cls, data_inicial: date, data_final: date, ignora_pk: None | int = None) -> models.QuerySet:
        """Retorna os períodos cujas datas se sobrepõem ao intervalo informado.

        Args:
            data_inicial: Primeiro dia do intervalo.
            data_final: Último dia do intervalo.
            ignora_pk: Período a ser desconsiderado.

        Returns:
            QuerySet de períodos sobrepostos, ordenados pela data inicial.
        """
        return (
            cls.objects
            .filter(data_inicial__lte=data_final, data_final__gte=data_inicial)
            .exclude(pk=ignora_pk)
            .order_by('data_inicial')
        )

    @classmethod
    def tem_sobreposicao_relevante(cls, hoje: date) -> bool:
        """Indica se o período vigente ou o da Próxima Vigência se sobrepõe a outro período.

        Trava de segurança: com períodos sobrepostos, a classificação de vigência deixa de ser única.

        Args:
            hoje: Data de referência.

        Returns:
            `True` se houver sobreposição envolvendo o vigente ou a Próxima Vigência.
        """
        return any(
            periodo and cls.sobrepostos(periodo.data_inicial, periodo.data_final, periodo.pk).exists()
            for periodo in cls.vigente_e_proxima_vigencia_em(hoje)
        )

    @classmethod
    def anterior_a(cls, periodo: 'PeriodoPaa') -> Optional['PeriodoPaa']:
        """Retorna o período imediatamente anterior ao informado, ou `None` se não houver.

        Args:
            periodo: Período de referência.

        Returns:
            Período que terminou antes do início do informado e tem a maior data inicial.
        """
        return cls.objects.filter(data_final__lt=periodo.data_inicial).order_by('-data_inicial').first()

    @classmethod
    def relevantes_para(cls, associacao, hoje: date) -> models.QuerySet:
        """Retorna os períodos relevantes para decidir o estado do botão de elaboração do PAA.

        Args:
            associacao: Associação consultada.
            hoje: Data de referência.

        Returns:
            QuerySet ordenado pela data inicial, sem duplicidades, com o período vigente, a Próxima
            Vigência imediata e os períodos encerrados com PAA da associação em
            elaboração. (casos quando a UE não finalizar até o fim o período)
        """
        vigente, proxima = cls.vigente_e_proxima_vigencia_em(hoje)
        condicao = (
            models.Q(pk=vigente.pk if vigente else None) |
            models.Q(pk=proxima.pk if proxima else None) |
            models.Q(paa__associacao=associacao, paa__status=PaaStatusEnum.EM_ELABORACAO.name, data_final__lt=hoje)
        )
        return cls.objects.filter(condicao).distinct().order_by('data_inicial')

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

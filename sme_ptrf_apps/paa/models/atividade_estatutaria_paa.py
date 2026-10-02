"""
Módulo de modelos para atividades estatutárias do PAA.

Este módulo define a entidade responsável por registrar as atividades
estatutárias associadas a um PAA em uma data específica.
"""
from django.db import models
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.paa.models.paa import Paa


class AtividadeEstatutariaPaa(ModeloBase):
    """
    Representa a associação de uma atividade estatutária a um PAA em uma data específica.

    Essa model registra a ocorrência da atividade no contexto de um plano anual,
    vinculando uma atividade estatutária a um PAA e ao período em que ela foi
    realizada ou deverá ser considerada.
    """
    history = AuditlogHistoryField()
    atividade_estatutaria = models.ForeignKey('paa.AtividadeEstatutaria', on_delete=models.PROTECT)
    paa = models.ForeignKey('paa.Paa', on_delete=models.PROTECT, verbose_name="PAA")
    data = models.DateField('Data da atividade', blank=False, null=False)

    def __str__(self) -> str:
        """Retorna uma representação textual da atividade com o nome e a data."""
        return f"{self.atividade_estatutaria.nome} - {self.data.strftime('%d/%m/%Y')}"

    @classmethod
    def todas_datas_preenchidas(cls, paa: Paa) -> bool:
        """
        Verifica se todas as atividades estatutárias ativas do PAA possuem data preenchida.

        Args:
            paa: Instância do PAA a ser verificada.

        Returns:
            bool: True se não houver atividade estatutária ativa sem data
            registrada para o PAA, False caso contrário.
        """
        atividades_estatutarias_sem_data = cls.verificar_atividades_estatutarias_sem_datas(paa)

        if not atividades_estatutarias_sem_data:
            return True

        return False

    @classmethod
    def verificar_atividades_estatutarias_sem_datas(cls, paa: Paa) -> bool:
        """
        Verifica se existem atividades estatutárias ativas sem nenhuma data registrada para o PAA.

        Considera as atividades estatutárias ativas que sejam globais
        (sem PAA vinculado) ou específicas do PAA informado, comparando
        a quantidade total com a quantidade de atividades que já possuem
        ao menos um registro de data em AtividadeEstatutariaPaa.

        Args:
            paa: Instância do PAA a ser verificada.

        Returns:
            bool: True se houver atividade estatutária ativa sem data
            registrada, False caso contrário (inclusive quando não há
            atividades estatutárias ativas).
        """
        from django.db.models import Q
        from sme_ptrf_apps.paa.choices import StatusChoices
        from sme_ptrf_apps.paa.models.atividade_estatutaria import AtividadeEstatutaria

        atividades_estatutaria = AtividadeEstatutaria.objects.filter(
            Q(paa__isnull=True) | Q(paa=paa),
            status=StatusChoices.ATIVO,
        )

        if not atividades_estatutaria.exists():
            return False

        atividades_preenchidas_ids = cls.objects.filter(
            paa=paa,
            atividade_estatutaria__in=atividades_estatutaria
        ).values_list('atividade_estatutaria_id', flat=True)

        if len(atividades_estatutaria) > len(atividades_preenchidas_ids):
            return True

        return False

    class Meta:
        verbose_name = "Atividade Estatutária PAA"
        verbose_name_plural = "Atividades Estatutárias PAA"
        unique_together = ['atividade_estatutaria', 'paa', 'data']


auditlog.register(AtividadeEstatutariaPaa)

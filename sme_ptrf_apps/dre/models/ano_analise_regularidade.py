from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from sme_ptrf_apps.core.models_abstracts import TemCriadoEm, TemAlteradoEm
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class AnoAnaliseRegularidade(TemCriadoEm, TemAlteradoEm):
    # Status de atualização
    STATUS_NENHUMA_ATUALIZACAO_REQUERIDA = 'NENHUMA_REQUERIDA'
    STATUS_AGUARDANDO_INICIO_ATUALIZACAO = 'AGUARDANDO_INICIO'
    STATUS_ATUALIZACAO_EM_PROCESSAMENTO = 'EM_PROCESAMENTO'
    STATUS_ATUALIZACAO_CONCLUIDA = 'CONCLUIDA'

    STATUS_ATUALIZACAO_NOMES = {
        STATUS_NENHUMA_ATUALIZACAO_REQUERIDA: 'Nenhuma atualização requerida',
        STATUS_AGUARDANDO_INICIO_ATUALIZACAO: 'Aguardando inicio de processo de atualização',
        STATUS_ATUALIZACAO_EM_PROCESSAMENTO: 'Atualização de regularidade em processamento',
        STATUS_ATUALIZACAO_CONCLUIDA: 'Atualização de regularidade concluída'
    }

    STATUS_ATUALIZACAO_CHOICES = (
        (STATUS_NENHUMA_ATUALIZACAO_REQUERIDA, STATUS_ATUALIZACAO_NOMES[STATUS_NENHUMA_ATUALIZACAO_REQUERIDA]),
        (STATUS_AGUARDANDO_INICIO_ATUALIZACAO, STATUS_ATUALIZACAO_NOMES[STATUS_AGUARDANDO_INICIO_ATUALIZACAO]),
        (STATUS_ATUALIZACAO_EM_PROCESSAMENTO, STATUS_ATUALIZACAO_NOMES[STATUS_ATUALIZACAO_EM_PROCESSAMENTO]),
        (STATUS_ATUALIZACAO_CONCLUIDA, STATUS_ATUALIZACAO_NOMES[STATUS_ATUALIZACAO_CONCLUIDA]),
    )

    history = AuditlogHistoryField()
    lookup_field = 'ano'
    ano = models.PositiveSmallIntegerField(
        'Ano de análise de regularidade',
        default=2020,
        validators=[MaxValueValidator(2099), MinValueValidator(2000)],
        unique=True
    )
    atualizacao_em_massa = models.BooleanField('Atualização em massa do status de regularidade?', default=False)
    status_atualizacao = models.CharField(
        'Status do processo de atualização',
        max_length=50,
        choices=STATUS_ATUALIZACAO_CHOICES,
        default=STATUS_NENHUMA_ATUALIZACAO_REQUERIDA,
    )

    class Meta:
        verbose_name = 'Ano de análise de regularidade'
        verbose_name_plural = 'Anos de análise de regularidade'

    def __str__(self):
        return f'{self.ano}'


auditlog.register(AnoAnaliseRegularidade)

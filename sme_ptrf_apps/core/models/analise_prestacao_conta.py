from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class AnalisePrestacaoConta(ModeloBase):
    # Status Choice
    STATUS_EM_ANALISE = 'EM_ANALISE'
    STATUS_DEVOLVIDA = 'DEVOLVIDA'
    STATUS_APROVADA = 'APROVADA'
    STATUS_APROVADA_RESSALVA = 'APROVADA_RESSALVA'
    STATUS_REPROVADA = 'REPROVADA'

    STATUS_NOMES = {
        STATUS_EM_ANALISE: 'Em análise',
        STATUS_DEVOLVIDA: 'Devolvida para acertos',
        STATUS_APROVADA: 'Aprovada',
        STATUS_APROVADA_RESSALVA: 'Aprovada com ressalvas',
        STATUS_REPROVADA: 'Reprovada',
    }

    STATUS_CHOICES = (
        (STATUS_EM_ANALISE, STATUS_NOMES[STATUS_EM_ANALISE]),
        (STATUS_DEVOLVIDA, STATUS_NOMES[STATUS_DEVOLVIDA]),
        (STATUS_APROVADA, STATUS_NOMES[STATUS_APROVADA]),
        (STATUS_APROVADA_RESSALVA, STATUS_NOMES[STATUS_APROVADA_RESSALVA]),
        (STATUS_REPROVADA, STATUS_NOMES[STATUS_REPROVADA]),
    )

    prestacao_conta = models.ForeignKey('PrestacaoConta', on_delete=models.CASCADE,
                                        related_name='analises_da_prestacao')

    status = models.CharField(
        'status',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_EM_ANALISE
    )

    devolucao_prestacao_conta = models.ForeignKey(
        'DevolucaoPrestacaoConta',
        on_delete=models.SET_NULL,
        related_name='analises_da_devolucao',
        blank=True, null=True,
    )

    def __str__(self):
        return f"{self.prestacao_conta.periodo} - Análise #{self.pk}"

    class Meta:
        verbose_name = "Análise de prestação de contas"
        verbose_name_plural = "15.0) Análises de prestações de contas"



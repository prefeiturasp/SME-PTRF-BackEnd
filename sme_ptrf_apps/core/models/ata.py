from datetime import datetime

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class Ata(ModeloBase):
    # Tipo de Ata
    ATA_APRESENTACAO = 'APRESENTACAO'
    ATA_RETIFICACAO = 'RETIFICACAO'

    ATA_NOMES = {
        ATA_APRESENTACAO: 'Apresentação',
        ATA_RETIFICACAO: 'Retificação',
    }

    ATA_CHOICES = (
        (ATA_APRESENTACAO, ATA_NOMES[ATA_APRESENTACAO]),
        (ATA_RETIFICACAO, ATA_NOMES[ATA_RETIFICACAO]),
    )

    # Tipo de Reunião
    REUNIAO_ORDINARIA = 'ORDINARIA'
    REUNIAO_EXTRAORDINARIA = 'EXTRAORDINARIA'

    REUNIAO_NOMES = {
        REUNIAO_ORDINARIA: 'Ordinária',
        REUNIAO_EXTRAORDINARIA: 'Extraordinária',
    }

    REUNIAO_CHOICES = (
        (REUNIAO_ORDINARIA, REUNIAO_NOMES[REUNIAO_ORDINARIA]),
        (REUNIAO_EXTRAORDINARIA, REUNIAO_NOMES[REUNIAO_EXTRAORDINARIA]),
    )

    # Convocação
    CONVOCACAO_PRIMEIRA = 'PRIMEIRA'
    CONVOCACAO_SEGUNDA = 'SEGUNDA'

    CONVOCACAO_NOMES = {
        CONVOCACAO_PRIMEIRA: '1ª convocação',
        CONVOCACAO_SEGUNDA: '2ª convocação',
    }

    CONVOCACAO_CHOICES = (
        (CONVOCACAO_PRIMEIRA, CONVOCACAO_NOMES[CONVOCACAO_PRIMEIRA]),
        (CONVOCACAO_SEGUNDA, CONVOCACAO_NOMES[CONVOCACAO_SEGUNDA]),
    )

    # Parecer Choice
    PARECER_APROVADA = 'APROVADA'
    PARECER_REJEITADA = 'REJEITADA'

    PARECER_NOMES = {
        PARECER_APROVADA: 'Aprovada',
        PARECER_REJEITADA: 'Rejeitada',
    }

    PARECER_CHOICES = (
        (PARECER_APROVADA, PARECER_NOMES[PARECER_APROVADA]),
        (PARECER_REJEITADA, PARECER_NOMES[PARECER_REJEITADA]),
    )

    prestacao_conta = models.ForeignKey('PrestacaoConta', on_delete=models.CASCADE, related_name='atas_da_prestacao')

    periodo = models.ForeignKey('Periodo', on_delete=models.PROTECT, related_name='+')

    associacao = models.ForeignKey('Associacao', on_delete=models.PROTECT, related_name='atas_da_associacao')

    tipo_ata = models.CharField(
        'tipo de ata',
        max_length=20,
        choices=ATA_CHOICES,
        default=ATA_APRESENTACAO
    )

    tipo_reuniao = models.CharField(
        'tipo de reunião',
        max_length=20,
        choices=REUNIAO_CHOICES,
        default=REUNIAO_ORDINARIA
    )

    convocacao = models.CharField(
        'convocação',
        max_length=20,
        choices=CONVOCACAO_CHOICES,
        default=CONVOCACAO_PRIMEIRA,
    )

    data_reuniao = models.DateField('data da reunião', blank=True, null=True)

    local_reuniao = models.CharField('local da reunião', max_length=200, blank=True, default='')

    presidente_reuniao = models.CharField('presidente da reunião', max_length=200, blank=True, default='')

    cargo_presidente_reuniao = models.CharField('cargo do presidente da reunião', max_length=200, blank=True,
                                                default='')

    secretario_reuniao = models.CharField('secretario da reunião', max_length=200, blank=True, default='')

    cargo_secretaria_reuniao = models.CharField('cargo da secretária da reunião', max_length=200, blank=True,
                                                default='')

    comentarios = models.TextField('Manifestações, comentários e justificativas', blank=True, default='')

    parecer_conselho = models.CharField(
        'parecer do conselho',
        max_length=20,
        choices=PARECER_CHOICES,
        default=PARECER_APROVADA,
    )

    preenchida_em = models.DateTimeField("Preenchida em", blank=True, null=True)

    @property
    def nome(self):
        return f'Ata de {self.ATA_NOMES[self.tipo_ata]} da prestação de contas'

    @classmethod
    def iniciar(cls, prestacao_conta):
        return Ata.objects.create(
            prestacao_conta=prestacao_conta,
            periodo=prestacao_conta.periodo,
            associacao=prestacao_conta.associacao,
        )

    def __str__(self):
        return f"Ata {self.periodo.referencia} - {self.ATA_NOMES[self.tipo_ata]} - {self.data_reuniao}"

    class Meta:
        verbose_name = "Ata"
        verbose_name_plural = "09.4) Atas"


@receiver(pre_save, sender=Ata)
def ata_pre_save(instance, **kwargs):
    criando_ata = instance._state.adding
    if not criando_ata:
        instance.preenchida_em = datetime.now()

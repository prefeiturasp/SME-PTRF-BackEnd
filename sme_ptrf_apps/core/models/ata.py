import logging

from datetime import datetime

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from sme_ptrf_apps.core.models_abstracts import ModeloBase

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from waffle import get_waffle_flag_model

logger = logging.getLogger(__name__)


class Ata(ModeloBase):
    history = AuditlogHistoryField()

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

    # Status Choice
    STATUS_NAO_GERADO = 'NAO_GERADO'
    STATUS_EM_PROCESSAMENTO = 'EM_PROCESSAMENTO'
    STATUS_CONCLUIDO = 'CONCLUIDO'

    STATUS_NOMES = {
        STATUS_NAO_GERADO: 'Não gerado',
        STATUS_EM_PROCESSAMENTO: 'Em processamento',
        STATUS_CONCLUIDO: 'Geração concluída',
    }

    STATUS_CHOICES = (
        (STATUS_NAO_GERADO, STATUS_NOMES[STATUS_NAO_GERADO]),
        (STATUS_EM_PROCESSAMENTO, STATUS_NOMES[STATUS_EM_PROCESSAMENTO]),
        (STATUS_CONCLUIDO, STATUS_NOMES[STATUS_CONCLUIDO]),
    )

    arquivo_pdf = models.FileField(blank=True, null=True, verbose_name='Relatório em PDF')

    prestacao_conta = models.ForeignKey(
        'PrestacaoConta',
        on_delete=models.CASCADE,
        related_name='atas_da_prestacao',
        blank=True,
        null=True
    )

    periodo = models.ForeignKey('Periodo', on_delete=models.PROTECT, related_name='+')

    associacao = models.ForeignKey('Associacao', on_delete=models.PROTECT, related_name='atas_da_associacao')
    
    composicao = models.ForeignKey(
        'mandatos.Composicao',
        on_delete=models.PROTECT,
        verbose_name="Composição utilizada",
        related_name='atas_da_composicao',
        blank=True,
        null=True
    )
    
    presidente_da_reuniao = models.ForeignKey('Participante', on_delete=models.SET_NULL, related_name='presidente_participante_ata', blank=True, null=True)
    
    secretario_da_reuniao = models.ForeignKey('Participante', on_delete=models.SET_NULL, related_name='secretario_participante_ata', blank=True, null=True)

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

    status_geracao_pdf = models.CharField(
        'status Pdf',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NAO_GERADO
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

    retificacoes = models.TextField('Retificações', blank=True, default='')

    hora_reuniao = models.TimeField("Hora da reunião", default="00:00")

    previa = models.BooleanField("É prévia?", default=False)

    justificativa_repasses_pendentes = models.TextField('Justificativa repasses pendentes', blank=True, default='')
    
    pdf_gerado_previamente = models.BooleanField("PDF gerado previamente", blank=True, default=False, help_text="O PDF já foi gerado e precisa ser regerado quando a ata é editada/apagada")

    @property
    def nome(self):
        return f'Ata de {self.ATA_NOMES[self.tipo_ata]} da prestação de contas'

    @property
    def documento_gerado(self):
        return self.status_geracao_pdf == Ata.STATUS_CONCLUIDO

    @property
    def completa(self):
        from sme_ptrf_apps.core.services.associacoes_service import tem_repasses_pendentes_periodos_ate_agora
        
        flags = get_waffle_flag_model()
        if flags.objects.filter(name='historico-de-membros', everyone=True).exists():
            esta_completa = (
                self.tipo_ata and
                self.tipo_reuniao and
                self.convocacao and
                self.data_reuniao and
                self.local_reuniao and
                self.presidente_da_reuniao and
                self.secretario_da_reuniao and
                self.hora_reuniao
            )

            if tem_repasses_pendentes_periodos_ate_agora(associacao=self.associacao, periodo=self.periodo):
                esta_completa = esta_completa and self.justificativa_repasses_pendentes

            return esta_completa
        else:
            esta_completa = (
                self.tipo_ata and
                self.tipo_reuniao and
                self.convocacao and
                self.data_reuniao and
                self.local_reuniao and
                self.presidente_reuniao and
                self.cargo_presidente_reuniao and
                self.secretario_reuniao and
                self.cargo_secretaria_reuniao and
                self.hora_reuniao
            )

            if tem_repasses_pendentes_periodos_ate_agora(associacao=self.associacao, periodo=self.periodo):
                esta_completa = esta_completa and self.justificativa_repasses_pendentes

            presidente_presente = self.presentes_na_ata.filter(nome=self.presidente_reuniao).exists()
            esta_completa = esta_completa and presidente_presente

            secretario_presente = self.presentes_na_ata.filter(nome=self.secretario_reuniao).exists()
            esta_completa = esta_completa and secretario_presente
    
            return esta_completa

    @classmethod
    def iniciar(cls, prestacao_conta, retificacao=False):
        logger.info(f'Iniciando Ata PC={prestacao_conta}, Retificação={retificacao}...')

        previa_ata = Ata.objects.filter(
            associacao=prestacao_conta.associacao,
            periodo=prestacao_conta.periodo,
            prestacao_conta=prestacao_conta if retificacao else None,
            tipo_ata='RETIFICACAO' if retificacao else 'APRESENTACAO',
            previa=True
        ).first()

        if previa_ata:
            previa = False
            if retificacao and prestacao_conta.status == 'DEVOLVIDA':
                # Atas de retificação criadas enquanto a PC esta devolvida são apenas prévias.
                previa = True
            logger.info(f'Encontrada uma prévia da ata. previa={previa}')
            if not retificacao:
                previa_ata.prestacao_conta = prestacao_conta
            previa_ata.previa = previa
            previa_ata.save()
            return previa_ata
        else:
            previa = False
            if retificacao and prestacao_conta.status == 'DEVOLVIDA':
                # Atas de retificação criadas enquanto a PC esta devolvida são apenas prévias.
                previa = True
            logger.info(f'Não encontrada prévia de ata. Criando nova ata. previa={previa}')
            return Ata.objects.create(
                prestacao_conta=prestacao_conta,
                periodo=prestacao_conta.periodo,
                associacao=prestacao_conta.associacao,
                tipo_ata='RETIFICACAO' if retificacao else 'APRESENTACAO',
                previa=previa
            )

    @classmethod
    def iniciar_previa(cls, associacao, periodo, retificacao=False):
        logger.info(f'Criando prévia de ata. associacao={associacao}, periodo={periodo}, retificacao={retificacao}')
        return Ata.objects.create(
            prestacao_conta=None,
            periodo=periodo,
            associacao=associacao,
            tipo_ata='RETIFICACAO' if retificacao else 'APRESENTACAO',
            previa=True,
        )

    def __str__(self):
        return f"Ata {self.periodo.referencia} - {self.ATA_NOMES[self.tipo_ata]} - {self.data_reuniao}"

    def arquivo_pdf_iniciar(self):
        self.status_geracao_pdf = self.STATUS_EM_PROCESSAMENTO
        self.save()

    def arquivo_pdf_concluir(self):
        self.pdf_gerado_previamente = True
        self.status_geracao_pdf = self.STATUS_CONCLUIDO
        self.save()

    def arquivo_pdf_nao_gerado(self):
        self.status_geracao_pdf = self.STATUS_NAO_GERADO
        self.save()

    class Meta:
        verbose_name = "Ata"
        verbose_name_plural = "09.4) Atas"


@receiver(pre_save, sender=Ata)
def ata_pre_save(instance, **kwargs):
    criando_ata = instance._state.adding
    if not criando_ata:
        instance.preenchida_em = datetime.now()


auditlog.register(Ata)

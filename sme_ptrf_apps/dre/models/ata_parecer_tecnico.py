from datetime import datetime

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from sme_ptrf_apps.core.models_abstracts import ModeloBase

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
import logging

logger = logging.getLogger(__name__)


class AtaParecerTecnico(ModeloBase):
    history = AuditlogHistoryField()

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

    periodo = models.ForeignKey('core.Periodo', on_delete=models.PROTECT,
                                related_name='atas_parecer_tecnico_dre_do_periodo')

    dre = models.ForeignKey('core.Unidade', on_delete=models.PROTECT, related_name='atas_parecer_tecnico_da_dre',
                            to_field="codigo_eol", blank=True, null=True, limit_choices_to={'tipo_unidade': 'DRE'})

    status_geracao_pdf = models.CharField(
        'status Pdf',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NAO_GERADO
    )

    numero_ata = models.IntegerField('Numero da ata', blank=True, null=True)

    data_reuniao = models.DateField('Data da reunião', blank=True, null=True)

    hora_reuniao = models.TimeField("Hora da reunião", default="00:00")

    local_reuniao = models.CharField('Local da reunião', max_length=200, blank=True, default='')

    comentarios = models.TextField('Manifestações, comentários e justificativas', blank=True, default='')

    preenchida_em = models.DateTimeField("Preenchida em", blank=True, null=True)

    numero_portaria = models.IntegerField('Numero da portaria', blank=True, null=True)

    data_portaria = models.DateField('Data da portaria', blank=True, null=True)

    consolidado_dre = models.ForeignKey('ConsolidadoDRE', on_delete=models.CASCADE,
                                        related_name='atas_de_parecer_tecnico_do_consolidado_dre',
                                        blank=True, null=True)

    sequencia_de_publicacao = models.IntegerField('Sequência de publicação', blank=True, null=True)

    sequencia_de_retificacao = models.IntegerField('Sequência de retificação', blank=True, null=True)


    @classmethod
    def criar_ou_retornar_ata_sem_consolidado_dre(cls, dre, periodo, sequencia_de_publicacao, sequencia_de_retificacao):
        ata, _ = cls.objects.get_or_create(
            dre=dre,
            periodo=periodo,
            sequencia_de_publicacao=sequencia_de_publicacao,
            sequencia_de_retificacao=sequencia_de_retificacao,
            defaults={'dre': dre, 'periodo': periodo, 'sequencia_de_publicacao': sequencia_de_publicacao, 'sequencia_de_retificacao': sequencia_de_retificacao},
        )

        return ata

    @classmethod
    def iniciar(cls, dre, periodo):
        ata_atual = AtaParecerTecnico.objects.filter(
            dre=dre,
            periodo=periodo
        ).first()

        if ata_atual:
            logger.info(f"Ata de parecer técnico: {ata_atual.uuid} será excluida")
            ata_atual.delete()

        logger.info(f"Gerando nova ata...")
        ata = AtaParecerTecnico.objects.create(
            dre=dre,
            periodo=periodo
        )

        logger.info(f"Ata de parecer técnico gerada: {ata.uuid}")
        return ata

    def __str__(self):
        return f"<DRE: {self.dre} Periodo: {self.periodo}>"

    class Meta:
        verbose_name = "Ata de Parecer Tecnico"
        verbose_name_plural = "Atas de Parecer Tecnicos"

    def arquivo_pdf_iniciar(self):
        self.status_geracao_pdf = self.STATUS_EM_PROCESSAMENTO
        self.save(update_fields=['status_geracao_pdf'])

    def arquivo_pdf_concluir(self):
        self.status_geracao_pdf = self.STATUS_CONCLUIDO
        self.save(update_fields=['status_geracao_pdf'])

    def arquivo_pdf_nao_gerado(self):
        self.status_geracao_pdf = self.STATUS_NAO_GERADO
        self.save(update_fields=['status_geracao_pdf'])

    def atrelar_consolidado_dre(self, consolidado_dre):
        self.consolidado_dre = consolidado_dre
        self.save(update_fields=['consolidado_dre'])
        return self


@receiver(pre_save, sender=AtaParecerTecnico)
def ata_pre_save(instance, **kwargs):
    criando_ata = instance._state.adding
    if not criando_ata:
        instance.preenchida_em = datetime.now()


auditlog.register(AtaParecerTecnico)


from django.db import models
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from sme_ptrf_apps.core.models_abstracts import ModeloBase

class AtaPaa(ModeloBase):
    history = AuditlogHistoryField()

    ATA_APRESENTACAO = 'APRESENTACAO'

    ATA_NOMES = {
        ATA_APRESENTACAO: 'Apresentação',
    }

    ATA_CHOICES = (
        (ATA_APRESENTACAO, ATA_NOMES[ATA_APRESENTACAO]),
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
        PARECER_APROVADA: 'Aprovado',
        PARECER_REJEITADA: 'Rejeitado',
    }

    PARECER_CHOICES = (
        (PARECER_APROVADA, PARECER_NOMES[PARECER_APROVADA]),
        (PARECER_REJEITADA, PARECER_NOMES[PARECER_REJEITADA]),
    )

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
    
    arquivo_pdf = models.FileField(blank=True, null=True, verbose_name='Ata PAA em PDF')
    
    paa = models.ForeignKey('Paa', on_delete=models.CASCADE, related_name='atas_da_paa')
    
    composicao = models.ForeignKey(
          'mandatos.Composicao',
          on_delete=models.PROTECT,
          verbose_name="Composição utilizada",
          related_name='atas_paa_da_composicao',
          blank=True,
          null=True
      )
    
    presidente_da_reuniao = models.ForeignKey('paa.ParticipanteAtaPaa', on_delete=models.SET_NULL, related_name='presidente_participante_ata_paa', blank=True, null=True)
      
    secretario_da_reuniao = models.ForeignKey('paa.ParticipanteAtaPaa', on_delete=models.SET_NULL, related_name='secretario_participante_ata_paa', blank=True, null=True)
    
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
    
    comentarios = models.TextField('Manifestações, comentários e justificativas', blank=True, default='')

    parecer_conselho = models.CharField(
        'parecer do conselho',
        max_length=20,
        choices=PARECER_CHOICES,
        default=PARECER_APROVADA,
    )
    
    preenchida_em = models.DateTimeField("Preenchida em", blank=True, null=True)
    
    hora_reuniao = models.TimeField("Hora da reunião", default="00:00")

    previa = models.BooleanField("É prévia?", default=False)
    
    justificativa = models.TextField('Justificativa de rejeição', blank=True, default='')
      
    pdf_gerado_previamente = models.BooleanField("PDF gerado previamente", blank=True, default=False, help_text="O PDF já foi gerado e precisa ser regerado quando a ata é editada/apagada")
    
    @property
    def nome(self):
      return f'Ata de {self.ATA_NOMES[self.tipo_ata]} do PAA'
    
    @property
    def documento_gerado(self):
      return self.status_geracao_pdf == self.STATUS_CONCLUIDO
    
    def __str__(self):
      return f"Ata PAA {self.paa.periodo_paa.referencia} - {self.ATA_NOMES[self.tipo_ata]} - {self.data_reuniao}"
  
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

    @classmethod
    def iniciar(cls, paa):
        ata_paa = cls.objects.filter(
            paa=paa,
            tipo_ata=cls.ATA_APRESENTACAO
        ).first()

        if ata_paa:
            return ata_paa

        return cls.objects.create(
            paa=paa,
            tipo_ata=cls.ATA_APRESENTACAO
        )

    class Meta:
        verbose_name = "Ata PAA"
        verbose_name_plural = "Atas PAA"
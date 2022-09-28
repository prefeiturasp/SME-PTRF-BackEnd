from django.db import models
from ...core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class ConsolidadoDRE(ModeloBase):
    history = AuditlogHistoryField()

    STATUS_NAO_GERADOS = 'NAO_GERADOS'
    STATUS_GERADOS_PARCIAIS = 'GERADOS_PARCIAIS'
    STATUS_GERADOS_TOTAIS = 'GERADOS_TOTAIS'
    STATUS_EM_PROCESSAMENTO = 'EM_PROCESSAMENTO'

    STATUS_NOMES = {
        STATUS_NAO_GERADOS: 'Documentos não gerados',
        STATUS_GERADOS_PARCIAIS: 'Documentos parciais gerados',
        STATUS_GERADOS_TOTAIS: 'Documentos finais gerados',
        STATUS_EM_PROCESSAMENTO: 'Documentos em processamento'
    }

    STATUS_CHOICES = (
        (STATUS_NAO_GERADOS, STATUS_NOMES[STATUS_NAO_GERADOS]),
        (STATUS_GERADOS_PARCIAIS, STATUS_NOMES[STATUS_GERADOS_PARCIAIS]),
        (STATUS_GERADOS_TOTAIS, STATUS_NOMES[STATUS_GERADOS_TOTAIS]),
        (STATUS_EM_PROCESSAMENTO, STATUS_NOMES[STATUS_EM_PROCESSAMENTO]),
    )

    # Versao Choice
    VERSAO_FINAL = 'FINAL'
    VERSAO_PREVIA = 'PREVIA'

    VERSAO_NOMES = {
        VERSAO_FINAL: 'final',
        VERSAO_PREVIA: 'prévia',
    }

    VERSAO_CHOICES = (
        (VERSAO_FINAL, VERSAO_NOMES[VERSAO_FINAL]),
        (VERSAO_PREVIA, VERSAO_NOMES[VERSAO_PREVIA]),
    )

    STATUS_SME_NAO_PUBLICADO = 'NAO_PUBLICADO'
    STATUS_SME_PUBLICADO = 'PUBLICADO'
    STATUS_SME_EM_ANALISE = 'EM_ANALISE'
    STATUS_SME_DEVOLVIDO = 'DEVOLVIDO'
    STATUS_SME_ANALISADO = 'ANALISADO'

    STATUS_SME_NOMES = {
        STATUS_SME_NAO_PUBLICADO: 'Não publicado',
        STATUS_SME_PUBLICADO: 'Publicado',
        STATUS_SME_EM_ANALISE: 'Em análise',
        STATUS_SME_DEVOLVIDO: 'Devolvido',
        STATUS_SME_ANALISADO: 'Analisado'
    }

    STATUS_SME_CHOICES = (
        (STATUS_SME_NAO_PUBLICADO, STATUS_SME_NOMES[STATUS_SME_NAO_PUBLICADO]),
        (STATUS_SME_PUBLICADO, STATUS_SME_NOMES[STATUS_SME_PUBLICADO]),
        (STATUS_SME_EM_ANALISE, STATUS_SME_NOMES[STATUS_SME_EM_ANALISE]),
        (STATUS_SME_DEVOLVIDO, STATUS_SME_NOMES[STATUS_SME_DEVOLVIDO]),
        (STATUS_SME_ANALISADO, STATUS_SME_NOMES[STATUS_SME_ANALISADO]),
    )

    dre = models.ForeignKey('core.Unidade', on_delete=models.PROTECT, related_name='consolidados_dre_da_dre',
                            to_field="codigo_eol", blank=True, null=True, limit_choices_to={'tipo_unidade': 'DRE'})

    periodo = models.ForeignKey('core.Periodo', on_delete=models.PROTECT,
                                related_name='consolidados_dre_do_periodo')

    eh_parcial = models.BooleanField("É parcial?", default=True)

    sequencia_de_publicacao = models.IntegerField('Sequência de publicação', blank=True, null=True)

    status = models.CharField(
        'status',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NAO_GERADOS
    )

    versao = models.CharField(
        'versão',
        max_length=20,
        choices=VERSAO_CHOICES,
        default=VERSAO_FINAL
    )

    status_sme = models.CharField(
        'status SME',
        max_length=30,
        choices=STATUS_SME_CHOICES,
        default=STATUS_SME_NAO_PUBLICADO
    )

    data_publicacao = models.DateField('Publicado em', blank=True, null=True)

    pagina_publicacao = models.CharField('Página publicacao', max_length=50, blank=True, default='')

    class Meta:
        verbose_name = 'Consolidado DRE'
        verbose_name_plural = 'Consolidados DREs'
        unique_together = ['periodo', 'dre', 'sequencia_de_publicacao']
        ordering = ['-sequencia_de_publicacao']

    def __str__(self):
        if self.status == self.STATUS_EM_PROCESSAMENTO:
            status_str = 'Documentos sendo gerados. Aguarde.'
        elif self.versao == self.VERSAO_PREVIA:
            status_str = f"Prévia gerada em {self.alterado_em.strftime('%d/%m/%Y às %H:%M')}"
        elif self.status == self.STATUS_NAO_GERADOS:
            status_str = 'Documentos não gerados'
        else:
            status_str = f"Documentos {'finais' if self.status == 'GERADOS_TOTAIS' else 'parciais'} " \
                         f"gerados dia {self.alterado_em.strftime('%d/%m/%Y às %H:%M')}"

        return status_str

    @property
    def referencia(self):
        return "Única" if self.sequencia_de_publicacao == 0 else f'Parcial #{self.sequencia_de_publicacao}'

    @classmethod
    def criar_ou_retornar_consolidado_dre(cls, dre, periodo, sequencia_de_publicacao):

        # Verificando se existe alguma instancia criada antes da modificação do incremental
        consolidado_dre = cls.objects.filter(dre=dre, periodo=periodo, sequencia_de_publicacao__isnull=True).last()

        if consolidado_dre:
            consolidado_dre.dre = dre
            consolidado_dre.periodo = periodo
            consolidado_dre.sequencia_de_publicacao = sequencia_de_publicacao
            consolidado_dre.save()
        else:
            consolidado_dre, _ = cls.objects.get_or_create(
                dre=dre,
                periodo=periodo,
                sequencia_de_publicacao=sequencia_de_publicacao,
                defaults={'dre': dre, 'periodo': periodo, 'sequencia_de_publicacao': sequencia_de_publicacao, },
            )

        return consolidado_dre

    def passar_para_status_em_processamento(self):
        self.status = self.STATUS_EM_PROCESSAMENTO
        self.save()
        return self

    def passar_para_status_gerado(self, parcial):
        self.status = self.STATUS_GERADOS_TOTAIS if not parcial else self.STATUS_GERADOS_PARCIAIS
        self.save()
        return self

    def atribuir_versao(self, previa):
        self.versao = self.VERSAO_PREVIA if previa else self.VERSAO_FINAL
        self.save()
        return self

    def atribuir_se_eh_parcial(self, parcial):
        self.eh_parcial = parcial
        self.save()
        return self

    def get_valor_status_choice(self):
        return self.get_status_display()

    def marcar_status_sme_como_publicado(self, data_publicacao, pagina_publicacao):
        self.status_sme = self.STATUS_SME_PUBLICADO
        self.data_publicacao = data_publicacao
        self.pagina_publicacao = pagina_publicacao
        self.save()
        return self

    def marcar_status_sme_como_nao_publicado(self):
        self.status_sme = self.STATUS_SME_NAO_PUBLICADO
        self.data_publicacao = None
        self.pagina_publicacao = ''
        self.save()
        return self


auditlog.register(ConsolidadoDRE)

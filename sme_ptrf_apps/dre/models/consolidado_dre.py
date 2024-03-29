import logging

from django.db import models

from ...core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.db import transaction
from ..models import RelatorioConsolidadoDRE
from django.contrib.auth import get_user_model
from datetime import date


logger = logging.getLogger(__name__)


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

    data_de_inicio_da_analise = models.DateField('Data de início da análise (data de recebimento)', blank=True, null=True)

    responsavel_pela_analise = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Responsável',
        related_name='consolidado_dre_usuario_responsavel'
    )

    analise_atual = models.ForeignKey('AnaliseConsolidadoDre', on_delete=models.SET_NULL,
                                      related_name='consolidado_dre_da_analise_atual',
                                      blank=True, null=True)

    sequencia_de_retificacao = models.IntegerField('Sequência de retificação', blank=True, null=True, default=0)

    consolidado_retificado = models.ForeignKey(
        'ConsolidadoDRE', on_delete=models.PROTECT,
        related_name='retificacoes',
        blank=True, null=True,
        default=None,
    )

    motivo_retificacao = models.TextField('Motivo de retificação', blank=True, null=True)
    gerou_uma_retificacao = models.BooleanField("Já gerou uma retificação?", default=False)

    pcs_do_consolidado = models.ManyToManyField(
        'core.PrestacaoConta',
        related_name='consolidados_dre_da_prestacao_de_contas',
        blank=True,
    )

    def vincular_pc_ao_consolidado(self, pc):
        logger.info(f'Vinculando PC {pc} ao consolidado #{self.id}')
        pc.atrelar_consolidado_dre(self)
        pc.save()
        self.pcs_do_consolidado.add(pc)

    def desvincular_pc_do_consolidado(self, pc):
        logger.info(f'Desvinculando PC {pc} do consolidado #{self.id}')
        self.pcs_do_consolidado.remove(pc)

    @property
    def foi_publicado(self):
        return self.status_sme == self.STATUS_SME_PUBLICADO

    @property
    def exibe_botao_retificar(self):
        return True if self.gerou_uma_retificacao else self.foi_publicado

    @property
    def permite_retificacao(self):
        result = {
            "permite": True,
            "tooltip": ''
        }

        if self.gerou_uma_retificacao:
            possui_retificacoes_nao_geradas = False

            for retificacao in self.retificacoes.all():
                if not retificacao.retificacao_gerada:
                    possui_retificacoes_nao_geradas = True

            if possui_retificacoes_nao_geradas:
                result["permite"] = False
                result["tooltip"] = "As PCs habilitadas para retificação estão disponíveis na edição" \
                                    " da retificação desta publicação."
            elif not self.prestacoes_de_conta_do_consolidado_dre.all():
                result["permite"] = False
                result["tooltip"] = "Esta publicação não possui PCs disponíveis para retificação"

        return result

    @property
    def eh_retificacao(self):
        return self.consolidado_retificado is not None

    @property
    def eh_publicacao_unica(self):
        if self.eh_parcial:
            return False

        return True


    @property
    def habilita_geracao(self):
        if self.eh_retificacao:
            if self.versao == self.VERSAO_FINAL and not self.retificacao_gerada:
                return True
            else:
                return False
        else:
            return False

    @property
    def retificacao_gerada(self):
        if self.eh_retificacao and self.laudas_do_consolidado_dre.all():
            return True

        return False


    class Meta:
        verbose_name = 'Consolidado DRE'
        verbose_name_plural = 'Consolidados DREs'
        unique_together = ['periodo', 'dre', 'sequencia_de_publicacao', 'sequencia_de_retificacao']
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
        if self.eh_retificacao:
            return f"Retificação da publicação de {self.consolidado_retificado.data_publicacao.strftime('%d/%m/%Y') if self.consolidado_retificado.data_publicacao else ''}"
        else:
            return "Única" if self.sequencia_de_publicacao == 0 else f'Parcial #{self.sequencia_de_publicacao}'


    @property
    def get_data_publicacao_do_consolidado_original(self):
        if self.eh_retificacao:
            return self.consolidado_retificado.data_publicacao

        return None


    @classmethod
    def criar_ou_retornar_consolidado_dre(cls, dre, periodo, sequencia_de_publicacao, sequencia_de_retificacao=0):

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
                sequencia_de_retificacao=sequencia_de_retificacao,
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
        self.desfazer_analise_atual()
        self.status_sme = self.STATUS_SME_PUBLICADO
        self.data_publicacao = data_publicacao
        self.pagina_publicacao = pagina_publicacao
        self.data_de_inicio_da_analise = None
        self.responsavel_pela_analise = None
        self.save()
        return self

    def marcar_status_sme_como_nao_publicado(self):
        self.desfazer_analise_atual()
        self.status_sme = self.STATUS_SME_NAO_PUBLICADO
        self.data_publicacao = None
        self.pagina_publicacao = ''
        self.save()
        return self

    def marcar_status_sme_como_em_analise(self, usuario):
        self.status_sme = self.STATUS_SME_EM_ANALISE
        self.data_de_inicio_da_analise = date.today()
        self.responsavel_pela_analise = usuario
        self.save()
        return self

    def pode_reabrir(self):
        if self.status_sme == self.STATUS_SME_NAO_PUBLICADO:
            return True

        return False

    def permite_edicao(self):
        if self.status_sme == self.STATUS_SME_EM_ANALISE:
            return True

        return False

    def documentos_detalhamento(self, analise_atual):
        from ..models import DocumentoAdicional
        from ..models import AnaliseDocumentoConsolidadoDre

        lista_documentos = []

        relatorios_consolidados_dre = self.relatorios_consolidados_dre_do_consolidado_dre.all()

        # for utilizado para casos que sejam relatórios por conta
        for relatorio_dre in relatorios_consolidados_dre:
            nome = ""
            if relatorio_dre.tipo_conta:
                nome = f"Demonstrativo da Execução Físico-Financeira - Conta {relatorio_dre.tipo_conta}"
            else:
                nome = "Demonstrativo da Execução Físico-Financeira"

            analise_documento_consolidado_dre = None
            if analise_atual:
                analise_documento_consolidado_dre = AnaliseDocumentoConsolidadoDre.objects.filter(
                    analise_consolidado_dre=analise_atual,
                    relatorio_consolidao_dre=relatorio_dre
                ).first()
            dado_relatorio = {
                "uuid": f"{relatorio_dre.uuid}",
                "nome": nome,
                "exibe_acoes": True,
                "analise_documento_consolidado_dre": {
                    'detalhamento': analise_documento_consolidado_dre.detalhamento if analise_documento_consolidado_dre else None,
                    'resultado': analise_documento_consolidado_dre.resultado if analise_documento_consolidado_dre else None,
                    'uuid': analise_documento_consolidado_dre.uuid if analise_documento_consolidado_dre else None,
                    'copiado': analise_documento_consolidado_dre.copiado if analise_documento_consolidado_dre else None,
                },
                'tipo_documento': 'RELATORIO_CONSOLIDADO'
            }

            lista_documentos.append(dado_relatorio)

        ata_parecer_tecnico = self.atas_de_parecer_tecnico_do_consolidado_dre.first()
        if ata_parecer_tecnico:

            analise_documento_consolidado_dre = None
            if analise_atual:
                analise_documento_consolidado_dre = AnaliseDocumentoConsolidadoDre.objects.filter(
                    analise_consolidado_dre=analise_atual,
                    ata_parecer_tecnico=ata_parecer_tecnico
                ).first()

            dado_ata = {
                "uuid": f"{ata_parecer_tecnico.uuid}",
                "nome": "Parecer Técnico Conclusivo",
                "exibe_acoes": True,
                "analise_documento_consolidado_dre": {
                    'detalhamento': analise_documento_consolidado_dre.detalhamento if analise_documento_consolidado_dre else None,
                    'resultado': analise_documento_consolidado_dre.resultado if analise_documento_consolidado_dre else None,
                    'uuid': analise_documento_consolidado_dre.uuid if analise_documento_consolidado_dre else None,
                    'copiado': analise_documento_consolidado_dre.copiado if analise_documento_consolidado_dre else None,
                },
                'tipo_documento': 'ATA_PARECER_TECNICO'
            }

            lista_documentos.append(dado_ata)

        documentos_adicionais = DocumentoAdicional.objects.all()
        for documento in documentos_adicionais:
            analise_documento_consolidado_dre = None
            if analise_atual:
                analise_documento_consolidado_dre = AnaliseDocumentoConsolidadoDre.objects.filter(
                    analise_consolidado_dre=analise_atual,
                    documento_adicional=documento
                ).first()

            dado_documento = {
                "uuid": f"{documento.uuid}",
                "nome": documento.nome,
                "exibe_acoes": False,
                "analise_documento_consolidado_dre": {
                    'detalhamento': analise_documento_consolidado_dre.detalhamento if analise_documento_consolidado_dre else None,
                    'resultado': analise_documento_consolidado_dre.resultado if analise_documento_consolidado_dre else None,
                    'uuid': analise_documento_consolidado_dre.uuid if analise_documento_consolidado_dre else None,
                    'copiado': analise_documento_consolidado_dre.copiado if analise_documento_consolidado_dre else None,
                },
                'tipo_documento': 'DOCUMENTO_ADICIONAL'
            }

            lista_documentos.append(dado_documento)

        return lista_documentos

    def remove_publicacao_pcs(self):
        prestacoes = self.prestacoes_de_conta_do_consolidado_dre.all()

        for prestacao in prestacoes:
            logger.info(f"Passando a prestação de contas para não publicada: {prestacao.uuid}")
            prestacao.publicada = False
            prestacao.save()

    def apaga_relatorio_dre_versao_consolidada(self):
        versao_consolidada = RelatorioConsolidadoDRE.VERSAO_CONSOLIDADA
        relatorio = RelatorioConsolidadoDRE.objects.filter(
            dre=self.dre,
            periodo=self.periodo,
            versao=versao_consolidada
        ).first()

        if relatorio:
            logger.info(f"O relatorio da dre {relatorio} será apagado")
            relatorio.delete()

    def desfazer_analise_atual(self):
        self.analise_atual = None
        self.save()

    @transaction.atomic
    def reabrir_consolidado(self):
        logger.info(f'Apagando o consolidado dre de uuid {self.uuid}.')

        try:
            self.remove_publicacao_pcs()
            self.apaga_relatorio_dre_versao_consolidada()
            self.delete()
            logger.info(f'Consolidado dre de uuid {self.uuid} foi apagado.')
            return True
        except Exception as e:
            logger.error(f'Houve algum erro ao tentar apagar o consolidado dre de uuid {self.uuid}.')
            logger.error(f'{e}')
            return False

    def devolver_consolidado(self, data_limite, username=None):
        from sme_ptrf_apps.dre.services import RelatorioDevolucaoAcertos

        self.status_sme = self.STATUS_SME_DEVOLVIDO
        for analise_documento in self.analise_atual.analises_de_documentos_da_analise_do_consolidado.all():
            analise_documento.copiado = True
            analise_documento.save()
        self.analise_atual.devolucao(data_limite)
        self.save()

        if username:
            relatorio = RelatorioDevolucaoAcertos(
                analise_consolidado=self.analise_atual,
                username=username,
                previa=False
            )

            relatorio.gerar_arquivo_relatorio_devolucao_acertos()

        logging.info(f'Consolidado devolvido com a data_limite {data_limite}.')

        self.notificar_devolucao()
        return self

    def notificar_devolucao(self):
        from sme_ptrf_apps.dre.services.dre_service import DreService
        dre_service = DreService(dre=self.dre)
        dre_service.notificar_devolucao_consolidado(consolidado_dre=self)

    @transaction.atomic
    def analisar_consolidado(self, usuario):
        from ..models.analise_consolidado_dre import AnaliseConsolidadoDre
        from ..services import AnaliseConsolidadoDreService
        try:
            if not self.analise_atual and len(self.analises_do_consolidado_dre.all()) > 0:
                self.analise_atual = self.analises_do_consolidado_dre.last()
                self.marcar_status_sme_como_em_analise(usuario)
                return self

            analise_anterior = self.analise_atual
            analise_atual = AnaliseConsolidadoDre.objects.create(consolidado_dre=self)

            self.marcar_status_sme_como_em_analise(usuario)
            self.analise_atual = analise_atual
            if analise_anterior:
                self.analise_atual.copiado = True
                self.analise_anterior = analise_anterior
                self.analise_anterior.data_retorno_analise = date.today()
                self.analise_anterior.save()
                self.analise_atual.save()
                AnaliseConsolidadoDreService(
                    analise_origem=self.analise_anterior,
                    analise_destino=self.analise_atual,
                ).copia_documentos_consolidado_entre_analises()

            self.analise_atual.save()
            self.save()

            return self
        except Exception as e:
            logger.error(f'Houve algum erro ao tentar analisar o consolidado dre de uuid {self.uuid}.')
            logger.error(f'{e}')
            return False

    @transaction.atomic
    def concluir_analise_consolidado(self, usuario):
        try:
            self.desfazer_analise_atual()
            self.status_sme = self.STATUS_SME_ANALISADO
            self.responsavel_pela_analise = usuario
            self.save()
            return self
        except Exception as e:
            logger.error(f'Houve algum erro ao tentar concluir a análise do consolidado dre de uuid {self.uuid}.')
            logger.error(f'{e}')
            return False

    def pcs_vinculadas_ao_consolidado(self):
        pcs = self.pcs_do_consolidado.all().order_by('associacao__unidade__tipo_unidade', 'associacao__unidade__nome')
        lista_pcs = []

        # É necessário que essas validações sejam feitas aqui, pois cada tipo de consolidado tem um comportamento especifico

        if self.consolidado_retificado is None and not self.gerou_uma_retificacao:
            # Consolidado original que não possui retificacoes

            for pc in pcs:
                pc_em_retificacao = False
                tooltip_nao_pode_retificar = None

                dado = {
                    "uuid": f"{pc.uuid}",
                    "unidade_eol": pc.associacao.unidade.codigo_eol,
                    "unidade_nome": pc.associacao.unidade.nome,
                    "unidade_tipo_unidade": pc.associacao.unidade.tipo_unidade,
                    "pc_em_retificacao": pc_em_retificacao,
                    "tooltip_nao_pode_retificar": tooltip_nao_pode_retificar
                }

                lista_pcs.append(dado)

        elif self.consolidado_retificado is None and self.gerou_uma_retificacao:
            # Consolidado original que possui retificações

            for pc in pcs:
                pc_em_retificacao = False if pc in self.prestacoes_de_conta_do_consolidado_dre.all() else True
                tooltip_nao_pode_retificar = None if pc in self.prestacoes_de_conta_do_consolidado_dre.all() \
                    else "Esta PC foi retificada em outra publicação."

                dado = {
                    "uuid": f"{pc.uuid}",
                    "unidade_eol": pc.associacao.unidade.codigo_eol,
                    "unidade_nome": pc.associacao.unidade.nome,
                    "unidade_tipo_unidade": pc.associacao.unidade.tipo_unidade,
                    "pc_em_retificacao": pc_em_retificacao,
                    "tooltip_nao_pode_retificar": tooltip_nao_pode_retificar
                }

                lista_pcs.append(dado)

        elif self.consolidado_retificado and not self.gerou_uma_retificacao:
            # Retificação original que não possui retificações

            pc_em_retificacao = False
            tooltip_nao_pode_retificar = None

            for pc in pcs:
                dado = {
                    "uuid": f"{pc.uuid}",
                    "unidade_eol": pc.associacao.unidade.codigo_eol,
                    "unidade_nome": pc.associacao.unidade.nome,
                    "unidade_tipo_unidade": pc.associacao.unidade.tipo_unidade,
                    "pc_em_retificacao": pc_em_retificacao,
                    "tooltip_nao_pode_retificar": tooltip_nao_pode_retificar
                }

                lista_pcs.append(dado)

        elif self.consolidado_retificado and self.gerou_uma_retificacao:
            # Retificação original que possui retificacoes

            for pc in pcs:
                pc_em_retificacao = False if pc in self.prestacoes_de_conta_do_consolidado_dre.all() else True
                tooltip_nao_pode_retificar = None if pc in self.prestacoes_de_conta_do_consolidado_dre.all() \
                    else "Esta PC foi retificada em outra publicação."

                dado = {
                    "uuid": f"{pc.uuid}",
                    "unidade_eol": pc.associacao.unidade.codigo_eol,
                    "unidade_nome": pc.associacao.unidade.nome,
                    "unidade_tipo_unidade": pc.associacao.unidade.tipo_unidade,
                    "pc_em_retificacao": pc_em_retificacao,
                    "tooltip_nao_pode_retificar": tooltip_nao_pode_retificar
                }

                lista_pcs.append(dado)

        return lista_pcs

    def pcs_retificaveis(self):
        if self.eh_retificacao:
            return self.consolidado_retificado.prestacoes_de_conta_do_consolidado_dre.all()
        else:
            return self.prestacoes_de_conta_do_consolidado_dre.all()

    def pcs_em_retificacao(self):
        lista_pcs = self.prestacoes_de_conta_do_consolidado_dre.all().order_by(
            "associacao__unidade__tipo_unidade", "associacao__unidade__nome"
        )

        lista_ordenada = sorted(lista_pcs, key=lambda pc: pc.pode_desfazer_retificacao)

        return lista_ordenada

    def get_proxima_sequencia_retificacao(self):
        ultima_sequencia = ConsolidadoDRE.objects.filter(dre=self.dre).filter(periodo=self.periodo).order_by(
            'sequencia_de_retificacao').last()

        return ultima_sequencia.sequencia_de_retificacao + 1


auditlog.register(ConsolidadoDRE)

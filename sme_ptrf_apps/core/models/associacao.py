import datetime
from django.db import models
from sme_ptrf_apps.core.models.conta_associacao import ContaAssociacao

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from .validators import cnpj_validation
from ..choices import MembroEnum, FiltroInformacoesAssociacao
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

# necessario para utilizacao da funcao sorted
from .periodo import Periodo

from django.core.exceptions import ValidationError
from django.db.models import Q

class AssociacoesAtivasManager(models.Manager):
    def get_queryset(self):
        return super(AssociacoesAtivasManager, self).get_queryset().exclude(cnpj="")


class Associacao(ModeloIdNome):
    history = AuditlogHistoryField()

    # Tags de informações
    TAG_ENCERRADA = {"id": "1", "nome": "Associação encerrada", "descricao": "A associação foi encerrada."}

    # Status do Presidente
    STATUS_PRESIDENTE_PRESENTE = 'PRESENTE'
    STATUS_PRESIDENTE_AUSENTE = 'AUSENTE'

    STATUS_PRESIDENTE_NOMES = {
        STATUS_PRESIDENTE_PRESENTE: 'Presente',
        STATUS_PRESIDENTE_AUSENTE: 'Ausente',
    }

    STATUS_PRESIDENTE_CHOICES = (
        (STATUS_PRESIDENTE_PRESENTE, STATUS_PRESIDENTE_NOMES[STATUS_PRESIDENTE_PRESENTE]),
        (STATUS_PRESIDENTE_AUSENTE, STATUS_PRESIDENTE_NOMES[STATUS_PRESIDENTE_AUSENTE]),
    )

    # Status valores reprogramados iniciais
    STATUS_VALORES_REPROGRAMADOS_NAO_FINALIZADO = "NAO_FINALIZADO"
    STATUS_VALORES_REPROGRAMADOS_EM_CONFERENCIA_DRE = "EM_CONFERENCIA_DRE"
    STATUS_VALORES_REPROGRAMADOS_EM_CORRECAO_UE = "EM_CORRECAO_UE"
    STATUS_VALORES_REPROGRAMADOS_VALORES_CORRETOS = "VALORES_CORRETOS"

    STATUS_VALORES_REPROGRAMADOS_NOMES = {
        STATUS_VALORES_REPROGRAMADOS_NAO_FINALIZADO: 'Não finalizado',
        STATUS_VALORES_REPROGRAMADOS_EM_CONFERENCIA_DRE: 'Em conferência DRE',
        STATUS_VALORES_REPROGRAMADOS_EM_CORRECAO_UE: 'Em correção UE',
        STATUS_VALORES_REPROGRAMADOS_VALORES_CORRETOS: 'Valores corretos',
    }

    STATUS_VALORES_REPROGRAMADOS_CHOICES = (
        (STATUS_VALORES_REPROGRAMADOS_NAO_FINALIZADO, STATUS_VALORES_REPROGRAMADOS_NOMES[
            STATUS_VALORES_REPROGRAMADOS_NAO_FINALIZADO]),
        (STATUS_VALORES_REPROGRAMADOS_EM_CONFERENCIA_DRE, STATUS_VALORES_REPROGRAMADOS_NOMES[
            STATUS_VALORES_REPROGRAMADOS_EM_CONFERENCIA_DRE]),
        (STATUS_VALORES_REPROGRAMADOS_EM_CORRECAO_UE, STATUS_VALORES_REPROGRAMADOS_NOMES[
            STATUS_VALORES_REPROGRAMADOS_EM_CORRECAO_UE]),
        (STATUS_VALORES_REPROGRAMADOS_VALORES_CORRETOS, STATUS_VALORES_REPROGRAMADOS_NOMES[
            STATUS_VALORES_REPROGRAMADOS_VALORES_CORRETOS]),
    )

    unidade = models.ForeignKey('Unidade', on_delete=models.PROTECT, related_name="associacoes", to_field="codigo_eol",
                                null=True)

    cnpj = models.CharField(
        "CNPJ", max_length=20, validators=[cnpj_validation], blank=True, default="", unique=True
    )

    periodo_inicial = models.ForeignKey(
        'Periodo',
        on_delete=models.PROTECT,
        verbose_name='período inicial',
        related_name='associacoes_iniciadas_no_periodo', null=True, blank=True,
        help_text="O período inicial informado é uma referência e indica que o período a ser habilitado para a associação será o período posterior ao período informado."
    )

    data_de_encerramento = models.DateField(
        'Data de encerramento',
        blank=True,
        null=True,
        help_text="A associação deixará de ser exibida nos períodos posteriores à data de encerramento informada."
    )

    ccm = models.CharField('CCM', max_length=15, null=True, blank=True, default="")

    email = models.EmailField("E-mail", max_length=254, null=True, blank=True, default="")

    processo_regularidade = models.CharField('Nº processo regularidade', max_length=100, default='', blank=True)

    status_presidente = models.CharField(
        'Status do Presidente',
        max_length=15,
        choices=STATUS_PRESIDENTE_CHOICES,
        default=STATUS_PRESIDENTE_PRESENTE,
    )

    cargo_substituto_presidente_ausente = models.CharField(
        'Cargo substituto do presidente ausente',
        max_length=65,
        blank=True,
        null=True,
        choices=MembroEnum.diretoria_executiva_choices(),
        default=None)

    status_valores_reprogramados = models.CharField(
        'Status dos valores reprogramados',
        max_length=20,
        choices=STATUS_VALORES_REPROGRAMADOS_CHOICES,
        default=STATUS_VALORES_REPROGRAMADOS_VALORES_CORRETOS
    )

    def foi_encerrada(self):
        return self.data_de_encerramento is not None

    @property
    def tags_de_informacao(self):
        tags = []

        if self.foi_encerrada():
            tags.append(tag_informacao(
                self.TAG_ENCERRADA,
                f"{self.tooltip_data_encerramento}"
            ))

        return tags

    def apaga_implantacoes_de_saldo(self):
        self.fechamentos_associacao.filter(status='IMPLANTACAO').delete()

    @property
    def presidente_associacao(self):
        cargo = self.cargos.filter(cargo_associacao=MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.name).first()
        if cargo:
            return {
                'nome': cargo.nome,
                'email': cargo.email,
                'cargo_educacao': cargo.cargo_educacao,
                'telefone': cargo.telefone,
                'endereco': cargo.endereco,
                'bairro': cargo.bairro,
                'cep': cargo.cep
            }
        else:
            return {
                'nome': '',
                'email': '',
                'cargo_educacao': '',
                'telefone': '',
                'endereco': '',
                'bairro': '',
                'cep': ''
            }

    @property
    def presidente_conselho_fiscal(self):
        cargo = self.cargos.filter(cargo_associacao=MembroEnum.PRESIDENTE_CONSELHO_FISCAL.name).first()
        if cargo:
            return {
                'nome': cargo.nome,
                'email': cargo.email,
                'cargo_educacao': cargo.cargo_educacao
            }
        else:
            return {
                'nome': '',
                'email': '',
                'cargo_educacao': ''
            }

    @property
    def encerrada(self):
        return self.data_de_encerramento is not None

    def periodos_com_prestacao_de_contas(self, ignorar_pcs_com_acertos_que_demandam_exclusoes_e_fechamentos=False):
        periodos = set()

        prestacoes_da_associacao = self.prestacoes_de_conta_da_associacao

        if self.encerrada:
            prestacoes_da_associacao = prestacoes_da_associacao.filter(
                periodo__data_inicio_realizacao_despesas__lte=self.data_de_encerramento
            )

        for prestacao in prestacoes_da_associacao.all():
            if ignorar_pcs_com_acertos_que_demandam_exclusoes_e_fechamentos:
                if prestacao.analise_atual and prestacao.analise_atual.requer_alteracao_em_lancamentos == True:
                    continue
            periodos.add(prestacao.periodo)

        return periodos

    def proximo_periodo_de_prestacao_de_contas(self, ignorar_devolvidas=False):
        prestacoes_da_associacao = self.prestacoes_de_conta_da_associacao

        if ignorar_devolvidas:
            prestacoes_da_associacao = prestacoes_da_associacao.exclude(status='DEVOLVIDA')

        if self.encerrada:
            prestacoes_da_associacao = prestacoes_da_associacao.filter(
                periodo__data_inicio_realizacao_despesas__lte=self.data_de_encerramento
            )

        ultima_prestacao_feita = prestacoes_da_associacao.last()
        ultimo_periodo_com_prestacao = ultima_prestacao_feita.periodo if ultima_prestacao_feita else None
        if ultimo_periodo_com_prestacao:
            periodo_seguinte = ultimo_periodo_com_prestacao.periodo_seguinte.first()
            if not self.encerrada or (self.encerrada and periodo_seguinte and periodo_seguinte.data_inicio_realizacao_despesas <= self.data_de_encerramento):
                return periodo_seguinte
            else:
                return None
        else:
            return self.periodo_inicial.periodo_seguinte.first() if self.periodo_inicial else None

    def periodos_para_prestacoes_de_conta(self, ignorar_devolvidas=False):
        periodos = set(
            self.periodos_com_prestacao_de_contas(ignorar_pcs_com_acertos_que_demandam_exclusoes_e_fechamentos=True))

        proximo_periodo = self.proximo_periodo_de_prestacao_de_contas(ignorar_devolvidas)
        if proximo_periodo:
            periodos.add(proximo_periodo)

        periodos_ordenados = sorted(periodos, key=Periodo.get_referencia, reverse=True)
        return periodos_ordenados

    def periodos_ate_agora_fora_implantacao(self):
        from datetime import datetime
        from .periodo import Periodo

        qry_periodos = Periodo.objects.filter(
            data_inicio_realizacao_despesas__lte=datetime.today()).order_by('-referencia')

        if self.periodo_inicial:
            qry_periodos = qry_periodos.filter(
                data_inicio_realizacao_despesas__gte=self.periodo_inicial.data_fim_realizacao_despesas
            )

        if self.data_de_encerramento:
            qry_periodos = qry_periodos.filter(
                data_inicio_realizacao_despesas__lte=self.data_de_encerramento
            )
        return qry_periodos.all()

    def membros_por_cargo(self):
        cargos = []
        for key in MembroEnum:
            cargo = self.cargos.filter(cargo_associacao=key.name).first()
            if cargo:
                cargos.append(cargo)
        return cargos

    @classmethod
    def acoes_da_associacao(cls, associacao_uuid):
        associacao = cls.objects.filter(uuid=associacao_uuid).first()
        return associacao.acoes.all().order_by('acao__posicao_nas_pesquisas') if associacao else []

    def altera_status_valor_reprogramado(self, status):
        self.status_valores_reprogramados = status
        self.save()

    @property
    def pode_editar_periodo_inicial(self):
        from ..services.associacoes_service import ValidaSePodeEditarPeriodoInicial
        response = ValidaSePodeEditarPeriodoInicial(associacao=self).response
        return response

    @property
    def tooltip_data_encerramento(self):
        return f"A associação foi encerrada em {self.data_de_encerramento.strftime('%d/%m/%Y')}" if \
            self.data_de_encerramento else None

    @property
    def pode_editar_dados_associacao_encerrada(self):
        if self.encerrada:
            ultima_pc = self.prestacoes_de_conta_da_associacao.order_by('id').last()
            if ultima_pc:
                if ultima_pc.pc_publicada_no_diario_oficial:
                    return False
        return True

    @property
    def membros_diretoria_executiva_e_conselho_fiscal_cadastrados(self):
        for key in MembroEnum:
            cargo = self.cargos.filter(cargo_associacao=key.name)
            if not cargo.exists():
                return False
        return True

    def pendencias_dados_da_associacao_para_geracao_de_documentos(self):
        pendencia_cadastro = not self.nome or not self.ccm
        pendencia_membros = not self.membros_diretoria_executiva_e_conselho_fiscal_cadastrados
        pendencia_contas =  self.contas.filter(Q(banco_nome__exact='') | Q(agencia__exact='') | Q(numero_conta__exact='',
                                               status=ContaAssociacao.STATUS_ATIVA)).exists()
        if pendencia_cadastro or pendencia_membros or pendencia_contas:
            pendencias = {
                'pendencia_cadastro': pendencia_cadastro,
                'pendencia_membros': pendencia_membros,
                'pendencia_contas': pendencia_contas
            }
        else:
            pendencias = None

        return pendencias

    def pendencias_conciliacao_bancaria_por_periodo_para_geracao_de_documentos(self, periodo):
        from ..services import info_resumo_conciliacao

        pendencias = {
            'contas_pendentes': []
        }

        contas = self.contas.filter(status=ContaAssociacao.STATUS_ATIVA)
        observacoes = self.observacoes_conciliacao_da_associacao.filter(periodo=periodo)
        for conta in contas:
            resumo = info_resumo_conciliacao(periodo, conta)
            observacao = observacoes.filter(conta_associacao=conta).first()
            if observacao is None or not (observacao.data_extrato and ((resumo['saldo_posterior_total'] > 0 and observacao.comprovante_extrato) or resumo['saldo_posterior_total'] == 0)):
                pendencias['contas_pendentes'].append(conta.uuid)

        if not pendencias['contas_pendentes']:
            return None

        return pendencias

    objects = models.Manager()  # Manager Padrão
    ativas = AssociacoesAtivasManager()

    class Meta:
        verbose_name = "Associação"
        verbose_name_plural = "07.0) Associações"

    def clean(self):
        data_fim_realizacao_despesas = self.periodo_inicial.data_fim_realizacao_despesas if self.periodo_inicial and self.periodo_inicial.data_fim_realizacao_despesas else None

        if self.data_de_encerramento and self.data_de_encerramento > datetime.date.today():
            raise ValidationError(
                {'data_de_encerramento': "Data de encerramento não pode ser maior que a data de Hoje"})

        if data_fim_realizacao_despesas and self.data_de_encerramento and self.data_de_encerramento < data_fim_realizacao_despesas:
            raise ValidationError(
                {
                    'data_de_encerramento': "Data de encerramento não pode ser menor que data_fim_realizacao_despesas do período inicial"})

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    @classmethod
    def get_associacoes_ativas_no_periodo(cls, periodo, dre=None):
        from .parametros import Parametros

        associacoes_ativas = cls.ativas

        if dre:
            associacoes_ativas = associacoes_ativas.filter(unidade__dre=dre)

        if Parametros.get().desconsiderar_associacoes_nao_iniciadas:
            associacoes_ativas = associacoes_ativas.exclude(periodo_inicial__isnull=True)

            associacoes_ativas = associacoes_ativas.exclude(periodo_inicial__referencia__gte=periodo.referencia)

        associacoes_ativas = associacoes_ativas.exclude(
            data_de_encerramento__lte=periodo.data_inicio_realizacao_despesas)

        return associacoes_ativas

    @classmethod
    def filtro_informacoes_to_json(cls):
        return FiltroInformacoesAssociacao.choices()

    @classmethod
    def get_tags_informacoes_list(cls):
        return [cls.TAG_ENCERRADA]

def tag_informacao(tipo_de_tag, hint):
    return {
        'tag_id': tipo_de_tag['id'],
        'tag_nome': tipo_de_tag['nome'],
        'tag_hint': hint,
    }

auditlog.register(Associacao)

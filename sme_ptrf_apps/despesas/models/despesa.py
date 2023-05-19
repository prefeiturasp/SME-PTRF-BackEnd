from datetime import datetime

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.db.models import Count
from django.dispatch import receiver

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from .fornecedor import Fornecedor
from .validators import cpf_cnpj_validation
from ..status_cadastro_completo import STATUS_CHOICES, STATUS_COMPLETO, STATUS_INCOMPLETO, STATUS_INATIVO
from ...core.models import Associacao


class DespesasCompletasManager(models.Manager):
    def get_queryset(self):
        return super(DespesasCompletasManager, self).get_queryset().filter(status=STATUS_COMPLETO)


class Despesa(ModeloBase):
    # Tags de informações
    TAG_ANTECIPADO = {"id": "1", "nome": "Antecipado", "descricao": "Data do pagamento anterior à data do documento."}
    TAG_ESTORNADO = {"id": "2", "nome": "Estornado", "descricao": "Despesa estornada."}
    TAG_PARCIAL = {"id": "3", "nome": "Parcial", "descricao": "Parte da despesa paga com recursos próprios ou de mais de uma conta."}
    TAG_IMPOSTO = {"id": "4", "nome": "Imposto", "descricao": "Despesa com recolhimento de imposto."}
    TAG_IMPOSTO_PAGO = {"id": "5", "nome": "Imposto Pago", "descricao": "Imposto recolhido relativo a uma despesa de serviço."}
    TAG_INATIVA = {"id": "6", "nome": "Excluído", "descricao": "Lançamento excluído."}

    history = AuditlogHistoryField()

    associacao = models.ForeignKey(Associacao, on_delete=models.PROTECT, related_name='despesas', blank=True,
                                   null=True)

    numero_documento = models.CharField('Nº do documento', max_length=100, default='', blank=True)

    tipo_documento = models.ForeignKey('TipoDocumento', on_delete=models.PROTECT, blank=True, null=True)

    data_documento = models.DateField('Data do documento', blank=True, null=True)

    cpf_cnpj_fornecedor = models.CharField(
        "CPF / CNPJ", max_length=20, validators=[cpf_cnpj_validation]
        , blank=True, null=True, default=""
    )

    nome_fornecedor = models.CharField("Nome do fornecedor", max_length=100, default='', blank=True)

    tipo_transacao = models.ForeignKey('TipoTransacao', on_delete=models.PROTECT, blank=True, null=True)

    documento_transacao = models.CharField('Nº doc transação', max_length=100, default='', blank=True)

    data_transacao = models.DateField('Data da transacao', blank=True, null=True)

    valor_total = models.DecimalField('Valor Total', max_digits=8, decimal_places=2, default=0)

    valor_recursos_proprios = models.DecimalField('Valor pago com recursos próprios', max_digits=8, decimal_places=2,
                                                  default=0)

    valor_original = models.DecimalField('Valor original', max_digits=8, decimal_places=2, default=0)

    eh_despesa_sem_comprovacao_fiscal = models.BooleanField('É despesa sem comprovação fiscal?', default=False)

    eh_despesa_reconhecida_pela_associacao = models.BooleanField('É despesa reconhecida pela Associação?', default=True)

    numero_boletim_de_ocorrencia = models.CharField('Nº boletim de ocorrência', max_length=100, default='', blank=True)

    retem_imposto = models.BooleanField('Retém imposto?', default=False)

    despesas_impostos = models.ManyToManyField('Despesa', blank=True, related_name='despesa_geradora')

    motivos_pagamento_antecipado = models.ManyToManyField('MotivoPagamentoAntecipado', blank=True)

    outros_motivos_pagamento_antecipado = models.TextField('Outros motivos para pagamento antecipado', blank=True,
                                                           default='')

    status = models.CharField(
        'status',
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_INCOMPLETO
    )

    data_e_hora_de_inativacao = models.DateTimeField("Inativado em", blank=True, null=True)

    objects = models.Manager()  # Manager Padrão
    completas = DespesasCompletasManager()

    @property
    def valor_ptrf(self):
        return self.valor_total - self.valor_recursos_proprios

    @property
    def conferido(self):
        return not self.rateios.filter(conferido=False).exists()

    @property
    def despesa_geradora_do_imposto(self):
        # Na criação de uma nova instância (ainda sem id) retorna um queryset vazio.
        return self.despesa_geradora if self.id else Despesa.objects.none()

    valor_ptrf.fget.short_description = 'Valor coberto pelo PTRF'

    @property
    def tags_de_informacao(self):
        tags = []
        if self.teve_pagamento_antecipado():
            tags.append(tag_informacao(
                self.TAG_ANTECIPADO,
                f'Data do pagamento ({self.data_transacao:%d/%m/%Y}) anterior à data do documento ({self.data_documento:%d/%m/%Y}).')
            )

        if self.possui_estornos():
            tags.append(tag_informacao(
                self.TAG_ESTORNADO,
                f'Esse gasto possui estornos.')
            )

        if self.possui_retencao_de_impostos():
            tags.append(tag_informacao(
                self.TAG_IMPOSTO,
                self.__hint_impostos()
            ))

        if self.e_despesa_de_imposto():
            tags.append(tag_informacao(
                self.TAG_IMPOSTO_PAGO,
                self.__hint_imposto_pago()
            ))

        if self.tem_pagamento_com_recursos_proprios() or self.tem_pagamentos_em_multiplas_contas():
            tags.append(tag_informacao(
                self.TAG_PARCIAL,
                'Parte da despesa foi paga com recursos próprios ou por mais de uma conta.'
            ))

        if self.e_despesa_inativa():
            tags.append(tag_informacao(
                self.TAG_INATIVA,
                f"Este gasto foi excluído em {self.data_e_hora_de_inativacao.strftime('%d/%m/%Y %H:%M:%S')}"
            ))
        return tags

    @property
    def periodo_da_despesa(self):
        from sme_ptrf_apps.core.models import Periodo
        return Periodo.da_data(self.data_transacao)

    @property
    def inativar_em_vez_de_excluir(self):
        from sme_ptrf_apps.core.models import PrestacaoConta
        if self.status == STATUS_INCOMPLETO:
            return False
        else:
            return PrestacaoConta.objects.filter(
                associacao=self.associacao,
                periodo=self.periodo_da_despesa
            ).exists()

    @property
    def mensagem_inativacao(self):
        return f"Este gasto foi excluído em {self.data_e_hora_de_inativacao.strftime('%d/%m/%Y %H:%M:%S')}" \
            if self.status == "INATIVO" else None

    def __str__(self):
        return f"{self.numero_documento} - {self.data_documento} - {self.valor_total:.2f}"

    def __hint_impostos(self):
        if not self.despesas_impostos.exists():
            return []

        linhas_hint = []
        if self.despesas_impostos.count() == 1:
            linhas_hint.append('Essa despesa teve retenção de imposto:')
        else:
            linhas_hint.append('Essa despesa teve retenções de impostos:')

        for imposto in self.despesas_impostos.all():
            pagamento = f'pago em {imposto.data_transacao:%d/%m/%Y}' if imposto.data_transacao else 'pagamento ainda não realizado'
            linhas_hint.append(f'R$ {str(imposto.valor_total).replace(".",",")}, {pagamento}.')

        return linhas_hint

    def __hint_imposto_pago(self):
        if not self.despesa_geradora.exists():
            return ""

        despesa_geradora = self.despesa_geradora.first()
        separador = ' / ' if despesa_geradora.numero_documento and despesa_geradora.nome_fornecedor else ''
        referencia_despesa = f'{despesa_geradora.numero_documento}{separador}{despesa_geradora.nome_fornecedor}.'

        return f'Esse imposto está relacionado à despesa {referencia_despesa}'

    def cadastro_completo(self):

        completo = self.data_transacao and \
                   self.valor_total > 0

        if completo and not self.eh_despesa_sem_comprovacao_fiscal and not self.despesa_geradora_do_imposto.first():
            completo = completo and self.cpf_cnpj_fornecedor

        if completo and not self.eh_despesa_sem_comprovacao_fiscal and not self.despesa_geradora_do_imposto.first():
            completo = completo and self.nome_fornecedor

        if completo and not self.eh_despesa_sem_comprovacao_fiscal:
            completo = completo and self.tipo_transacao

        if completo and not self.eh_despesa_sem_comprovacao_fiscal:
            completo = completo and self.tipo_documento

        if completo and not self.eh_despesa_sem_comprovacao_fiscal and not self.despesa_geradora_do_imposto.first():
            completo = completo and self.data_documento

        if completo and not self.eh_despesa_sem_comprovacao_fiscal:
            if self.tipo_documento.numero_documento_digitado:
                completo = completo and self.numero_documento

        if completo and not self.eh_despesa_sem_comprovacao_fiscal and self.tipo_transacao.tem_documento:
            completo = completo and self.documento_transacao

        if completo:
            for rateio in self.rateios.all():
                completo = completo and rateio.status == STATUS_COMPLETO

        return completo

    def atualiza_status(self):
        if self.data_e_hora_de_inativacao:
            if self.status != STATUS_INATIVO:
                self.status = STATUS_INATIVO
                self.save()
            return

        cadastro_completo = self.cadastro_completo()
        status_completo = self.status == STATUS_COMPLETO
        if cadastro_completo != status_completo:
            self.save()  # Força um rec'alculo do status.

    def atualiza_rateios_como_saida_recurso_externo(self):
        for rateio in self.rateios.all():
            rateio.saida_de_recurso_externo = True
            rateio.save()

    def verifica_data_documento_vazio(self):
        if self.data_transacao:
            if not self.data_documento:
                self.data_documento = self.data_transacao
                self.save()

    def teve_pagamento_antecipado(self):
        return self.data_transacao and self.data_documento and self.data_transacao < self.data_documento

    def possui_estornos(self):
        return self.rateios.filter(estorno__isnull=False).exists()

    def possui_retencao_de_impostos(self):
        return self.despesas_impostos.exists()

    def e_despesa_de_imposto(self):
        return self.despesa_geradora.exists()

    def tem_pagamento_com_recursos_proprios(self):
        return self.valor_recursos_proprios > 0

    def tem_pagamentos_em_multiplas_contas(self):
        return self.rateios.values('conta_associacao').order_by('conta_associacao').annotate(count=Count('conta_associacao')).count() > 1

    def e_despesa_inativa(self):
        return self.status == STATUS_INATIVO

    def inativar_despesa(self):
        self.status = STATUS_INATIVO
        self.data_e_hora_de_inativacao = datetime.now()
        self.save()

        for rateio in self.rateios.all():
            rateio.inativar_rateio()

        for despesa_imposto in self.despesas_impostos.all():
            despesa_imposto.inativar_despesa()

        return self

    @classmethod
    def by_documento(cls, tipo_documento, numero_documento, cpf_cnpj_fornecedor, associacao__uuid):
        return cls.objects.filter(associacao__uuid=associacao__uuid).filter(
            cpf_cnpj_fornecedor=cpf_cnpj_fornecedor).filter(tipo_documento=tipo_documento).filter(
            numero_documento=numero_documento).first()

    @classmethod
    def get_tags_informacoes_list(cls):
        return [cls.TAG_ANTECIPADO, cls.TAG_ESTORNADO, cls.TAG_PARCIAL, cls.TAG_IMPOSTO, cls.TAG_IMPOSTO_PAGO, cls.TAG_INATIVA]

    class Meta:
        verbose_name = "Documento comprobatório da despesa"
        verbose_name_plural = "Documentos comprobatórios das despesas"


@receiver(pre_save, sender=Despesa)
def proponente_pre_save(instance, **kwargs):
    if instance.data_e_hora_de_inativacao:
        instance.status = STATUS_INATIVO
    else:
        instance.status = STATUS_COMPLETO if instance.cadastro_completo() else STATUS_INCOMPLETO


@receiver(post_save, sender=Despesa)
def rateio_post_save(instance, created, **kwargs):
    """
    Existe um motivo para o fornecedor não ser uma FK nesse modelo e ele ser atualizado indiretamente
    A existência da tabela de fornecedores é apenas para facilitar o preenchimento da despesa pelas associações
    Alterações feitas por uma associação no nome de um fornecedor não deve alterar diretamente as despesas de outras
    """
    if instance and instance.cpf_cnpj_fornecedor and instance.nome_fornecedor:
        Fornecedor.atualiza_ou_cria(cpf_cnpj=instance.cpf_cnpj_fornecedor, nome=instance.nome_fornecedor)


def tag_informacao(tipo_de_tag, hint):
    return {
        'tag_id': tipo_de_tag['id'],
        'tag_nome': tipo_de_tag['nome'],
        'tag_hint': hint,
    }


auditlog.register(Despesa)

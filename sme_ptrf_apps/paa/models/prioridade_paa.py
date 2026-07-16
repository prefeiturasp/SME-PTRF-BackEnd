"""
Módulo de modelos das prioridades do PAA (Plano Anual de Ação).

Este módulo define a entidade responsável por
representar as prioridades do PAA e seus atributos de negócio.
"""
from django.db import models
from django.db.models import QuerySet
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.core.validators import MinValueValidator
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.core.models import AcaoAssociacao
from sme_ptrf_apps.despesas.models import EspecificacaoMaterialServico, TipoCusteio
from sme_ptrf_apps.paa.enums import TipoAplicacaoOpcoesEnum, RecursoOpcoesEnum
from sme_ptrf_apps.paa.models import AcaoPdde, ProgramaPdde


class PrioridadePaaQuerySet(models.QuerySet):
    """
    Retorna as prioridades do PAA com informações obrigatórias
    pendentes de preenchimento.

    Uma prioridade é considerada incompleta quando:
    - o recurso não foi informado;
    - o valor total não foi informado;
    - o recurso é PDDE e a ação PDDE não foi informada;
    - o recurso é PTRF e a ação da associação não foi informada;
    - o recurso é OUTRO_RECURSO e o respectivo recurso não foi informado.
    """
    def incompletas(self) -> QuerySet:
        return self.filter(
            models.Q(recurso__isnull=True) |
            models.Q(valor_total__isnull=True) |
            models.Q(recurso=RecursoOpcoesEnum.PDDE.name, acao_pdde__isnull=True) |
            models.Q(recurso=RecursoOpcoesEnum.PTRF.name, acao_associacao__isnull=True) |
            models.Q(recurso=RecursoOpcoesEnum.OUTRO_RECURSO.name, outro_recurso__isnull=True)
        )


class SimNaoChoices(models.IntegerChoices):
    """Enumeração para representar os status de ativação de uma entidade."""
    SIM = 1, "Sim"
    NAO = 0, "Não"

    @classmethod
    def to_dict(cls) -> list:
        """
        Retorna uma lista de dicionários representando os status disponíveis.
        Cada dicionário contém a chave 'key' com o valor do status e a chave
        'value' com o rótulo do status.
        """
        return [dict(key=key.value, value=key.label) for key in cls]


class PrioridadePaa(ModeloBase):
    """
    Representa uma Prioridade do paa.

    Essa model registra armazena os dados da Prioridade do paa.
    """
    history = AuditlogHistoryField()

    paa = models.ForeignKey(
        'paa.Paa', on_delete=models.PROTECT, verbose_name="PAA", blank=False, null=True)

    paa_importado = models.ForeignKey(
        'paa.Paa', on_delete=models.PROTECT, verbose_name="PAA Importado",
        blank=True, null=True, related_name='paa_importado')

    prioridade = models.BooleanField(
        choices=SimNaoChoices.choices, default=SimNaoChoices.NAO, verbose_name='Prioridade')

    recurso = models.CharField(
        max_length=20, choices=RecursoOpcoesEnum.choices(), null=True, blank=False)

    acao_associacao = models.ForeignKey(AcaoAssociacao, on_delete=models.PROTECT,
                                        related_name="prioridade_paa_da_associacao",
                                        null=True, blank=True,
                                        help_text='Exibido quando o recurso é do tipo PTRF')

    programa_pdde = models.ForeignKey(ProgramaPdde, on_delete=models.PROTECT,
                                      verbose_name="Programa PDDE", blank=True, null=True,
                                      help_text='Exibido quando o recurso é do tipo PDDE')

    acao_pdde = models.ForeignKey(AcaoPdde, on_delete=models.PROTECT, null=True, blank=True,
                                  help_text='Exibido quando o recurso é do tipo PDDE')

    outro_recurso = models.ForeignKey("OutroRecurso", on_delete=models.PROTECT, null=True, blank=True,
                                      help_text='Exibido quando o recurso é do tipo Outros Recursos')

    tipo_aplicacao = models.CharField(max_length=10, null=True, blank=True,
                                      default=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
                                      choices=TipoAplicacaoOpcoesEnum.choices())

    tipo_despesa_custeio = models.ForeignKey(TipoCusteio, on_delete=models.PROTECT, null=True, blank=True,
                                             help_text='Exibido quando o tipo de aplicação é CUSTEIO')

    especificacao_material = models.ForeignKey(EspecificacaoMaterialServico, on_delete=models.PROTECT,
                                               null=True, blank=True)

    valor_total = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=True,
                                      validators=[MinValueValidator(0, message='Valor total não pode ser negativo.')])

    copia_de = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    objects = PrioridadePaaQuerySet.as_manager()

    class Meta:
        verbose_name = "Prioridade do PAA"
        verbose_name_plural = "Prioridades do PAA"

    def nome(self) -> str:
        """
            Exibição unificada em um campo, no admin, de acordo com a condição abaixo
        """
        if self.recurso == RecursoOpcoesEnum.PDDE.name:
            return self.acao_pdde.nome

        if self.recurso == RecursoOpcoesEnum.PTRF.name:
            return self.acao_associacao.acao.nome \
                if self.acao_associacao and self.acao_associacao.acao else 'Informar Ação PTRF'

        if self.recurso == RecursoOpcoesEnum.RECURSO_PROPRIO.name:
            return 'Recursos Próprios'

        if self.recurso == RecursoOpcoesEnum.OUTRO_RECURSO.name:
            return self.outro_recurso.nome if self.outro_recurso else 'Informar Recurso'
        return '--'
    nome.short_description = 'Ação'

    @classmethod
    def excluir_em_lote(cls, lista_uuids) -> list:
        """Exclui itens da prioridade em lote"""
        erros = []
        for item_uuid in lista_uuids:
            try:
                obj = cls.objects.get(uuid=item_uuid)
                obj.delete()
            except cls.DoesNotExist:
                erros.append(
                    {
                        'erro': 'Objeto não encontrado.',
                        'mensagem': f'O objeto Prioridade {item_uuid} não foi encontrado na base de dados.'
                    }
                )
        return erros


auditlog.register(PrioridadePaa)

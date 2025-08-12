from django.db import models
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.core.validators import MinValueValidator
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.core.models import AcaoAssociacao
from sme_ptrf_apps.despesas.models import EspecificacaoMaterialServico, TipoCusteio
from sme_ptrf_apps.paa.enums import TipoAplicacaoOpcoesEnum, RecursoOpcoesEnum
from sme_ptrf_apps.paa.models import AcaoPdde, ProgramaPdde


class SimNaoChoices(models.IntegerChoices):
    SIM = 1, "Sim"
    NAO = 0, "Não"

    @classmethod
    def to_dict(cls):
        return [dict(key=key.value, value=key.label) for key in cls]


class PrioridadePaa(ModeloBase):
    history = AuditlogHistoryField()

    paa = models.ForeignKey(
        'paa.Paa', on_delete=models.PROTECT, verbose_name="PAA", blank=False, null=True)

    prioridade = models.BooleanField(
        choices=SimNaoChoices.choices, default=SimNaoChoices.NAO, verbose_name='Prioridade')

    recurso = models.CharField(
        max_length=20, choices=RecursoOpcoesEnum.choices(), null=True, blank=False)

    acao_associacao = models.ForeignKey(AcaoAssociacao, on_delete=models.PROTECT, null=True, blank=True,
                                        help_text='Exibido quando o recurso é do tipo PTRF')

    programa_pdde = models.ForeignKey(ProgramaPdde, on_delete=models.PROTECT,
                                      verbose_name="Programa PDDE", blank=True, null=True,
                                      help_text='Exibido quando o recurso é do tipo PDDE')

    acao_pdde = models.ForeignKey(AcaoPdde, on_delete=models.PROTECT, null=True, blank=True,
                                  help_text='Exibido quando o recurso é do tipo PDDE')

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

    class Meta:
        verbose_name = "Prioridade do PAA"
        verbose_name_plural = "Prioridades do PAA"

    def nome(self):
        """
            Exibição unificada em um campo, no admin, de acordo com a condição abaixo
        """
        if self.acao_associacao:
            return self.acao_associacao.acao.nome
        elif self.acao_pdde:
            return self.acao_pdde.nome
        else:
            return 'Recursos Próprios'
    nome.short_description = 'Ação'

    @classmethod
    def excluir_em_lote(cls, lista_uuids):
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

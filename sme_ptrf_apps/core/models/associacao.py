from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from .validators import cnpj_validation


# from sme_ptrf_apps.users.models import User


class Associacao(ModeloIdNome):
    unidade = models.ForeignKey('Unidade', on_delete=models.PROTECT, related_name="associacoes", to_field="codigo_eol",
                                null=True)

    cnpj = models.CharField(
        "CNPJ", max_length=20, validators=[cnpj_validation], blank=True, default="", unique=True
    )

    presidente_associacao_nome = models.CharField('nome do presidente da associação', max_length=70, blank=True,
                                                  default="")
    presidente_associacao_rf = models.CharField('RF do presidente associação', max_length=10, blank=True, default="")

    presidente_conselho_fiscal_nome = models.CharField('nome do presidente da associação', max_length=70, blank=True,
                                                       default="")
    presidente_conselho_fiscal_rf = models.CharField('RF do presidente associação', max_length=10, blank=True,
                                                     default="")

    periodo_inicial = models.ForeignKey('Periodo', on_delete=models.PROTECT, verbose_name='período inicial',
                                        related_name='associacoes_iniciadas_no_periodo', null=True, blank=True)

    ccm = models.CharField('CCM', max_length=15, null=True, blank=True, default="")

    email = models.EmailField("E-mail", max_length=254, null=True, blank=True, default="")

    def apaga_implantacoes_de_saldo(self):
        self.fechamentos_associacao.filter(status='IMPLANTACAO').delete()

    @classmethod
    def acoes_da_associacao(cls, associacao_uuid):
        associacao = cls.objects.filter(uuid=associacao_uuid).first()
        return associacao.acoes.all().order_by('acao__posicao_nas_pesquisas') if associacao else []

    class Meta:
        verbose_name = "Associação"
        verbose_name_plural = "Associações"

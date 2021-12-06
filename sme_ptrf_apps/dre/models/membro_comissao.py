from django.db import models
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class MembroComissao(ModeloBase):
    history = AuditlogHistoryField()

    rf = models.CharField('RF', max_length=10)
    nome = models.CharField('Nome', max_length=160)
    email = models.EmailField("E-mail", max_length=254, null=True, blank=True)

    dre = models.ForeignKey('core.Unidade', on_delete=models.PROTECT, related_name='membros_de_comissoes',
                            to_field="codigo_eol", limit_choices_to={'tipo_unidade': 'DRE'})

    comissoes = models.ManyToManyField('Comissao', related_name='membros', verbose_name='Comissões')

    @property
    def qtd_comissoes(self):
        return self.comissoes.count()

    class Meta:
        verbose_name = "Membro de Comissão"
        verbose_name_plural = "Membros de Comissões"

    def __str__(self):
        return f"<RF:{self.rf} Nome:{self.nome} Qtd.Comissões:{self.qtd_comissoes}>"


auditlog.register(MembroComissao)

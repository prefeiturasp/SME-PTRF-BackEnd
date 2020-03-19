from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class EspecificacaoMaterialServico(ModeloBase):
    descricao = models.CharField('Descrição', max_length=200)

    tipo_aplicacao_recurso = models.ForeignKey('TipoAplicacaoRecurso', on_delete=models.PROTECT, blank=True, null=True)
    tipo_custeio = models.ForeignKey('TipoCusteio', on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return f"{self.descricao}"

    class Meta:
        verbose_name = "Especificação de material ou serviço"
        verbose_name_plural = "Especificações de materiais ou serviços"

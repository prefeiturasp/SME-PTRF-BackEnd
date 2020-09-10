from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class Atribuicao(ModeloBase):
    unidade = models.ForeignKey('core.Unidade', on_delete=models.PROTECT, related_name='atribuicoes',
                                blank=True, null=True)
    tecnico = models.ForeignKey('TecnicoDre', on_delete=models.CASCADE, related_name='atribuicoes',
                                blank=True, null=True)
    periodo = models.ForeignKey('core.Periodo', on_delete=models.PROTECT, related_name='atribuicoes',
                                blank=True, null=True)

    @classmethod
    def search(cls, **kwargs):
        """Função que permite fazer consulta de atribuição passando
        os parâmetros na forma chave:valor e sem a necessidade de fazer vários ifs
        para checar os parâmetros.

        exemplo:
        k = {'unidade__uuid': '3f871773-0dd6-4aa7-b5c1-61b926c1d8d0', 'periodo__uuid': None}
        q = Atribuicao.search(**k)
        return QuerySet"""
        kwargs = {k: v for k, v in kwargs.items() if v}
        return cls.objects.filter(**kwargs)

    class Meta:
        verbose_name = 'Atribuição'
        verbose_name_plural = 'Atribuições'

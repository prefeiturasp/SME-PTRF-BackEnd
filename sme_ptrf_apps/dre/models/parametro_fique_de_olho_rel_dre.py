from ckeditor.fields import RichTextField

from sme_ptrf_apps.core.models_abstracts import ModeloBase, SingletonModel


class ParametroFiqueDeOlhoRelDre(SingletonModel, ModeloBase):
    fique_de_olho = RichTextField(null=True, verbose_name='Texto do fique de olho')

    def __str__(self):
        return 'Texto do fique de olho de Relatórios Consolidado '

    class Meta:
        verbose_name = "Fique de olho (Relatório Consolidado)"
        verbose_name_plural = "Fique de olho (Relatório Consolidado)"

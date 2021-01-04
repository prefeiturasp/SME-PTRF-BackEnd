from ckeditor.fields import RichTextField

from sme_ptrf_apps.core.models_abstracts import ModeloBase, SingletonModel


class ParametroFiqueDeOlhoPc(SingletonModel, ModeloBase):
    fique_de_olho = RichTextField(null=True, verbose_name='Texto do fique de olho')

    def __str__(self):
        return 'Texto do fique de olho de Prestações de Contas '

    class Meta:
        verbose_name = "Fique de olho (Prestação de Contas)"
        verbose_name_plural = "01.1) Fique de olho (Prestação de Contas)"

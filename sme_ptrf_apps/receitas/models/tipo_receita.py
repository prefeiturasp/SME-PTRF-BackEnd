from sme_ptrf_apps.core.models_abstracts import ModeloIdNome


class TipoReceita(ModeloIdNome):

    class Meta:
        verbose_name = 'Tipo de receita'
        verbose_name_plural = 'Tipos de receita'

    def __str__(self):
        return self.nome

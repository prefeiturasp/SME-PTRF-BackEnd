from sme_ptrf_apps.core.models_abstracts import ModeloIdNome


class TipoCusteio(ModeloIdNome):

    class Meta:
        verbose_name = "Tipo de despesa de custeio"
        verbose_name_plural = "Tipos de despesa de custeio"
        unique_together = ['nome', ]

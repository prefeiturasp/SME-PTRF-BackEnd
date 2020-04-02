from sme_ptrf_apps.core.models_abstracts import ModeloIdNome


class TipoDocumento(ModeloIdNome):

    class Meta:
        verbose_name = "Tipo de documento"
        verbose_name_plural = "Tipos de documento"

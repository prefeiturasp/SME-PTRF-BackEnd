from sme_ptrf_apps.core.models_abstracts import ModeloIdNome


class TipoAplicacaoRecurso(ModeloIdNome):

    # @classmethod
    # def get_valores(cls):
    #     return cls.objects.all().order_by('nome')

    class Meta:
        verbose_name = "Tipo de aplicação de recurso"
        verbose_name_plural = "Tipos de aplicação de recursos"

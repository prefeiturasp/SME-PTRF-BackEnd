from sme_ptrf_apps.core.models_abstracts import ModeloBase


class CargosAssociacao(ModeloBase):
    nome = models.CharField('Nome', max_length=160)
    
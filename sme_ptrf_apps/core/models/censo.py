from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class Censo(ModeloBase):
    unidade = models.ForeignKey('Unidade', on_delete=models.PROTECT, related_name="censos", to_field="codigo_eol",
                                null=True)
    quantidade_alunos = models.IntegerField("Quantidade Alunos", blank=True, default=0)
    ano = models.CharField('Ano', max_length=4, blank=True, default="")

    def __str__(self):
        return f"Unidade: {self.unidade.nome}, quantidade_alunos: {self.quantidade_alunos}, ano: {self.ano}"

    class Meta:
        verbose_name = "Censo"
        verbose_name_plural = '13.0) Censos'

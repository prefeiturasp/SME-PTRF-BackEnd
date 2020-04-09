from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from .validators import cpf_cnpj_validation


class Fornecedor(ModeloBase):
    cpf_cnpj = models.CharField(
        "CPF / CNPJ", max_length=20, validators=[cpf_cnpj_validation]
        , blank=True, null=True, default=""
    )

    nome = models.CharField("Nome do fornecedor", max_length=100, default='', blank=True)

    def __str__(self):
        return f"{self.nome} - {self.cpf_cnpj}"

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"

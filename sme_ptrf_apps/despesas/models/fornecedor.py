from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from .validators import cpf_cnpj_validation, normalize_cpf_cnpj

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class Fornecedor(ModeloBase):
    history = AuditlogHistoryField()
    cpf_cnpj = models.CharField(
        "CPF / CNPJ", max_length=20, validators=[cpf_cnpj_validation]
        , blank=True, null=True, default="", unique=True
    )

    nome = models.CharField("Nome do fornecedor", max_length=100, default='', blank=True)

    def __str__(self):
        return f"{self.nome} - {self.cpf_cnpj}"

    def save(self, *args, **kwargs):
        if self.cpf_cnpj:
            self.cpf_cnpj = normalize_cpf_cnpj(self.cpf_cnpj)
        return super().save(*args, **kwargs)

    @classmethod
    def atualiza_ou_cria(cls, cpf_cnpj, nome):
        cpf_cnpj = normalize_cpf_cnpj(cpf_cnpj) if cpf_cnpj else cpf_cnpj
        obj, created = cls.objects.update_or_create(
            cpf_cnpj=cpf_cnpj,
            defaults={'nome': nome},
        )
        return obj, created

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"


auditlog.register(Fornecedor)

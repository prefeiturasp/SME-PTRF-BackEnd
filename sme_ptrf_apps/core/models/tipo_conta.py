from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloIdNome


class TipoConta(ModeloIdNome):
    """
    Os atributos banco_nome, agencia, numero_conta, numero_cartao são valores que devem
    ser utilizados como valores default na criação das contas da associação do tipo de 
    conta relacionado.
    """

    banco_nome = models.CharField('Nome do banco', max_length=50, blank=True, default='')
    agencia = models.CharField('Nº agência',  max_length=15, blank=True, default='')
    numero_conta = models.CharField('Nº conta', max_length=30, blank=True, default='')
    numero_cartao = models.CharField('Nº do cartão', max_length=80, blank=True, default='')

    class Meta:
        verbose_name = "Tipo de conta"
        verbose_name_plural = "Tipos de conta"

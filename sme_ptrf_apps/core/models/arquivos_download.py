from django.contrib.auth import get_user_model
from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase


class ArquivoDownload(ModeloBase):
    # Status Choice
    STATUS_EM_PROCESSAMENTO = 'EM_PROCESSAMENTO'
    STATUS_CONCLUIDO = 'CONCLUIDO'
    STATUS_ERRO = 'ERRO'

    STATUS_NOMES = {
        STATUS_EM_PROCESSAMENTO: 'Em processamento',
        STATUS_CONCLUIDO: 'Concluído',
        STATUS_ERRO: 'Erro'
    }

    STATUS_CHOICES = (
        (STATUS_EM_PROCESSAMENTO, STATUS_NOMES[STATUS_EM_PROCESSAMENTO]),
        (STATUS_CONCLUIDO, STATUS_NOMES[STATUS_CONCLUIDO]),
        (STATUS_ERRO, STATUS_NOMES[STATUS_ERRO])
    )

    identificador = models.CharField("Nome do arquivo", max_length=20, default='')
    arquivo = models.FileField(null=True, verbose_name='Arquivo')
    status = models.CharField(
        'status',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_EM_PROCESSAMENTO
    )
    msg_erro = models.CharField("Mensagem erro", max_length=300, blank=True)
    lido = models.BooleanField("Foi lido?", default=False)
    central_de_downloads = models.BooleanField("Deve ir para central de downloads?", default=False)
    usuario = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)

    class Meta:
        verbose_name = "Arquivo Download"
        verbose_name_plural = "15.0) Arquivos Download"


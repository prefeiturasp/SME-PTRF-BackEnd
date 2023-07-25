from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from django.contrib.auth import get_user_model
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from datetime import datetime


class TaskCelery(ModeloBase):
    history = AuditlogHistoryField()

    id_task_assincrona = models.CharField('id task assincrona', max_length=160, editable=False)

    nome_task = models.CharField('Nome', max_length=160)

    usuario = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='tasks_celery_do_usuario',
                                default='', blank=True, null=True, verbose_name="Usuário")

    data_hora_finalizacao = models.DateTimeField("Data e hora de finalizacao", null=True, blank=True)

    finalizada = models.BooleanField("Finalizada ?", default=False)

    # Setar true quando for finalizada atraves de um revoke
    finalizacao_forcada = models.BooleanField("Finalizada forçadamente ?", default=False)

    associacao = models.ForeignKey('Associacao', on_delete=models.CASCADE,
                                   related_name='tasks_celery_da_associacao',
                                   blank=True, null=True, verbose_name="Associação")

    periodo = models.ForeignKey('Periodo', on_delete=models.CASCADE,
                                related_name='asks_celery_do_periodo', blank=True, null=True)

    prestacao_conta = models.ForeignKey('PrestacaoConta', on_delete=models.SET_NULL,
                                        related_name='tasks_celery_da_prestacao_conta', blank=True, null=True)

    class Meta:
        verbose_name = "Task assincrona celery"
        verbose_name_plural = "19.1) Tasks assincronas celery"

    def __str__(self):
        texto_retorno = f"Task: {self.nome_task} - finalizada: {self.finalizada}"
        return texto_retorno

    def registra_data_hora_finalizacao_forcada(self):
        self.finalizada = True
        self.finalizacao_forcada = True
        self.data_hora_finalizacao = datetime.now()
        self.save()

    def registra_data_hora_finalizacao(self):
        self.finalizada = True
        self.data_hora_finalizacao = datetime.now()
        self.save()


auditlog.register(TaskCelery)

from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from django.contrib.auth import get_user_model
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TaskCelery(ModeloBase):
    history = AuditlogHistoryField()

    id_task_assincrona = models.CharField('id task assincrona', max_length=160, blank=True, null=True)

    nome_task = models.CharField('Nome', max_length=160)

    usuario = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='tasks_celery_do_usuario',
                                default=None, blank=True, null=True, verbose_name="Usuário")

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

    log = models.TextField('Log capturado', blank=True, default='')

    class Meta:
        verbose_name = "Task assincrona celery"
        verbose_name_plural = "19.1) Tasks assincronas celery"

    def __str__(self):
        texto_retorno = f"Task: {self.nome_task} - finalizada: {self.finalizada}"
        return texto_retorno

    def registra_data_hora_finalizacao_forcada(self, log=None):
        self.finalizada = True
        self.finalizacao_forcada = True
        self.data_hora_finalizacao = datetime.now()

        if log:
            log_atual = self.log
            novo_log = log_atual + f"\n {log}" if log_atual else log
            self.log = novo_log

        self.save()

    def registra_data_hora_finalizacao(self, log=None):
        self.finalizada = True
        self.data_hora_finalizacao = datetime.now()

        if log:
            log_atual = self.log
            novo_log = log_atual + f"\n {log}" if log_atual else log
            self.log = novo_log

        self.save()

    def grava_log(self, log):
        logger.info(f"{log}")
        self.log = log
        self.save()
        
    def grava_log_concatenado(self, log):
        logger.info(f"{log}")
        self.log = self.log + f"\n{log}"
        self.save()


auditlog.register(TaskCelery)

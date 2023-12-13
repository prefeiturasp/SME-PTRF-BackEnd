import logging

from sme_ptrf_apps.core.models import Periodo, Associacao, TaskCelery
from sme_ptrf_apps.core.services import concluir_prestacao_de_contas
from sme_ptrf_apps.core.tasks import concluir_prestacao_de_contas_async, gerar_relatorio_apos_acertos_async

logger = logging.getLogger(__name__)


class PrestacaoContaService:
    def __init__(self, periodo_uuid, associacao_uuid):
        try:
            self._periodo = Periodo.by_uuid(uuid=periodo_uuid)
        except Periodo.DoesNotExist:
            raise Exception(f"Período com uuid {periodo_uuid} não encontrado")

        try:
            self._associacao = Associacao.by_uuid(uuid=associacao_uuid)
        except Associacao.DoesNotExist:
            raise Exception(f"Associação com uuid {associacao_uuid} não encontrada")

    def concluir_pc(self, usuario, justificativa_acertos_pendentes):
        logger.info(f"Conclusão de PC V2. Período:{self._periodo.referencia} Associação:{self._associacao.nome}")

        dados = concluir_prestacao_de_contas(
            associacao=self._associacao,
            periodo=self._periodo,
            usuario=usuario,
            monitoraPc=True,
        )
        prestacao_de_contas = dados["prestacao"]

        erro_pc = dados["erro"]
        if erro_pc:
            raise Exception(erro_pc)
        else:
            task_celery = TaskCelery.objects.create(
                nome_task="concluir_prestacao_de_contas_async",
                usuario=usuario,
                associacao=self._associacao,
                periodo=self._periodo,
                prestacao_conta=prestacao_de_contas
            )

            id_task = concluir_prestacao_de_contas_async.apply_async(
                (
                    self._periodo.uuid,
                    self._associacao.uuid,
                    usuario.username,
                    True,
                    dados["e_retorno_devolucao"],
                    dados["requer_geracao_documentos"],
                    dados["requer_geracao_fechamentos"],
                    dados["requer_acertos_em_extrato"],
                    justificativa_acertos_pendentes,
                ), countdown=1
            )

            if dados["e_retorno_devolucao"]:
                task_celery_geracao_relatorio_apos_acerto = TaskCelery.objects.create(
                    nome_task="gerar_relatorio_apos_acertos_async",
                    associacao=self._associacao,
                    periodo=self._periodo,
                    usuario=usuario
                )

                id_task_geracao_relatorio_apos_acerto = gerar_relatorio_apos_acertos_async.apply_async(
                    (
                        task_celery_geracao_relatorio_apos_acerto.uuid,
                        self._associacao.uuid,
                        self._periodo.uuid,
                        usuario.name
                    ), countdown=1
                )

                task_celery_geracao_relatorio_apos_acerto.id_task_assincrona = id_task_geracao_relatorio_apos_acerto
                task_celery_geracao_relatorio_apos_acerto.save()

            task_celery.id_task_assincrona = id_task
            task_celery.save()

        return prestacao_de_contas

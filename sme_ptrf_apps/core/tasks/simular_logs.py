from celery import shared_task

from sme_ptrf_apps.utils.simulador_de_logs import simular_logs


@shared_task(
    time_limet=90,
    soft_time_limit=120
)
def simular_logs_async():
    simular_logs()

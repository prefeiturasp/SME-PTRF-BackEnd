import pytest
from ...models import RelatorioConsolidadoDRE
from sme_ptrf_apps.core.models import TipoConta
from ...services.consolidado_dre_service import concluir_consolidado_dre, gerar_previa_consolidado_dre

pytestmark = pytest.mark.django_db


def test_gerar_previa_consolidado_dre(
    dre_teste_service_consolidado_dre,
    periodo_teste_service_consolidado_dre,
    consolidado_dre_teste_service_consolidado_dre,
    retorna_parcial_false,
    retorna_username,
    ata_parecer_tecnico_teste_service,
    unidade_teste_service_consolidado_dre_02,
    unidade_teste_service_consolidado_dre_01,
    associacao_teste_service_consolidado_dre_01,
    associacao_teste_service_consolidado_dre_02,
    ano_analise_regularidade_2022_teste_service
):
    consolidado_dre = gerar_previa_consolidado_dre(
        dre_teste_service_consolidado_dre,
        periodo_teste_service_consolidado_dre,
        retorna_parcial_false,
        retorna_username,
    )

    assert consolidado_dre.uuid == consolidado_dre_teste_service_consolidado_dre.uuid

    assert consolidado_dre.versao == 'PREVIA'


def test_criar_previa_documentos_relatorio_fisico_financeiro_todas_as_contas(
    dre_teste_service_consolidado_dre,
    periodo_teste_service_consolidado_dre,
    consolidado_dre_teste_service_consolidado_dre,
    retorna_parcial_false,
    retorna_username,
    ano_analise_regularidade_2022_teste_service,
    comissao_exame_contas_teste_service,
    membro_comissao_teste_service,
    parametros_dre_teste_service,
    ata_parecer_tecnico_teste_service,
    settings
):
    # Foi fundamental para o teste passar!!
    # CELERY_ALWAYS_EAGER
    # Se for True, todas as tarefas serão executadas localmente bloqueando até que a tarefa retorne.
    # apply_async() e Task.delay() retorna uma EagerResult instância, que emula a API e o comportamento de AsyncResult,
    # exceto que o resultado já foi avaliado.
    # Ou seja, as tarefas serão executadas localmente em vez de serem enviadas para a fila.
    settings.CELERY_TASK_ALWAYS_EAGER = True

    parcial = retorna_parcial_false
    usuario = retorna_username

    gerar_previa_consolidado_dre(
        dre=dre_teste_service_consolidado_dre,
        periodo=periodo_teste_service_consolidado_dre,
        parcial=parcial,
        usuario=usuario,
    )

    assert consolidado_dre_teste_service_consolidado_dre \
           .relatorios_consolidados_dre_do_consolidado_dre \
           .first() \
           .versao == 'PREVIA'

    assert consolidado_dre_teste_service_consolidado_dre\
           .relatorios_consolidados_dre_do_consolidado_dre\
           .last()\
           .versao == 'PREVIA'

    assert ata_parecer_tecnico_teste_service.consolidado_dre.uuid == consolidado_dre_teste_service_consolidado_dre.uuid


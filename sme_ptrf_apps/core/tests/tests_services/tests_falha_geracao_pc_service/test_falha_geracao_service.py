import pytest
from sme_ptrf_apps.core.models.falha_geracao_pc import FalhaGeracaoPc
from sme_ptrf_apps.core.services.falha_geracao_pc_service import FalhaGeracaoPcService, InfoRegistroFalhaGeracaoPc
from freezegun import freeze_time

pytestmark = pytest.mark.django_db


def test_deve_gerar_registro_falha_geracao_pc(
    prestacao_conta_teste_falha_geracao_pc_service,
    periodo_teste_falha_geracao_pc_service,
    usuario_dre_teste_falha_geracao_pc_service,
    associacao_teste_falha_geracao_pc_service,
):
    assert not FalhaGeracaoPc.objects.filter(
        associacao=associacao_teste_falha_geracao_pc_service,
        periodo=periodo_teste_falha_geracao_pc_service
    ).first()

    registra_falha = FalhaGeracaoPcService(
        prestacao_de_contas=prestacao_conta_teste_falha_geracao_pc_service,
        periodo=periodo_teste_falha_geracao_pc_service,
        usuario=usuario_dre_teste_falha_geracao_pc_service,
        associacao=associacao_teste_falha_geracao_pc_service
    )
    registra_falha.registra_falha_geracao_pc()

    assert FalhaGeracaoPc.objects.filter(
        associacao=associacao_teste_falha_geracao_pc_service,
        periodo=periodo_teste_falha_geracao_pc_service
    ).first()


@freeze_time("2023-03-06 09:10:00")
def test_deve_alterar_registro_falha_geracao_pc_incrementar_numero_de_ocorrencias(
    prestacao_conta_teste_falha_geracao_pc_service,
    periodo_teste_falha_geracao_pc_service,
    usuario_dre_teste_falha_geracao_pc_service,
    associacao_teste_falha_geracao_pc_service,
    falha_geracao_pc_teste_falha_geracao_pc_service_01,
):
    # Data da data_hora_ultima_ocorrencia da fixture (falha_geracao_pc_teste_falha_geracao_pc_service_01) 2023-03-06 09:07:19

    registro = FalhaGeracaoPc.objects.filter(
        associacao=associacao_teste_falha_geracao_pc_service,
        periodo=periodo_teste_falha_geracao_pc_service
    ).first()

    assert registro.qtd_ocorrencias_sucessivas == 1

    registra_falha = FalhaGeracaoPcService(
        prestacao_de_contas=prestacao_conta_teste_falha_geracao_pc_service,
        periodo=periodo_teste_falha_geracao_pc_service,
        usuario=usuario_dre_teste_falha_geracao_pc_service,
        associacao=associacao_teste_falha_geracao_pc_service
    )
    registra_falha.registra_falha_geracao_pc()

    registro = FalhaGeracaoPc.objects.filter(
        associacao=associacao_teste_falha_geracao_pc_service,
        periodo=periodo_teste_falha_geracao_pc_service
    ).first()

    assert registro.qtd_ocorrencias_sucessivas == 2


@freeze_time("2023-03-07 09:10:00")
def test_deve_alterar_registro_falha_geracao_pc_zerar_numero_de_ocorrencias(
    prestacao_conta_teste_falha_geracao_pc_service,
    periodo_teste_falha_geracao_pc_service,
    usuario_dre_teste_falha_geracao_pc_service,
    associacao_teste_falha_geracao_pc_service,
    falha_geracao_pc_teste_falha_geracao_pc_service_02,
):
    # Data da data_hora_ultima_ocorrencia da fixture (falha_geracao_pc_teste_falha_geracao_pc_service_01) 2023-03-06 09:07:19

    registro = FalhaGeracaoPc.objects.filter(
        associacao=associacao_teste_falha_geracao_pc_service,
        periodo=periodo_teste_falha_geracao_pc_service
    ).first()

    assert registro.qtd_ocorrencias_sucessivas == 2

    registra_falha = FalhaGeracaoPcService(
        prestacao_de_contas=prestacao_conta_teste_falha_geracao_pc_service,
        periodo=periodo_teste_falha_geracao_pc_service,
        usuario=usuario_dre_teste_falha_geracao_pc_service,
        associacao=associacao_teste_falha_geracao_pc_service
    )
    registra_falha.registra_falha_geracao_pc()

    registro = FalhaGeracaoPc.objects.filter(
        associacao=associacao_teste_falha_geracao_pc_service,
        periodo=periodo_teste_falha_geracao_pc_service
    ).first()

    assert registro.qtd_ocorrencias_sucessivas == 1


def test_deve_marcar_como_resolvido_registro_falha_geracao_pc(
    periodo_teste_falha_geracao_pc_service,
    usuario_dre_teste_falha_geracao_pc_service,
    associacao_teste_falha_geracao_pc_service,
    falha_geracao_pc_teste_falha_geracao_pc_service_01,
):
    # Data da data_hora_ultima_ocorrencia da fixture (falha_geracao_pc_teste_falha_geracao_pc_service_01) 2023-03-06 09:07:19

    registro = FalhaGeracaoPc.objects.filter(
        associacao=associacao_teste_falha_geracao_pc_service,
        periodo=periodo_teste_falha_geracao_pc_service
    ).first()

    assert not registro.resolvido

    registra_falha = FalhaGeracaoPcService(
        periodo=periodo_teste_falha_geracao_pc_service,
        usuario=usuario_dre_teste_falha_geracao_pc_service,
        associacao=associacao_teste_falha_geracao_pc_service
    )
    registra_falha.marcar_como_resolvido()

    registro = FalhaGeracaoPc.objects.filter(
        associacao=associacao_teste_falha_geracao_pc_service,
        periodo=periodo_teste_falha_geracao_pc_service
    ).first()

    assert registro.resolvido


def test_deve_retornar_info_registro_falha_geracao_pc_nao_excede_tentativas(
    periodo_teste_falha_geracao_pc_service,
    periodo_teste_falha_geracao_pc_service_02,
    usuario_dre_teste_falha_geracao_pc_service,
    associacao_teste_falha_geracao_pc_service,
    parametros_teste_falha_geracao_pc_service,
    falha_geracao_pc_teste_falha_geracao_pc_service_nao_excede_tentativas,
    falha_geracao_pc_teste_falha_geracao_pc_service_nao_excede_tentativas_02,
):
    registra_falha = InfoRegistroFalhaGeracaoPc(
        associacao=associacao_teste_falha_geracao_pc_service,
        usuario=usuario_dre_teste_falha_geracao_pc_service,
    )

    response = registra_falha.info_registro_falha_geracao_pc()

    esperado = [
        {
            "exibe_modal": True,
            "excede_tentativas": False,
            "texto": f"Houve um problema na conclusão do período/acerto 2022.1. Favor concluir novamente.",
            "periodo_referencia": '2022.1',
            "periodo_uuid": periodo_teste_falha_geracao_pc_service.uuid,
            "periodo_data_final": periodo_teste_falha_geracao_pc_service.data_fim_realizacao_despesas,
            "periodo_data_inicio": periodo_teste_falha_geracao_pc_service.data_inicio_realizacao_despesas,
            "associacao": associacao_teste_falha_geracao_pc_service.uuid,
            "usuario": usuario_dre_teste_falha_geracao_pc_service.username,
        },
        {
            "exibe_modal": True,
            "excede_tentativas": False,
            "texto": f"Houve um problema na conclusão do período/acerto 2022.2. Favor concluir novamente.",
            "periodo_referencia": '2022.2',
            "periodo_uuid": periodo_teste_falha_geracao_pc_service_02.uuid,
            "periodo_data_final": periodo_teste_falha_geracao_pc_service_02.data_fim_realizacao_despesas,
            "periodo_data_inicio": periodo_teste_falha_geracao_pc_service_02.data_inicio_realizacao_despesas,
            "associacao": associacao_teste_falha_geracao_pc_service.uuid,
            "usuario": usuario_dre_teste_falha_geracao_pc_service.username,
        }
    ]

    assert response == esperado


def test_deve_retornar_info_registro_falha_geracao_pc_excede_tentativas(
    periodo_teste_falha_geracao_pc_service,
    usuario_dre_teste_falha_geracao_pc_service,
    associacao_teste_falha_geracao_pc_service,
    parametros_teste_falha_geracao_pc_service,
    falha_geracao_pc_teste_falha_geracao_pc_service_excede_tentativas,
):
    registra_falha = InfoRegistroFalhaGeracaoPc(
        associacao=associacao_teste_falha_geracao_pc_service,
        usuario=usuario_dre_teste_falha_geracao_pc_service,
    )

    response = registra_falha.info_registro_falha_geracao_pc()

    esperado = [{
        "exibe_modal": True,
        "excede_tentativas": True,
        "texto": f"Infelizmente um problema impediu a conclusão do período/acerto 2022.1",
        "periodo_referencia": '2022.1',
        "periodo_uuid": periodo_teste_falha_geracao_pc_service.uuid,
        "periodo_data_final": periodo_teste_falha_geracao_pc_service.data_fim_realizacao_despesas,
        "periodo_data_inicio": periodo_teste_falha_geracao_pc_service.data_inicio_realizacao_despesas,
        "associacao": associacao_teste_falha_geracao_pc_service.uuid,
        "usuario": usuario_dre_teste_falha_geracao_pc_service.username,
    }]

    assert response == esperado


def test_deve_retornar_info_registro_falha_geracao_pc_nao_exibe_modal(
    periodo_teste_falha_geracao_pc_service,
    usuario_dre_teste_falha_geracao_pc_service,
    associacao_teste_falha_geracao_pc_service,
    parametros_teste_falha_geracao_pc_service,
    falha_geracao_pc_teste_falha_geracao_pc_service_nao_exibe_modal,
):
    registra_falha = InfoRegistroFalhaGeracaoPc(
        associacao=associacao_teste_falha_geracao_pc_service,
        usuario=usuario_dre_teste_falha_geracao_pc_service,
    )

    response = registra_falha.info_registro_falha_geracao_pc()

    esperado = []

    assert response == esperado

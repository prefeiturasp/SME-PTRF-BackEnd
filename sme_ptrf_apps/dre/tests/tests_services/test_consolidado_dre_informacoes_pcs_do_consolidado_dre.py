import pytest

from sme_ptrf_apps.dre.services import informacoes_pcs_aprovadas_aprovadas_com_ressalva_reprovadas_por_conta

pytestmark = pytest.mark.django_db


def test_retorna_informacoes_pcs_do_consolidado_dre_por_conta_cheque_pc_aprovada(
    dre_teste_service_consolidado_dre,
    periodo_teste_service_consolidado_dre,
    prestacao_conta_aprovada_teste_service_pc_aprovada_info_pc,
    associacao_teste_service_02,
    tipo_conta_cartao_teste_service,
    conta_associacao_teste_service_02
):
    dado = informacoes_pcs_aprovadas_aprovadas_com_ressalva_reprovadas_por_conta(
        dre_teste_service_consolidado_dre,
        periodo_teste_service_consolidado_dre,
        tipo_conta_cartao_teste_service,
        apenas_nao_publicadas=False
    )

    resultado_esperado = [
        {
            'unidade': {
                'uuid': f'{prestacao_conta_aprovada_teste_service_pc_aprovada_info_pc.associacao.unidade.uuid}',
                'codigo_eol': prestacao_conta_aprovada_teste_service_pc_aprovada_info_pc.associacao.unidade.codigo_eol,
                'tipo_unidade': prestacao_conta_aprovada_teste_service_pc_aprovada_info_pc.associacao.unidade.tipo_unidade,
                'nome': prestacao_conta_aprovada_teste_service_pc_aprovada_info_pc.associacao.unidade.nome,
                'sigla': prestacao_conta_aprovada_teste_service_pc_aprovada_info_pc.associacao.unidade.sigla,
            },

            'status_prestacao_contas': 'APROVADA',
            'uuid_pc': prestacao_conta_aprovada_teste_service_pc_aprovada_info_pc.uuid,
        }
    ]

    assert dado == resultado_esperado


def test_retorna_informacoes_pcs_do_consolidado_dre_por_conta_cheque_pc_reprovada(
    dre_teste_service_consolidado_dre,
    periodo_teste_service_consolidado_dre,
    prestacao_conta_reprovada_teste_service_publicada,
    associacao_teste_service_02,
    tipo_conta_cheque_teste_service,
    conta_associacao_teste_service
):
    dado = informacoes_pcs_aprovadas_aprovadas_com_ressalva_reprovadas_por_conta(
        dre_teste_service_consolidado_dre,
        periodo_teste_service_consolidado_dre,
        tipo_conta_cheque_teste_service,
        apenas_nao_publicadas=False
    )

    resultado_esperado = [
        {
            'unidade': {
                'uuid': f'{prestacao_conta_reprovada_teste_service_publicada.associacao.unidade.uuid}',
                'codigo_eol': prestacao_conta_reprovada_teste_service_publicada.associacao.unidade.codigo_eol,
                'tipo_unidade': prestacao_conta_reprovada_teste_service_publicada.associacao.unidade.tipo_unidade,
                'nome': prestacao_conta_reprovada_teste_service_publicada.associacao.unidade.nome,
                'sigla': prestacao_conta_reprovada_teste_service_publicada.associacao.unidade.sigla,
            },

            'status_prestacao_contas': 'REPROVADA',
            'uuid_pc': prestacao_conta_reprovada_teste_service_publicada.uuid,
            'motivos_reprovacao': []
        }
    ]

    assert dado == resultado_esperado

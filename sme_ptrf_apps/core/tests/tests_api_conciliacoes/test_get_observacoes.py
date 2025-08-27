import json
import pytest
from rest_framework import status
from datetime import date
from sme_ptrf_apps.core.models.solicitacao_encerramento_conta_associacao import SolicitacaoEncerramentoContaAssociacao
pytestmark = pytest.mark.django_db


def test_api_get_observacoes_sem_observacoes_e_encerramento(jwt_authenticated_client_a,
                                                            periodo_2020_1,
                                                            conta_associacao_cartao
                                                            ):
    conta_uuid = conta_associacao_cartao.uuid

    url = f'/api/conciliacoes/observacoes/?periodo={periodo_2020_1.uuid}&conta_associacao={conta_uuid}&associacao={conta_associacao_cartao.associacao.uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert result == {
        'observacao_uuid': None,
        'observacao': None,
        'saldo_extrato': None,
        'data_extrato': '2020-06-30',
        'comprovante_extrato': None,
        'data_atualizacao_comprovante_extrato': None,
        'data_encerramento': None,
        'saldo_encerramewnto': None,
        'possui_solicitacao_encerramento': False,
        'permite_editar_campos_extrato': True
    }

    assert response.status_code == status.HTTP_200_OK


def test_api_get_com_observacoes(jwt_authenticated_client_a,
                                 periodo,
                                 conta_associacao,
                                 observacao_conciliacao
                                 ):
    conta_uuid = conta_associacao.uuid

    url = f'/api/conciliacoes/observacoes/?periodo={periodo.uuid}&conta_associacao={conta_uuid}&associacao={conta_associacao.associacao.uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK

    assert result == {
        'observacao_uuid': f'{observacao_conciliacao.uuid}',
        'observacao': 'Uma bela observação.',
        'saldo_extrato': 1000.0,
        'data_extrato': '2020-07-01',
        'comprovante_extrato': '',
        'data_atualizacao_comprovante_extrato': None,
        'data_encerramento': None,
        'saldo_encerramewnto': None,
        'possui_solicitacao_encerramento': False,
        'permite_editar_campos_extrato': True
    }


def test_api_get_sem_observacoes_e_encerramento(jwt_authenticated_client_a,
                                                periodo_2019_1,
                                                conta_associacao,
                                                solicitacao_encerramento_conta_associacao_factory
                                                ):
    solicitacao_encerramento_conta_associacao_factory.create(
        conta_associacao=conta_associacao,
        status=SolicitacaoEncerramentoContaAssociacao.STATUS_APROVADA,
        data_de_encerramento_na_agencia=date(2019, 5, 1)
    )

    url = f'/api/conciliacoes/observacoes/?periodo={periodo_2019_1.uuid}&conta_associacao={conta_associacao.uuid}&associacao={conta_associacao.associacao.uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK

    assert result == {
        'observacao_uuid': None,
        'observacao': None,
        'saldo_extrato': None,
        'data_extrato': '2019-05-01',
        'comprovante_extrato': None,
        'data_atualizacao_comprovante_extrato': None,
        'data_encerramento': '2019-05-01',
        'saldo_encerramewnto': 0,
        'possui_solicitacao_encerramento': True,
        'permite_editar_campos_extrato': True
    }

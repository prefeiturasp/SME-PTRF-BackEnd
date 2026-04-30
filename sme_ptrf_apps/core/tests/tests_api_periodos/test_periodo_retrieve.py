import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_retrieve_periodo(
    jwt_authenticated_client_a,
    periodo_2021_2
):
    response = jwt_authenticated_client_a.get(
        f'/api/periodos/{periodo_2021_2.uuid}/', content_type='application/json')

    result = json.loads(response.content)

    p = periodo_2021_2

    esperado = {
        "uuid": f'{p.uuid}',
        "id": p.id,
        "referencia": p.referencia,
        "data_inicio_realizacao_despesas": f'{p.data_inicio_realizacao_despesas}' if p.data_inicio_realizacao_despesas else None,
        "data_fim_realizacao_despesas": f'{p.data_fim_realizacao_despesas}' if p.data_fim_realizacao_despesas else None,
        "data_prevista_repasse": f'{p.data_prevista_repasse}' if p.data_prevista_repasse else None,
        "data_inicio_prestacao_contas": f'{p.data_inicio_prestacao_contas}' if p.data_inicio_prestacao_contas else None,
        "data_fim_prestacao_contas": f'{p.data_fim_prestacao_contas}' if p.data_fim_prestacao_contas else None,
        "editavel": p.editavel,
        "periodo_anterior": {
            "id": p.periodo_anterior.id,
            "uuid": f'{p.periodo_anterior.uuid}',
            "referencia": p.periodo_anterior.referencia,
            "data_inicio_realizacao_despesas": f'{p.periodo_anterior.data_inicio_realizacao_despesas}' if p.periodo_anterior.data_inicio_realizacao_despesas else None,
            "data_fim_realizacao_despesas": f'{p.periodo_anterior.data_fim_realizacao_despesas}' if p.periodo_anterior.data_fim_realizacao_despesas else None,
            "referencia_por_extenso": f"{p.periodo_anterior.referencia.split('.')[1]}° repasse de {p.referencia.split('.')[0]}",
            "recurso": {
                "id": p.periodo_anterior.recurso.id,
                "uuid": f'{p.periodo_anterior.recurso.uuid}',
                "nome": p.periodo_anterior.recurso.nome,
                "nome_exibicao": p.periodo_anterior.recurso.nome_exibicao,
                "criado_em": f'{p.periodo_anterior.recurso.criado_em.isoformat()}' if p.periodo_anterior.recurso.criado_em else None,
                "alterado_em": f'{p.periodo_anterior.recurso.alterado_em.isoformat()}' if p.periodo_anterior.recurso.alterado_em else None,
                "cor": p.periodo_anterior.recurso.cor,
                "icone": p.periodo_anterior.recurso.icone if p.periodo_anterior.recurso.icone else None,
                "ativo": p.periodo_anterior.recurso.ativo,
                "legado": p.periodo_anterior.recurso.legado,
                "exibe_valores_reprogramados": p.periodo_anterior.recurso.exibe_valores_reprogramados
            }
        },
        "recurso": {
            "id": p.recurso.id,
            "uuid": f'{p.recurso.uuid}',
            "nome": p.recurso.nome,
            "nome_exibicao": p.recurso.nome_exibicao,
            "criado_em": f'{p.recurso.criado_em.isoformat()}' if p.recurso.criado_em else None,
            "alterado_em": f'{p.recurso.alterado_em.isoformat()}' if p.recurso.alterado_em else None,
            "cor": p.recurso.cor,
            "icone": p.recurso.icone if p.recurso.icone else None,
            "ativo": p.recurso.ativo,
            "legado": p.recurso.legado,
            "exibe_valores_reprogramados": p.recurso.exibe_valores_reprogramados
        }
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado

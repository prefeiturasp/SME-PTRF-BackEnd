import json
import pytest
from rest_framework import status
from ...models.comentario_analise_consolidado_dre import ComentarioAnaliseConsolidadoDRE

pytestmark = pytest.mark.django_db


def test_api_reordena_comentarios_consolidado_dre(
    jwt_authenticated_client_sme_teste_comentarios_de_analise_consolidado_dre,
    comentario_analise_consolidado_dre_01,
    comentario_analise_consolidado_dre_02,
    comentario_analise_consolidado_dre_03
):
    payload = {
        'comentarios_de_analise': [
            {
                'uuid': f'{comentario_analise_consolidado_dre_03.uuid}',
                'ordem': 1
            },
            {
                'uuid': f'{comentario_analise_consolidado_dre_01.uuid}',
                'ordem': 2
            },
            {
                'uuid': f'{comentario_analise_consolidado_dre_02.uuid}',
                'ordem': 3
            }
        ]
    }

    url = f'/api/comentarios-de-analises-consolidados-dre/reordenar-comentarios/'

    response = jwt_authenticated_client_sme_teste_comentarios_de_analise_consolidado_dre.patch(
        url,
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK

    comentario_3_atualizado = ComentarioAnaliseConsolidadoDRE.by_uuid(comentario_analise_consolidado_dre_03.uuid)
    assert comentario_3_atualizado.ordem == 1

    comentario_1_atualizado = ComentarioAnaliseConsolidadoDRE.by_uuid(comentario_analise_consolidado_dre_01.uuid)
    assert comentario_1_atualizado.ordem == 2

    comentario_2_atualizado = ComentarioAnaliseConsolidadoDRE.by_uuid(comentario_analise_consolidado_dre_02.uuid)
    assert comentario_2_atualizado.ordem == 3


def test_api_reordena_comentarios_consolidado_dre_exige_payload(
    jwt_authenticated_client_sme_teste_comentarios_de_analise_consolidado_dre,
    comentario_analise_consolidado_dre_01,
    comentario_analise_consolidado_dre_02,
    comentario_analise_consolidado_dre_03
):
    url = f'/api/comentarios-de-analises-consolidados-dre/reordenar-comentarios/'

    response = jwt_authenticated_client_sme_teste_comentarios_de_analise_consolidado_dre.patch(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    result_esperado = {
        'erro': 'falta_de_informacoes',
        'operacao': 'reordenar-comentarios',
        'mensagem': 'Faltou informar o campo comentarios_de_analise no payload.'
    }

    assert result == result_esperado, "Deve retornar erro falta_de_informacoes."


def test_api_reordena_comentarios_consolidado_dre_valida_uuids_comentarios(
    jwt_authenticated_client_sme_teste_comentarios_de_analise_consolidado_dre,
    comentario_analise_consolidado_dre_01,
    comentario_analise_consolidado_dre_02,
    comentario_analise_consolidado_dre_03
):
    payload = {
        'comentarios_de_analise': [
            {
                'uuid': f'{comentario_analise_consolidado_dre_03.uuid}XXX',  # Uuid Inválido
                'ordem': 1
            },
            {
                'uuid': f'{comentario_analise_consolidado_dre_01.uuid}',
                'ordem': 2
            },
            {
                'uuid': f'{comentario_analise_consolidado_dre_02.uuid}',
                'ordem': 3
            }
        ]
    }

    url = f'/api/comentarios-de-analises-consolidados-dre/reordenar-comentarios/'

    response = jwt_authenticated_client_sme_teste_comentarios_de_analise_consolidado_dre.patch(
        url,
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    result_esperado = {
        'erro': 'Objeto não encontrado.',
        'mensagem': 'Algum comentário da lista não foi encontrado pelo uuid informado.'
    }

    assert result == result_esperado, "Deveria ter retornado erro falta_de_informacoes."

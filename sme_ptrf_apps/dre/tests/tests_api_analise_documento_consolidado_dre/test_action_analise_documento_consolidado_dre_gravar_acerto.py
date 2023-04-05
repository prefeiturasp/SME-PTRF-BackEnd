import json
import pytest
from rest_framework import status

from ...models import AnaliseDocumentoConsolidadoDre

pytestmark = pytest.mark.django_db


def test_action_gravar_acerto_nao_deve_passar_uuid_documento_invalido(
    jwt_authenticated_client_relatorio_consolidado,
    analise_consolidado_dre_01,
    relatorio_consolidado_dre_01,
    analise_documento_consolidado_dre_gravar_acerto,
):
    uuid_analise_consolidado = f"{analise_consolidado_dre_01.uuid}"
    tipo_documento = 'RELATORIO_CONSOLIDADO'
    uuid_documento_invalido = f"{relatorio_consolidado_dre_01.uuid}XXX"

    payload = {
        "analise_atual_consolidado": f"{uuid_analise_consolidado}",
        "tipo_documento": tipo_documento,
        "documento": uuid_documento_invalido,  # UUID Documento Inválido
        "detalhamento": "Este é o novo detalhamento XXXXXXXXXXXx"
    }

    response = jwt_authenticated_client_relatorio_consolidado.post(
        f'/api/analises-documentos-consolidados-dre/gravar-acerto/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    result = json.loads(response.content)

    esperado = {
        "erro": "erro_ao_gravar_acerto",
        "mensagem": f"Não foi possível gravar o acerto para o Documento {uuid_documento_invalido} Tipo de Documento {tipo_documento}"
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == esperado


def test_action_gravar_acerto_nao_deve_passar_tipo_documento_invalido(
    jwt_authenticated_client_relatorio_consolidado,
    analise_consolidado_dre_01,
    relatorio_consolidado_dre_01,
    analise_documento_consolidado_dre_gravar_acerto,
):
    uuid_analise_consolidado = f"{analise_consolidado_dre_01.uuid}"

    tipo_documento_invalido = 'RELATORIO_CONSOLIDADOXX'

    payload = {
        "analise_atual_consolidado": f"{uuid_analise_consolidado}",
        "tipo_documento": tipo_documento_invalido,  # TIPO_DOCUMENTO Inválido
        "documento": f"{relatorio_consolidado_dre_01.uuid}",
        "detalhamento": "Este é o novo detalhamento XXXXXXXXXXXx"
    }

    response = jwt_authenticated_client_relatorio_consolidado.post(
        f'/api/analises-documentos-consolidados-dre/gravar-acerto/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    result = json.loads(response.content)

    esperado = {
        "erro": "tipo_de_documento_inválido",
        "mensagem": f"O tipo de documento {tipo_documento_invalido} é inválido as opções são: RELATORIO_CONSOLIDADO, ATA_PARECER_TECNICO ou DOCUMENTO_ADICIONAL"
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == esperado


def test_action_gravar_acerto_nao_deve_passar_analise_consolidado_dre_inexistente(
    jwt_authenticated_client_relatorio_consolidado,
    analise_consolidado_dre_01,
    relatorio_consolidado_dre_01,
    analise_documento_consolidado_dre_gravar_acerto,
):
    uuid_analise_consolidado_invalido = f"{analise_consolidado_dre_01.uuid}xx"

    payload = {
        "analise_atual_consolidado": f"{uuid_analise_consolidado_invalido}",  # UUID Inválido
        "tipo_documento": "RELATORIO_CONSOLIDADO",
        "documento": f"{relatorio_consolidado_dre_01.uuid}",
        "detalhamento": "Este é o novo detalhamento XXXXXXXXXXXx"
    }

    response = jwt_authenticated_client_relatorio_consolidado.post(
        f'/api/analises-documentos-consolidados-dre/gravar-acerto/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    result = json.loads(response.content)

    esperado = {
        "erro": "Objeto não encontrado.",
        "mensagem": f"O objeto AnaliseConsolidadoDre para o uuid {uuid_analise_consolidado_invalido} não foi encontrado na base."
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == esperado


def test_action_analise_documento_consolidado_dre_gravar_acerto(
    jwt_authenticated_client_relatorio_consolidado,
    analise_consolidado_dre_01,
    relatorio_consolidado_dre_01,
    analise_documento_consolidado_dre_gravar_acerto,
):
    payload = {
        "analise_atual_consolidado": f"{analise_consolidado_dre_01.uuid}",
        "tipo_documento": "RELATORIO_CONSOLIDADO",
        "documento": f"{relatorio_consolidado_dre_01.uuid}",
        "detalhamento": "Este é o novo detalhamento XXXXXXXXXXXx"
    }

    response = jwt_authenticated_client_relatorio_consolidado.post(
        f'/api/analises-documentos-consolidados-dre/gravar-acerto/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    result = json.loads(response.content)

    esperado = {
        "analise_consolidado_dre": f"{analise_consolidado_dre_01.uuid}",
        "ata_parecer_tecnico": None,
        "documento_adicional": None,
        "relatorio_consolidao_dre": f"{relatorio_consolidado_dre_01.uuid}",
        "detalhamento": "Este é o novo detalhamento XXXXXXXXXXXx",
        "resultado": "AJUSTE",
        "uuid": f"{analise_documento_consolidado_dre_gravar_acerto.uuid}"
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado

import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_post_documentos_marcar_como_corretos(
    jwt_authenticated_client_a,
    periodo_2020_1,
    conta_associacao_cartao,
    conta_associacao_cheque,
    tipo_documento_prestacao_conta_ata,
    tipo_documento_prestacao_conta_declaracao,
    tipo_conta_carteira,  # Não pode ser listada
    analise_prestacao_conta_2020_1_em_analise,
):
    prestacao_conta = analise_prestacao_conta_2020_1_em_analise.prestacao_conta

    payload = {
        'analise_prestacao': f'{analise_prestacao_conta_2020_1_em_analise.uuid}',
        'documentos_corretos': [
            {
                'tipo_documento': f'{tipo_documento_prestacao_conta_ata.uuid}',
                'conta_associacao': None,
            },
            {
                'tipo_documento': f'{tipo_documento_prestacao_conta_declaracao.uuid}',
                'conta_associacao': f'{conta_associacao_cartao.uuid}',
            },
        ]
    }

    url = f'/api/prestacoes-contas/{prestacao_conta.uuid}/documentos-corretos/'

    response = jwt_authenticated_client_a.post(url, data=json.dumps(payload), content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == {'message': 'Documentos marcados como corretos.'}

    assert analise_prestacao_conta_2020_1_em_analise.analises_de_documento.count() == 2

    analise_declaracao = analise_prestacao_conta_2020_1_em_analise.analises_de_documento.filter(
        tipo_documento_prestacao_conta=tipo_documento_prestacao_conta_declaracao
    ).first()

    assert analise_declaracao.conta_associacao == conta_associacao_cartao
    assert analise_declaracao.resultado == "CORRETO"

    analise_ata = analise_prestacao_conta_2020_1_em_analise.analises_de_documento.filter(
        tipo_documento_prestacao_conta=tipo_documento_prestacao_conta_ata
    ).first()

    assert analise_ata.conta_associacao is None
    assert analise_ata.resultado == "CORRETO"

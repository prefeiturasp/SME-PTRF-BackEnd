import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_post_documentos_marcar_como_nao_conferidos(
    jwt_authenticated_client_a,
    periodo_2020_1,
    conta_associacao_cartao,
    conta_associacao_cheque,
    tipo_documento_prestacao_conta_ata,
    tipo_documento_prestacao_conta_declaracao,
    tipo_conta_carteira,  # Não pode ser listada
    analise_documento_prestacao_conta_2020_1_ata_correta,
    analise_documento_prestacao_conta_2020_1_declaracao_cartao_correta
):
    analise = analise_documento_prestacao_conta_2020_1_declaracao_cartao_correta.analise_prestacao_conta
    prestacao_conta = analise.prestacao_conta

    payload = {
        'analise_prestacao': f'{analise.uuid}',
        'documentos_nao_conferidos': [
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

    assert analise.analises_de_documento.count() == 2, "Deveria iniciar com duas análises"

    url = f'/api/prestacoes-contas/{prestacao_conta.uuid}/documentos-nao-conferidos/'

    response = jwt_authenticated_client_a.post(url, data=json.dumps(payload), content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == {'message': 'Documentos marcados como não conferidos.'}

    assert analise.analises_de_lancamentos.count() == 0

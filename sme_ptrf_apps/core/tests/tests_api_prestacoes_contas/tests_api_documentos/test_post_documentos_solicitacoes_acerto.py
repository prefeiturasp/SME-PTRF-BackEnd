import json

import pytest

from rest_framework import status

from ....models import SolicitacaoAcertoDocumento

pytestmark = pytest.mark.django_db


def test_api_post_solicitacoes_acerto_documento(
    jwt_authenticated_client_a,
    periodo_2020_1,
    conta_associacao_cartao,
    conta_associacao_cheque,
    tipo_documento_prestacao_conta_ata,
    tipo_documento_prestacao_conta_declaracao,
    tipo_conta_carteira,  # Não pode ser listada
    tipo_acerto_documento_assinatura,
    analise_documento_prestacao_conta_2020_1_declaracao_cartao_correta,
    analise_documento_prestacao_conta_2020_1_ata_correta
):
    analise_prestacao = analise_documento_prestacao_conta_2020_1_declaracao_cartao_correta.analise_prestacao_conta
    prestacao_conta = analise_prestacao.prestacao_conta

    payload = {
        'analise_prestacao': f'{analise_prestacao.uuid}',
        'documentos': [
            {
                'tipo_documento': f'{tipo_documento_prestacao_conta_ata.uuid}',
                'conta_associacao': None,
            },
        ],
        'solicitacoes_acerto': [
            {
                'uuid': None,
                'copiado': False,
                'tipo_acerto': f'{tipo_acerto_documento_assinatura.uuid}',
                'detalhamento': '',
            },
        ]
    }

    assert analise_prestacao.analises_de_documento.count() == 2
    assert not SolicitacaoAcertoDocumento.objects.exists()

    url = f'/api/prestacoes-contas/{prestacao_conta.uuid}/solicitacoes-de-acerto-documento/'
    response = jwt_authenticated_client_a.post(url, data=json.dumps(payload), content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == {'message': 'Solicitações de acerto gravadas para os documentos.'}

    assert analise_prestacao.analises_de_documento.count() == 2
    assert SolicitacaoAcertoDocumento.objects.count() == 1

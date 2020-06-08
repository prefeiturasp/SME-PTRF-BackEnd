import json

import pytest
from rest_framework import status

from ...models import Ata

pytestmark = pytest.mark.django_db


def test_api_get_atas_tabelas(client, ata_2020_1_cheque_aprovada):
    response = client.get('/api/atas-associacao/tabelas/', content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'tipos_ata': [
            {
                'id': Ata.ATA_APRESENTACAO,
                'nome': Ata.ATA_NOMES[Ata.ATA_APRESENTACAO]
            },
            {
                'id': Ata.ATA_RETIFICACAO,
                'nome': Ata.ATA_NOMES[Ata.ATA_RETIFICACAO]
            }
        ],

        'tipos_reuniao': [
            {
                'id': Ata.REUNIAO_ORDINARIA,
                'nome': Ata.REUNIAO_NOMES[Ata.REUNIAO_ORDINARIA]
            },
            {
                'id': Ata.REUNIAO_EXTRAORDINARIA,
                'nome': Ata.REUNIAO_NOMES[Ata.REUNIAO_EXTRAORDINARIA]
            }
        ],

        'convocacoes': [
            {
                'id': Ata.CONVOCACAO_PRIMEIRA,
                'nome': Ata.CONVOCACAO_NOMES[Ata.CONVOCACAO_PRIMEIRA]
            },
            {
                'id': Ata.CONVOCACAO_SEGUNDA,
                'nome': Ata.CONVOCACAO_NOMES[Ata.CONVOCACAO_SEGUNDA]
            }
        ],

        'pareceres': [
            {
                'id': Ata.PARECER_APROVADA,
                'nome': Ata.PARECER_NOMES[Ata.PARECER_APROVADA]
            },
            {
                'id': Ata.PARECER_REJEITADA,
                'nome': Ata.PARECER_NOMES[Ata.PARECER_REJEITADA]
            },
            {
                'id': Ata.PARECER_RESSALVAS,
                'nome': Ata.PARECER_NOMES[Ata.PARECER_RESSALVAS]
            }
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado

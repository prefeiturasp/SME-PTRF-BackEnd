import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_retrieve_ata_parecer_tecnico(jwt_authenticated_client_dre, ata_parecer_tecnico):
    response = jwt_authenticated_client_dre.get(f'/api/ata-parecer-tecnico/{ata_parecer_tecnico.uuid}/',
                                              content_type='application/json')
    
    result = json.loads(response.content)

    result_esperado = {
        'alterado_em': None,
        'arquivo_pdf': None,
        'comentarios': 'Teste',
        'data_reuniao': '2020-07-01',
        'dre': {'codigo_eol': ata_parecer_tecnico.dre.codigo_eol,
                'dre': None,
                'nome': ata_parecer_tecnico.dre.nome,
                'nome_com_tipo': f"{ata_parecer_tecnico.dre.nome_com_tipo}",
                'sigla': ata_parecer_tecnico.dre.sigla,
                'tipo_unidade': 'DRE',
                'uuid': f'{ata_parecer_tecnico.dre.uuid}'},
        'eh_retificacao': False,
        'local_reuniao': 'Escola Teste',
        'motivo_retificacao': None,
        'numero_ata': 1,
        'periodo': {'data_fim_realizacao_despesas': '2019-11-30',
                    'data_inicio_realizacao_despesas': '2019-09-01',
                    'referencia': '2019.2',
                    'referencia_por_extenso': '2° repasse de 2019',
                    'id': ata_parecer_tecnico.periodo.id,
                    'uuid': f'{ata_parecer_tecnico.periodo.uuid}',
                    'recurso': {
                        'id': ata_parecer_tecnico.periodo.recurso.id,
                        'uuid': f'{ata_parecer_tecnico.periodo.recurso.uuid}',
                        'ativo': True,
                        'cor': ata_parecer_tecnico.periodo.recurso.cor,
                        'icone': None,
                        'legado': True,
                        'nome': ata_parecer_tecnico.periodo.recurso.nome,
                        'nome_exibicao': ata_parecer_tecnico.periodo.recurso.nome_exibicao,
                        'criado_em': result['periodo']['recurso']['criado_em'],
                        'alterado_em': result['periodo']['recurso']['alterado_em'],
                        'exibe_valores_reprogramados': ata_parecer_tecnico.periodo.recurso.exibe_valores_reprogramados,
                    }},
        'presentes_na_ata': [],
        'status_geracao_pdf': 'NAO_GERADO',
        'uuid': f'{ata_parecer_tecnico.uuid}',
        'hora_reuniao': '00:00',
        'data_portaria': None,
        'numero_portaria': None,
        'versao': 'PREVIA'
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado

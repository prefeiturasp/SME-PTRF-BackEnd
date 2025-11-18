import datetime
import json

import pytest
from rest_framework import status

from sme_ptrf_apps.paa.models import AtaPaa

pytestmark = pytest.mark.django_db


def test_api_retrieve_ata_paa(jwt_authenticated_client_sme, flag_paa, ata_paa):
    response = jwt_authenticated_client_sme.get(f'/api/atas-paa/{ata_paa.uuid}/', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result['uuid'] == str(ata_paa.uuid)
    assert result['nome'] == 'Ata de Apresentação do PAA'
    assert result['tipo_ata'] == AtaPaa.ATA_APRESENTACAO
    assert result['tipo_reuniao'] == AtaPaa.REUNIAO_ORDINARIA
    assert result['convocacao'] == AtaPaa.CONVOCACAO_PRIMEIRA
    assert result['parecer_conselho'] == AtaPaa.PARECER_APROVADA
    assert 'associacao' in result
    assert 'paa' in result
    assert 'presentes_na_ata_paa' in result


def test_api_update_ata_paa(jwt_authenticated_client_sme, flag_paa, ata_paa):
    """Testa atualizar ata PAA sem presentes"""
    payload = {
        "tipo_reuniao": "EXTRAORDINARIA",
        "convocacao": "SEGUNDA",
        "data_reuniao": "2025-06-20",
        "local_reuniao": "Sala XXX",
        "parecer_conselho": "REJEITADA",
        "comentarios": "TesteXXX",
        "presentes_na_ata_paa": [],
    }

    response = jwt_authenticated_client_sme.patch(
        f'/api/atas-paa/{ata_paa.uuid}/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    registro_alterado = AtaPaa.by_uuid(uuid=ata_paa.uuid)

    assert response.status_code == status.HTTP_200_OK
    assert registro_alterado.tipo_reuniao == 'EXTRAORDINARIA'
    assert registro_alterado.convocacao == "SEGUNDA"
    assert registro_alterado.data_reuniao == datetime.date(2025, 6, 20)
    assert registro_alterado.local_reuniao == "Sala XXX"
    assert registro_alterado.parecer_conselho == "REJEITADA"
    assert registro_alterado.comentarios == "TesteXXX"


def test_api_update_ata_paa_com_presentes(jwt_authenticated_client_sme, flag_paa, ata_paa):
    """Testa atualizar ata PAA criando presentes automaticamente"""
    from sme_ptrf_apps.paa.models import ParticipanteAtaPaa
    
    payload = {
        "tipo_reuniao": "ORDINARIA",
        "convocacao": "PRIMEIRA",
        "data_reuniao": "2025-06-20",
        "hora_reuniao": "14:00",
        "local_reuniao": "Sala de Reuniões",
        "parecer_conselho": "APROVADA",
        "comentarios": "Reunião de teste com presentes",
        "presentes_na_ata_paa": [
            {
                "nome": "João Silva",
                "identificacao": "1234567",
                "cargo": "Presidente da diretoria executiva",
                "membro": True,
                "presente": True,
                "presidente_da_reuniao": True,
                "secretario_da_reuniao": False,
                "conselho_fiscal": False,
                "professor_gremio": False
            },
            {
                "nome": "Maria Santos",
                "identificacao": "7654321",
                "cargo": "Secretário",
                "membro": True,
                "presente": True,
                "presidente_da_reuniao": False,
                "secretario_da_reuniao": True,
                "conselho_fiscal": False,
                "professor_gremio": False
            },
            {
                "nome": "Pedro Oliveira",
                "identificacao": "9876543",
                "cargo": "Tesoureiro",
                "membro": True,
                "presente": True,
                "presidente_da_reuniao": False,
                "secretario_da_reuniao": False,
                "conselho_fiscal": False,
                "professor_gremio": False
            }
        ]
    }

    # Verifica que não há presentes antes
    assert ata_paa.presentes_na_ata_paa.count() == 0

    response = jwt_authenticated_client_sme.patch(
        f'/api/atas-paa/{ata_paa.uuid}/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
    
    # Recarrega a ata do banco
    registro_alterado = AtaPaa.by_uuid(uuid=ata_paa.uuid)
    
    # Verifica os dados da ata
    assert registro_alterado.tipo_reuniao == 'ORDINARIA'
    assert registro_alterado.convocacao == "PRIMEIRA"
    assert registro_alterado.data_reuniao == datetime.date(2025, 6, 20)
    assert registro_alterado.local_reuniao == "Sala de Reuniões"
    assert registro_alterado.parecer_conselho == "APROVADA"
    assert registro_alterado.comentarios == "Reunião de teste com presentes"
    
    # Verifica que os presentes foram criados
    assert registro_alterado.presentes_na_ata_paa.count() == 3
    
    # Verifica os presentes criados
    presentes = registro_alterado.presentes_na_ata_paa.all()
    nomes_presentes = [p.nome for p in presentes]
    assert "João Silva" in nomes_presentes
    assert "Maria Santos" in nomes_presentes
    assert "Pedro Oliveira" in nomes_presentes
    
    # Verifica presidente e secretário
    assert registro_alterado.presidente_da_reuniao is not None
    assert registro_alterado.presidente_da_reuniao.nome == "João Silva"
    assert registro_alterado.secretario_da_reuniao is not None
    assert registro_alterado.secretario_da_reuniao.nome == "Maria Santos"
    
    # Verifica dados de um presente específico
    joao = presentes.get(nome="João Silva")
    assert joao.identificacao == "1234567"
    assert joao.cargo == "Presidente da diretoria executiva"
    assert joao.membro is True
    assert joao.presente is True


def test_api_get_atas_paa_tabelas(jwt_authenticated_client_sme, flag_paa, ata_paa):
    response = jwt_authenticated_client_sme.get('/api/atas-paa/tabelas/', content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'tipos_ata': [
            {
                'id': AtaPaa.ATA_APRESENTACAO,
                'nome': AtaPaa.ATA_NOMES[AtaPaa.ATA_APRESENTACAO]
            }
        ],
        'tipos_reuniao': [
            {
                'id': AtaPaa.REUNIAO_ORDINARIA,
                'nome': AtaPaa.REUNIAO_NOMES[AtaPaa.REUNIAO_ORDINARIA]
            },
            {
                'id': AtaPaa.REUNIAO_EXTRAORDINARIA,
                'nome': AtaPaa.REUNIAO_NOMES[AtaPaa.REUNIAO_EXTRAORDINARIA]
            }
        ],
        'convocacoes': [
            {
                'id': AtaPaa.CONVOCACAO_PRIMEIRA,
                'nome': AtaPaa.CONVOCACAO_NOMES[AtaPaa.CONVOCACAO_PRIMEIRA]
            },
            {
                'id': AtaPaa.CONVOCACAO_SEGUNDA,
                'nome': AtaPaa.CONVOCACAO_NOMES[AtaPaa.CONVOCACAO_SEGUNDA]
            }
        ],
        'pareceres': [
            {
                'id': AtaPaa.PARECER_APROVADA,
                'nome': AtaPaa.PARECER_NOMES[AtaPaa.PARECER_APROVADA]
            },
            {
                'id': AtaPaa.PARECER_REJEITADA,
                'nome': AtaPaa.PARECER_NOMES[AtaPaa.PARECER_REJEITADA]
            }
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


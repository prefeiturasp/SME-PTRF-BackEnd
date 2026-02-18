import pytest
from datetime import timedelta, date
from unittest.mock import patch, MagicMock

from sme_ptrf_apps.paa.api.serializers.ata_paa_serializer import (
    AtaPaaLookUpSerializer, AtaPaaSerializer, PresentesAtaPaaCreateSerializer, AtaPaaCreateSerializer)
from sme_ptrf_apps.paa.models import AtaPaa
from sme_ptrf_apps.despesas.status_cadastro_completo import STATUS_COMPLETO

pytestmark = pytest.mark.django_db


def test_lookup_serializer(ata_paa):
    serializer = AtaPaaLookUpSerializer(ata_paa)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['nome']
    assert serializer.data['alterado_em'] is None


def test_serializer(ata_paa):
    serializer = AtaPaaSerializer(ata_paa)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['paa']
    assert serializer.data['associacao']
    assert serializer.data['tipo_ata']
    assert serializer.data['tipo_reuniao']
    assert serializer.data['convocacao']
    assert serializer.data['data_reuniao']
    assert serializer.data['local_reuniao']
    assert serializer.data['comentarios']
    assert serializer.data['parecer_conselho']
    assert serializer.data['nome']
    assert serializer.data['hora_reuniao'] == "00:00"
    assert serializer.data['justificativa'] == ""
    assert 'precisa_professor_gremio' in serializer.data
    assert isinstance(serializer.data['precisa_professor_gremio'], bool)


def test_serializer_precisa_professor_gremio_true(
        ata_paa, parametros, acao_factory, acao_associacao_factory, despesa_factory, rateio_despesa_factory):
    """Testa se serializer retorna precisa_professor_gremio=True quando unidade precisa e há
      despesas completas com ação grêmio no período"""
    parametros.tipos_unidades_professor_gremio = ['EMEF']
    parametros.save()

    ata_paa.paa.associacao.unidade.tipo_unidade = 'EMEF'
    ata_paa.paa.associacao.unidade.save()

    # Cria ação "Orçamento Grêmio Estudantil"
    acao_gremio = acao_factory.create(nome='Orçamento Grêmio Estudantil')
    acao_associacao_gremio = acao_associacao_factory.create(
        associacao=ata_paa.paa.associacao,
        acao=acao_gremio,
        status='ATIVA'
    )

    # Cria despesa completa no período do PAA
    periodo_paa = ata_paa.paa.periodo_paa
    despesa = despesa_factory.create(
        associacao=ata_paa.paa.associacao,
        data_transacao=periodo_paa.data_inicial + timedelta(days=1),
        status=STATUS_COMPLETO
    )

    # Cria rateio completo com a ação do grêmio
    rateio_despesa_factory.create(
        despesa=despesa,
        associacao=ata_paa.paa.associacao,
        acao_associacao=acao_associacao_gremio
    )

    serializer = AtaPaaSerializer(ata_paa)
    assert serializer.data['precisa_professor_gremio'] is True


def test_serializer_precisa_professor_gremio_false(ata_paa, parametros):
    """Testa se serializer retorna precisa_professor_gremio=False quando unidade não precisa"""
    parametros.tipos_unidades_professor_gremio = []
    parametros.save()

    serializer = AtaPaaSerializer(ata_paa)
    assert serializer.data['precisa_professor_gremio'] is False


def test_update_participante_sem_presidente_nem_secretario(
    participante_ata_paa,
    ata_paa
):
    """Testa update de participante sem definir presidente ou secretário"""
    participante_ata_paa.ata_paa = ata_paa
    participante_ata_paa.save()

    serializer = PresentesAtaPaaCreateSerializer(instance=participante_ata_paa)

    validated_data = {
        'nome': 'João Silva Atualizado',
        'cargo': 'Presidente Atualizado',
        'presente': True
    }

    updated_participante = serializer.update(participante_ata_paa, validated_data)

    assert updated_participante.nome == 'João Silva Atualizado'
    assert updated_participante.cargo == 'Presidente Atualizado'
    assert updated_participante.presente is True
    assert ata_paa.presidente_da_reuniao != updated_participante
    assert ata_paa.secretario_da_reuniao != updated_participante


def test_update_participante_como_presidente_da_reuniao(
    participante_ata_paa,
    ata_paa
):
    """Testa update de participante definindo como presidente da reunião"""
    participante_ata_paa.ata_paa = ata_paa
    participante_ata_paa.save()

    serializer = PresentesAtaPaaCreateSerializer(instance=participante_ata_paa)

    validated_data = {
        'nome': 'João Silva',
        'cargo': 'Presidente',
        'presidente_da_reuniao': True
    }

    updated_participante = serializer.update(participante_ata_paa, validated_data)

    ata_paa.refresh_from_db()

    assert updated_participante.nome == 'João Silva'
    assert updated_participante.cargo == 'Presidente'
    assert ata_paa.presidente_da_reuniao == updated_participante
    assert ata_paa.secretario_da_reuniao != updated_participante


def test_update_participante_como_secretario_da_reuniao(
    participante_ata_paa,
    ata_paa
):
    """Testa update de participante definindo como secretário da reunião"""
    participante_ata_paa.ata_paa = ata_paa
    participante_ata_paa.save()

    serializer = PresentesAtaPaaCreateSerializer(instance=participante_ata_paa)

    validated_data = {
        'nome': 'Maria Santos',
        'cargo': 'Secretária',
        'secretario_da_reuniao': True
    }

    updated_participante = serializer.update(participante_ata_paa, validated_data)

    ata_paa.refresh_from_db()

    assert updated_participante.nome == 'Maria Santos'
    assert updated_participante.cargo == 'Secretária'
    assert ata_paa.secretario_da_reuniao == updated_participante
    assert ata_paa.presidente_da_reuniao != updated_participante


def test_create_ata_paa_sem_presentes(paa):
    """Testa criação de ata PAA sem participantes"""
    validated_data = {
        'paa': paa,
        'tipo_ata': AtaPaa.ATA_APRESENTACAO,
        'tipo_reuniao': AtaPaa.REUNIAO_ORDINARIA,
        'data_reuniao': date(2025, 2, 5),
        'local_reuniao': 'Escola Municipal',
        'comentarios': 'Primeira reunião'
    }

    serializer = AtaPaaCreateSerializer()
    ata_paa = serializer.create(validated_data)

    assert ata_paa.paa == paa
    assert ata_paa.tipo_ata == AtaPaa.ATA_APRESENTACAO
    assert ata_paa.data_reuniao == date(2025, 2, 5)
    assert ata_paa.local_reuniao == 'Escola Municipal'
    assert ata_paa.presentes_na_ata_paa.count() == 0
    assert ata_paa.presidente_da_reuniao is None
    assert ata_paa.secretario_da_reuniao is None


@patch('sme_ptrf_apps.paa.api.serializers.ata_paa_serializer.get_waffle_flag_model')
def test_create_ata_paa_com_presentes(mock_waffle, paa):
    """Testa criação de ata PAA com participantes"""
    mock_flag_model = MagicMock()
    mock_flag = MagicMock()
    mock_flag.name = 'historico-de-membros'
    mock_flag.everyone = True
    mock_flag_model.objects.filter.return_value.exists.return_value = True
    mock_waffle.return_value = mock_flag_model
    validated_data = {
        'paa': paa,
        'tipo_ata': AtaPaa.ATA_APRESENTACAO,
        'data_reuniao': date(2025, 2, 5),
        'presentes_na_ata_paa': [
            {
                'nome': 'João Silva',
                'cargo': 'Membro',
                'identificacao': '12345678900',
                'membro': True,
                'presente': True
            },
            {
                'nome': 'Maria Santos',
                'cargo': 'Membro',
                'identificacao': '98765432100',
                'membro': True,
                'presente': True
            }
        ]
    }

    serializer = AtaPaaCreateSerializer()
    ata_paa = serializer.create(validated_data)

    assert ata_paa.presentes_na_ata_paa.count() == 2
    assert ata_paa.presentes_na_ata_paa.filter(nome='João Silva').exists()
    assert ata_paa.presentes_na_ata_paa.filter(nome='Maria Santos').exists()


def test_create_ata_paa_define_presidente_da_reuniao(paa):
    """Testa criação de ata PAA com presidente da reunião"""
    validated_data = {
        'paa': paa,
        'tipo_ata': AtaPaa.ATA_APRESENTACAO,
        'data_reuniao': date(2025, 2, 5),
        'presentes_na_ata_paa': [
            {
                'nome': 'João Silva',
                'cargo': 'Presidente',
                'identificacao': '12345678900',
                'membro': True,
                'presente': True,
                'presidente_da_reuniao': True
            },
            {
                'nome': 'Maria Santos',
                'cargo': 'Membro',
                'identificacao': '98765432100',
                'membro': True,
                'presente': True
            }
        ]
    }

    serializer = AtaPaaCreateSerializer()
    ata_paa = serializer.create(validated_data)

    assert ata_paa.presidente_da_reuniao is not None
    assert ata_paa.presidente_da_reuniao.nome == 'João Silva'


def test_create_ata_paa_define_secretario_da_reuniao(paa):
    """Testa criação de ata PAA com secretário da reunião"""
    validated_data = {
        'paa': paa,
        'tipo_ata': AtaPaa.ATA_APRESENTACAO,
        'data_reuniao': date(2025, 2, 5),
        'presentes_na_ata_paa': [
            {
                'nome': 'João Silva',
                'cargo': 'Membro',
                'identificacao': '12345678900',
                'membro': True,
                'presente': True
            },
            {
                'nome': 'Maria Santos',
                'cargo': 'Secretária',
                'identificacao': '98765432100',
                'membro': True,
                'presente': True,
                'secretario_da_reuniao': True
            }
        ]
    }

    serializer = AtaPaaCreateSerializer()
    ata_paa = serializer.create(validated_data)

    assert ata_paa.secretario_da_reuniao is not None
    assert ata_paa.secretario_da_reuniao.nome == 'Maria Santos'


@patch('sme_ptrf_apps.paa.api.serializers.ata_paa_serializer.get_waffle_flag_model')
def test_create_ata_paa_define_presidente_da_reuniao_com_flag_historico(mock_waffle, paa):
    """Testa criação de ata PAA com presidente da reunião"""
    mock_flag_model = MagicMock()
    mock_flag = MagicMock()
    mock_flag.name = 'historico-de-membros'
    mock_flag.everyone = True
    mock_waffle.return_value = mock_flag_model
    mock_flag_model.objects.filter.return_value.exists.return_value = True
    validated_data = {
        'paa': paa,
        'tipo_ata': AtaPaa.ATA_APRESENTACAO,
        'data_reuniao': date(2025, 2, 5),
        'presentes_na_ata_paa': [
            {
                'nome': 'João Silva',
                'cargo': 'Presidente',
                'identificacao': '12345678900',
                'membro': True,
                'presente': True,
                'presidente_da_reuniao': True
            },
            {
                'nome': 'Maria Santos',
                'cargo': 'Membro',
                'identificacao': '98765432100',
                'membro': True,
                'presente': True
            }
        ]
    }

    serializer = AtaPaaCreateSerializer()
    ata_paa = serializer.create(validated_data)

    assert ata_paa.presidente_da_reuniao is not None
    assert ata_paa.presidente_da_reuniao.nome == 'João Silva'


@patch('sme_ptrf_apps.paa.api.serializers.ata_paa_serializer.get_waffle_flag_model')
def test_create_ata_paa_define_secretario_da_reuniao_com_flag_historico(mock_waffle, paa):
    """Testa criação de ata PAA com secretário da reunião"""
    mock_flag_model = MagicMock()
    mock_flag = MagicMock()
    mock_flag.name = 'historico-de-membros'
    mock_flag.everyone = True
    mock_flag_model.objects.filter.return_value.exists.return_value = True
    mock_waffle.return_value = mock_flag_model
    validated_data = {
        'paa': paa,
        'tipo_ata': AtaPaa.ATA_APRESENTACAO,
        'data_reuniao': date(2025, 2, 5),
        'presentes_na_ata_paa': [
            {
                'nome': 'João Silva',
                'cargo': 'Membro',
                'identificacao': '12345678900',
                'membro': True,
                'presente': True
            },
            {
                'nome': 'Maria Santos',
                'cargo': 'Secretária',
                'identificacao': '98765432100',
                'membro': True,
                'presente': True,
                'secretario_da_reuniao': True
            }
        ]
    }

    serializer = AtaPaaCreateSerializer()
    ata_paa = serializer.create(validated_data)

    assert ata_paa.secretario_da_reuniao is not None
    assert ata_paa.secretario_da_reuniao.nome == 'Maria Santos'


@patch('sme_ptrf_apps.paa.api.serializers.ata_paa_serializer.get_waffle_flag_model')
def test_create_ata_paa_com_waffle_flag_historico_membros_ativo(mock_waffle, paa, associacao, composicao_factory):
    """Testa criação com waffle flag historico-de-membros ativo"""
    mock_flag_model = MagicMock()
    mock_flag = MagicMock()
    mock_flag.name = 'historico-de-membros'
    mock_flag.everyone = True
    mock_flag_model.objects.filter.return_value.exists.return_value = True
    mock_waffle.return_value = mock_flag_model
    # Cria uma composição real
    composicao = composicao_factory.create()

    validated_data = {
        'paa': paa,
        'tipo_ata': AtaPaa.ATA_APRESENTACAO,
        'data_reuniao': date(2025, 2, 5),
        'presentes_na_ata_paa': []
    }

    with patch('sme_ptrf_apps.paa.api.serializers.ata_paa_serializer.ServicoRecuperaComposicaoPorData') as mock_servico:
        mock_servico.return_value.get_composicao_por_data_e_associacao.return_value = composicao

        serializer = AtaPaaCreateSerializer()
        ata_paa = serializer.create(validated_data)

        assert ata_paa.composicao == composicao
        mock_servico.return_value.get_composicao_por_data_e_associacao.assert_called_once_with(
            date(2025, 2, 5),
            paa.associacao
        )


def test_update_ata_paa_sem_presentes(ata_paa):
    """Testa update de ata PAA sem alterar participantes"""
    validated_data = {
        'local_reuniao': 'Nova Localização',
        'comentarios': 'Comentários atualizados',
        'data_reuniao': date(2025, 2, 5)
    }

    serializer = AtaPaaCreateSerializer()
    ata_paa_atualizada = serializer.update(ata_paa, validated_data)

    assert ata_paa_atualizada.local_reuniao == 'Nova Localização'
    assert ata_paa_atualizada.comentarios == 'Comentários atualizados'


@patch('sme_ptrf_apps.paa.api.serializers.ata_paa_serializer.get_waffle_flag_model')
def test_update_ata_paa_sem_presentes_com_flag_historico(mock_waffle, ata_paa):
    mock_flag_model = MagicMock()
    mock_flag = MagicMock()
    mock_flag.name = 'historico-de-membros'
    mock_flag.everyone = True
    mock_flag_model.objects.filter.return_value.exists.return_value = True
    mock_waffle.return_value = mock_flag_model
    validated_data = {
        'local_reuniao': 'Nova Localização',
        'comentarios': 'Comentários atualizados',
        'data_reuniao': date(2025, 2, 5)
    }

    serializer = AtaPaaCreateSerializer()
    ata_paa_atualizada = serializer.update(ata_paa, validated_data)

    assert ata_paa_atualizada.local_reuniao == 'Nova Localização'
    assert ata_paa_atualizada.comentarios == 'Comentários atualizados'


def test_update_ata_paa_adiciona_novos_presentes(ata_paa):
    """Testa que novos participantes são adicionados"""
    validated_data = {
        'presentes_na_ata_paa': [
            {
                'nome': 'João Silva',
                'cargo': 'Membro',
                'identificacao': '12345678900',
                'membro': True
            },
            {
                'nome': 'Maria Santos',
                'cargo': 'Membro',
                'identificacao': '98765432100',
                'membro': True
            }
        ]
    }

    serializer = AtaPaaCreateSerializer()
    ata_paa_atualizada = serializer.update(ata_paa, validated_data)

    assert ata_paa_atualizada.presentes_na_ata_paa.count() == 2
    assert ata_paa_atualizada.presentes_na_ata_paa.filter(nome='João Silva').exists()
    assert ata_paa_atualizada.presentes_na_ata_paa.filter(nome='Maria Santos').exists()


@patch('sme_ptrf_apps.paa.api.serializers.ata_paa_serializer.get_waffle_flag_model')
def test_update_ata_paa_adiciona_novos_presentes_com_flag_historico(mock_waffle, ata_paa):
    mock_flag_model = MagicMock()
    mock_flag = MagicMock()
    mock_flag.name = 'historico-de-membros'
    mock_flag.everyone = True
    mock_flag_model.objects.filter.return_value.exists.return_value = True
    mock_waffle.return_value = mock_flag_model
    """Testa que novos participantes são adicionados"""
    validated_data = {
        'presentes_na_ata_paa': [
            {
                'nome': 'João Silva',
                'cargo': 'Membro',
                'identificacao': '12345678900',
                'membro': True
            },
            {
                'nome': 'Maria Santos',
                'cargo': 'Membro',
                'identificacao': '98765432100',
                'membro': True
            }
        ]
    }

    serializer = AtaPaaCreateSerializer()
    ata_paa_atualizada = serializer.update(ata_paa, validated_data)

    assert ata_paa_atualizada.presentes_na_ata_paa.count() == 2
    assert ata_paa_atualizada.presentes_na_ata_paa.filter(nome='João Silva').exists()
    assert ata_paa_atualizada.presentes_na_ata_paa.filter(nome='Maria Santos').exists()


def test_update_ata_paa_define_novo_presidente(ata_paa):
    """Testa definição de novo presidente da reunião"""
    validated_data = {
        'presentes_na_ata_paa': [
            {
                'nome': 'João Silva',
                'cargo': 'Presidente',
                'identificacao': '12345678900',
                'presidente_da_reuniao': True
            }
        ]
    }

    serializer = AtaPaaCreateSerializer()
    ata_paa_atualizada = serializer.update(ata_paa, validated_data)

    assert ata_paa_atualizada.presidente_da_reuniao is not None
    assert ata_paa_atualizada.presidente_da_reuniao.nome == 'João Silva'


@patch('sme_ptrf_apps.paa.api.serializers.ata_paa_serializer.get_waffle_flag_model')
def test_update_ata_paa_define_novo_presidente_com_flag_historico(mock_waffle, ata_paa):
    mock_flag_model = MagicMock()
    mock_flag = MagicMock()
    mock_flag.name = 'historico-de-membros'
    mock_flag.everyone = True
    mock_flag_model.objects.filter.return_value.exists.return_value = True
    mock_waffle.return_value = mock_flag_model
    """ Testa definição de novo presidente da reunião """
    validated_data = {
        'presentes_na_ata_paa': [
            {
                'nome': 'João Silva',
                'cargo': 'Presidente',
                'identificacao': '12345678900',
                'presidente_da_reuniao': True
            }
        ]
    }

    serializer = AtaPaaCreateSerializer()
    ata_paa_atualizada = serializer.update(ata_paa, validated_data)

    assert ata_paa_atualizada.presidente_da_reuniao is not None
    assert ata_paa_atualizada.presidente_da_reuniao.nome == 'João Silva'


def test_update_ata_paa_define_novo_secretario(ata_paa):
    """ Testa definição de novo secretário da reunião """
    validated_data = {
        'presentes_na_ata_paa': [
            {
                'nome': 'Maria Santos',
                'cargo': 'Secretária',
                'identificacao': '98765432100',
                'secretario_da_reuniao': True
            }
        ]
    }

    serializer = AtaPaaCreateSerializer()
    ata_paa_atualizada = serializer.update(ata_paa, validated_data)

    assert ata_paa_atualizada.secretario_da_reuniao is not None
    assert ata_paa_atualizada.secretario_da_reuniao.nome == 'Maria Santos'


@patch('sme_ptrf_apps.paa.api.serializers.ata_paa_serializer.get_waffle_flag_model')
def test_update_ata_paa_define_novo_secretario_com_flag_historico(mock_waffle, ata_paa):
    mock_flag_model = MagicMock()
    mock_flag = MagicMock()
    mock_flag.name = 'historico-de-membros'
    mock_flag.everyone = True
    mock_flag_model.objects.filter.return_value.exists.return_value = True
    mock_waffle.return_value = mock_flag_model
    """Testa definição de novo secretário da reunião"""
    validated_data = {
        'presentes_na_ata_paa': [
            {
                'nome': 'Maria Santos',
                'cargo': 'Secretária',
                'identificacao': '98765432100',
                'secretario_da_reuniao': True
            }
        ]
    }

    serializer = AtaPaaCreateSerializer()
    ata_paa_atualizada = serializer.update(ata_paa, validated_data)

    assert ata_paa_atualizada.secretario_da_reuniao is not None
    assert ata_paa_atualizada.secretario_da_reuniao.nome == 'Maria Santos'

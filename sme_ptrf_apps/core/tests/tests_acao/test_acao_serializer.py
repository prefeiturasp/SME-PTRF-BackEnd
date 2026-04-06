import pytest
from unittest.mock import patch

from sme_ptrf_apps.core.models import Recurso
from ...api.serializers.acao_serializer import AcaoSerializer

pytestmark = pytest.mark.django_db


def test_serializer(acao):

    serializer = AcaoSerializer(acao)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['nome']
    assert not serializer.data['e_recursos_proprios']
    assert serializer.data['uuid']
    assert serializer.data['posicao_nas_pesquisas'] is not None


def test_serializer_create_valido():
    recurso = Recurso.objects.get(legado=True)
    data = {
        'nome': 'Acao Criada Serializer',
        'recurso': str(recurso.uuid),
        'aceita_capital': True,
        'aceita_custeio': False,
        'aceita_livre': True,
        'e_recursos_proprios': False,
        'posicao_nas_pesquisas': 'AAAA',
        'exibir_paa': True,
    }
    serializer = AcaoSerializer(data=data)

    assert serializer.is_valid(), serializer.errors
    acao = serializer.save()
    assert acao.nome == 'Acao Criada Serializer'
    assert acao.aceita_capital is True
    assert acao.aceita_livre is True
    assert acao.recurso == recurso


def test_serializer_create_sem_nome_invalido():
    recurso = Recurso.objects.get(legado=True)
    data = {'recurso': str(recurso.uuid)}
    serializer = AcaoSerializer(data=data)

    assert not serializer.is_valid()
    assert 'nome' in serializer.errors


def test_serializer_update_exibir_paa_false_chama_desabilitar(acao):
    with patch(
        'sme_ptrf_apps.core.api.serializers.acao_serializer.desabilitar_acao_ptrf_paa'
    ) as mock_desabilitar:
        serializer = AcaoSerializer(acao, data={'exibir_paa': False}, partial=True)
        assert serializer.is_valid(), serializer.errors
        serializer.save()

        mock_desabilitar.assert_called_once_with(acao)


def test_serializer_update_exibir_paa_true_nao_chama_desabilitar(acao):
    with patch(
        'sme_ptrf_apps.core.api.serializers.acao_serializer.desabilitar_acao_ptrf_paa'
    ) as mock_desabilitar:
        serializer = AcaoSerializer(acao, data={'exibir_paa': True}, partial=True)
        assert serializer.is_valid(), serializer.errors
        serializer.save()

        mock_desabilitar.assert_not_called()


def test_serializer_update_sem_campo_exibir_paa_nao_chama_desabilitar(acao):
    with patch(
        'sme_ptrf_apps.core.api.serializers.acao_serializer.desabilitar_acao_ptrf_paa'
    ) as mock_desabilitar:
        serializer = AcaoSerializer(acao, data={'aceita_capital': True}, partial=True)
        assert serializer.is_valid(), serializer.errors
        serializer.save()

        mock_desabilitar.assert_not_called()

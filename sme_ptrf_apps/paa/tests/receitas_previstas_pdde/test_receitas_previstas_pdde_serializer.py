import pytest

from sme_ptrf_apps.paa.api.serializers import ReceitaPrevistaPddeSerializer

pytestmark = pytest.mark.django_db


def test_receita_prevista_serializer_list_serializer(receita_prevista_pdde):
    serializer = ReceitaPrevistaPddeSerializer(receita_prevista_pdde)
    assert serializer.data is not None
    assert 'uuid' in serializer.data
    assert 'paa' in serializer.data
    assert 'acao_pdde' in serializer.data
    assert 'acao_pdde_objeto' in serializer.data
    assert 'previsao_valor_custeio' in serializer.data
    assert 'previsao_valor_capital' in serializer.data
    assert 'previsao_valor_livre' in serializer.data
    assert 'saldo_custeio' in serializer.data
    assert 'saldo_capital' in serializer.data
    assert 'saldo_livre' in serializer.data


def test_receita_prevista_serializer_list_serializer_sem_acao(receita_prevista_pdde_sem_acao):
    serializer = ReceitaPrevistaPddeSerializer(receita_prevista_pdde_sem_acao)
    assert serializer.data is not None
    assert 'uuid' in serializer.data
    assert 'paa' in serializer.data
    assert serializer.data['acao_pdde'] is None
    assert 'previsao_valor_custeio' in serializer.data
    assert 'previsao_valor_capital' in serializer.data
    assert 'previsao_valor_livre' in serializer.data
    assert 'saldo_custeio' in serializer.data
    assert 'saldo_capital' in serializer.data
    assert 'saldo_livre' in serializer.data


def test_receita_prevista_serializer_list_serializer_sem_acao_validate():
    from rest_framework.exceptions import ValidationError
    with pytest.raises(ValidationError):
        ReceitaPrevistaPddeSerializer().validate({})


def test_receita_prevista_serializer_list_serializer_sem_paa_validate():
    from rest_framework.exceptions import ValidationError
    with pytest.raises(ValidationError):
        ReceitaPrevistaPddeSerializer().validate({'acao_pdde': '32309a0f-9d86-404b-908a-16f25cb76d5b'})


def test_receita_prevista_serializer_list_serializer_sem_erro_validate():
    data = {
        'paa': '32309a0f-9d86-404b-908a-16f25cb76d5b',
        'acao_pdde': '32309a0f-9d86-404b-908a-16f25cb76d5b',
    }
    assert ReceitaPrevistaPddeSerializer().validate(data) == data

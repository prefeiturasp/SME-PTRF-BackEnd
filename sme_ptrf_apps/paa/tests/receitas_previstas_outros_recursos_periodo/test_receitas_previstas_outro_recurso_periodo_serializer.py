import pytest

from sme_ptrf_apps.paa.api.serializers import ReceitaPrevistaOutroRecursoPeriodoSerializer

pytestmark = pytest.mark.django_db


def test_receita_prevista_serializer_list_serializer(receita_prevista_outro_recurso_periodo):
    serializer = ReceitaPrevistaOutroRecursoPeriodoSerializer(receita_prevista_outro_recurso_periodo)
    assert serializer.data is not None
    assert 'uuid' in serializer.data
    assert 'paa' in serializer.data
    assert 'outro_recurso_periodo' in serializer.data
    assert 'previsao_valor_custeio' in serializer.data
    assert 'previsao_valor_capital' in serializer.data
    assert 'previsao_valor_livre' in serializer.data
    assert 'saldo_custeio' in serializer.data
    assert 'saldo_capital' in serializer.data
    assert 'saldo_livre' in serializer.data


def test_serializer_erro_paa_obrigatorio(outro_recurso_periodo):
    payload = {
        "outro_recurso_periodo": outro_recurso_periodo.uuid,
    }

    serializer = ReceitaPrevistaOutroRecursoPeriodoSerializer(data=payload)
    assert not serializer.is_valid()

    assert "paa" in serializer.errors
    assert serializer.errors["paa"] == ["PAA não foi informado."]


def test_serializer_erro_recurso_obrigatorio(paa):
    payload = {"paa": paa.uuid}

    serializer = ReceitaPrevistaOutroRecursoPeriodoSerializer(data=payload)
    assert not serializer.is_valid()

    assert "outro_recurso_periodo" in serializer.errors
    assert serializer.errors["outro_recurso_periodo"] == ["Outro Recurso do Período não foi informado."]


def test_serializer_unique_together_validator(receita_prevista_outro_recurso_periodo):
    payload = {
        "paa": receita_prevista_outro_recurso_periodo.paa.uuid,
        "outro_recurso_periodo": receita_prevista_outro_recurso_periodo.outro_recurso_periodo.uuid,
    }

    serializer = ReceitaPrevistaOutroRecursoPeriodoSerializer(data=payload)
    assert not serializer.is_valid()

    assert "non_field_errors" in serializer.errors
    assert serializer.errors["non_field_errors"][0] == \
           "Já existe uma receita cadastrada para o recurso no período!"


def test_campos_read_only_nao_podem_ser_setados(paa, outro_recurso_periodo):
    payload = {
        "paa": str(paa.uuid),
        "outro_recurso_periodo": str(outro_recurso_periodo.uuid),
        "uuid": "valor-indevido",
        "id": 999,
    }

    serializer = ReceitaPrevistaOutroRecursoPeriodoSerializer(data=payload)
    assert serializer.is_valid(), serializer.errors

    instance = serializer.save()

    assert instance.id != 999
    assert instance.uuid != "valor-indevido"


def test_receita_prevista_outro_recurso_serializer_bloqueia_edicao_com_documento_final_concluido(
    receita_prevista_outro_recurso_periodo
):
    """Testa que não é possível editar receita prevista de outros recursos quando documento final está concluído"""
    from sme_ptrf_apps.paa.fixtures.factories.documento_paa_factory import DocumentoPaaFactory
    
    DocumentoPaaFactory.create(
        paa=receita_prevista_outro_recurso_periodo.paa,
        versao="FINAL",
        status_geracao="CONCLUIDO"
    )
    
    payload = {
        "previsao_valor_custeio": "1000.00",
    }
    
    serializer = ReceitaPrevistaOutroRecursoPeriodoSerializer(
        instance=receita_prevista_outro_recurso_periodo,
        data=payload,
        partial=True
    )
    
    assert not serializer.is_valid()
    assert 'mensagem' in serializer.errors
    assert 'Não é possível editar receitas previstas de outros recursos após a geração do documento final do PAA.' in serializer.errors['mensagem']

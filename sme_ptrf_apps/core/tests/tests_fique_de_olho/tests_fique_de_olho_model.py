import pytest

from ...models import FiqueDeOlho, TipoTextoFiqueDeOlhoChoices

pytestmark = pytest.mark.django_db


def test_instance_model(fique_de_olho):
    model = fique_de_olho
    assert isinstance(model, FiqueDeOlho)
    assert model.uuid
    assert model.id
    assert model.texto
    assert model.tipo_texto
    assert model.recurso


def test_srt_model(fique_de_olho):
    assert str(fique_de_olho) == (
        f"{fique_de_olho.get_short_texto()} (ASSOCIAÇÕES - Prestação de Contas) - {fique_de_olho.recurso.nome}"
    )


def test_delete_nao_exclui_registro(fique_de_olho):
    fique_de_olho.delete()
    assert FiqueDeOlho.objects.filter(id=fique_de_olho.id).exists()


def test_get_tipo_texto_display(fique_de_olho):
    assert fique_de_olho.get_tipo_texto_display() == "ASSOCIAÇÕES - Prestação de Contas"


def test_filter_by_recurso(fique_de_olho):
    resultado = FiqueDeOlho.filter_by_recurso(fique_de_olho.recurso)
    assert fique_de_olho in resultado


def test_filter_by_tipo_texto(fique_de_olho):
    resultado = FiqueDeOlho.filter_by_tipo_texto(fique_de_olho.tipo_texto)
    assert fique_de_olho in resultado


def test_get_first_with_recurso_and_tipo_texto(fique_de_olho):
    resultado = FiqueDeOlho.get_first_with_recurso_and_tipo_texto(
        fique_de_olho.recurso, fique_de_olho.tipo_texto
    )
    assert resultado == fique_de_olho


def test_tipo_texto_fique_de_olho_choices():
    assert TipoTextoFiqueDeOlhoChoices.choices == [
        ("associacoes_prestacao_contas", "ASSOCIAÇÕES - Prestação de Contas"),
        ("associacoes_historico_membros", "ASSOCIAÇÕES - Histórico de Membros"),
        ("diretorias_consolidado_das_pcs", "DIRETORIAS - Consolidado das PCs"),
    ]


def test_tipo_texto_fique_de_olho_choices_associacoes_historico_membros():
    choice = TipoTextoFiqueDeOlhoChoices.ASSOCIACOES_HISTORICO_MEMBROS
    assert choice.value == "associacoes_historico_membros"
    assert choice.label == "ASSOCIAÇÕES - Histórico de Membros"

import pytest

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
def test_str_representation(parametro_paa):
    assert str(parametro_paa) == 'Parâmetros do PAA'


@pytest.mark.django_db
def test_texto_pagina_paa_ue_field(parametro_paa):
    """Testa se o campo texto_pagina_paa_ue pode ser definido e recuperado"""
    texto_teste = "<p>Texto de teste para página PAA UE</p>"
    parametro_paa.texto_pagina_paa_ue = texto_teste
    parametro_paa.save()
    
    parametro_paa.refresh_from_db()
    assert parametro_paa.texto_pagina_paa_ue == texto_teste


@pytest.mark.django_db
def test_introducao_do_paa_ue_1_field(parametro_paa):
    """Testa se o campo introducao_do_paa_ue_1 pode ser definido e recuperado"""
    texto_teste = "<p>Introdução do PAA 1</p>"
    parametro_paa.introducao_do_paa_ue_1 = texto_teste
    parametro_paa.save()
    
    parametro_paa.refresh_from_db()
    assert parametro_paa.introducao_do_paa_ue_1 == texto_teste


@pytest.mark.django_db
def test_introducao_do_paa_ue_2_field(parametro_paa):
    """Testa se o campo introducao_do_paa_ue_2 pode ser definido e recuperado"""
    texto_teste = "<p>Introdução do PAA 2</p>"
    parametro_paa.introducao_do_paa_ue_2 = texto_teste
    parametro_paa.save()
    
    parametro_paa.refresh_from_db()
    assert parametro_paa.introducao_do_paa_ue_2 == texto_teste


@pytest.mark.django_db
def test_conclusao_do_paa_ue_1_field(parametro_paa):
    """Testa se o campo conclusao_do_paa_ue_1 pode ser definido e recuperado"""
    texto_teste = "<p>Conclusão do PAA 1</p>"
    parametro_paa.conclusao_do_paa_ue_1 = texto_teste
    parametro_paa.save()
    
    parametro_paa.refresh_from_db()
    assert parametro_paa.conclusao_do_paa_ue_1 == texto_teste


@pytest.mark.django_db
def test_conclusao_do_paa_ue_2_field(parametro_paa):
    """Testa se o campo conclusao_do_paa_ue_2 pode ser definido e recuperado"""
    texto_teste = "<p>Conclusão do PAA 2</p>"
    parametro_paa.conclusao_do_paa_ue_2 = texto_teste
    parametro_paa.save()
    
    parametro_paa.refresh_from_db()
    assert parametro_paa.conclusao_do_paa_ue_2 == texto_teste


@pytest.mark.django_db
def test_all_text_fields_can_be_null(parametro_paa):
    """Testa se todos os campos de texto podem ser None"""
    parametro_paa.texto_pagina_paa_ue = None
    parametro_paa.introducao_do_paa_ue_1 = None
    parametro_paa.introducao_do_paa_ue_2 = None
    parametro_paa.conclusao_do_paa_ue_1 = None
    parametro_paa.conclusao_do_paa_ue_2 = None
    parametro_paa.save()
    
    parametro_paa.refresh_from_db()
    assert parametro_paa.texto_pagina_paa_ue is None
    assert parametro_paa.introducao_do_paa_ue_1 is None
    assert parametro_paa.introducao_do_paa_ue_2 is None
    assert parametro_paa.conclusao_do_paa_ue_1 is None
    assert parametro_paa.conclusao_do_paa_ue_2 is None

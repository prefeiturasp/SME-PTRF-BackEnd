import json
import pytest
from rest_framework import status


pytestmark = pytest.mark.django_db


class TestTextosPaaUeAPI:
    """Testes para as actions de textos PAA UE"""

    def test_get_textos_paa_ue_success(self, jwt_authenticated_client_sme, flag_paa, parametro_paa):
        """Testa GET textos-paa-ue retornando todos os 5 textos"""

        parametro_paa.texto_pagina_paa_ue = "<p>Texto da página PAA UE</p>"
        parametro_paa.introducao_do_paa_ue_1 = "<p>Introdução do PAA 1</p>"
        parametro_paa.introducao_do_paa_ue_2 = "<p>Introdução do PAA 2</p>"
        parametro_paa.conclusao_do_paa_ue_1 = "<p>Conclusão do PAA 1</p>"
        parametro_paa.conclusao_do_paa_ue_2 = "<p>Conclusão do PAA 2</p>"
        parametro_paa.save()

        response = jwt_authenticated_client_sme.get('/api/parametros-paa/textos-paa-ue/')
        content = json.loads(response.content)

        assert response.status_code == status.HTTP_200_OK
        assert 'texto_pagina_paa_ue' in content
        assert 'introducao_do_paa_ue_1' in content
        assert 'introducao_do_paa_ue_2' in content
        assert 'conclusao_do_paa_ue_1' in content
        assert 'conclusao_do_paa_ue_2' in content
        
        assert content['texto_pagina_paa_ue'] == "<p>Texto da página PAA UE</p>"
        assert content['introducao_do_paa_ue_1'] == "<p>Introdução do PAA 1</p>"
        assert content['introducao_do_paa_ue_2'] == "<p>Introdução do PAA 2</p>"
        assert content['conclusao_do_paa_ue_1'] == "<p>Conclusão do PAA 1</p>"
        assert content['conclusao_do_paa_ue_2'] == "<p>Conclusão do PAA 2</p>"

    def test_get_textos_paa_ue_with_none_values(self, jwt_authenticated_client_sme, flag_paa, parametro_paa):
        """Testa GET textos-paa-ue com valores None"""
        response = jwt_authenticated_client_sme.get('/api/parametros-paa/textos-paa-ue/')
        content = json.loads(response.content)

        assert response.status_code == status.HTTP_200_OK
        assert content['texto_pagina_paa_ue'] is None
        assert content['introducao_do_paa_ue_1'] is None
        assert content['introducao_do_paa_ue_2'] is None
        assert content['conclusao_do_paa_ue_1'] is None
        assert content['conclusao_do_paa_ue_2'] is None

    def test_patch_update_textos_paa_ue_success(self, jwt_authenticated_client_sme, flag_paa, parametro_paa):
        """Testa PATCH update-textos-paa-ue com sucesso"""
        data = {
            'texto_pagina_paa_ue': '<p>Novo texto da página</p>',
            'introducao_do_paa_ue_1': '<p>Nova introdução 1</p>',
            'introducao_do_paa_ue_2': '<p>Nova introdução 2</p>'
        }

        response = jwt_authenticated_client_sme.patch(
            '/api/parametros-paa/update-textos-paa-ue/',
            data=json.dumps(data),
            content_type='application/json'
        )
        content = json.loads(response.content)

        assert response.status_code == status.HTTP_200_OK
        assert content['detail'] == 'Salvo com sucesso'

        parametro_paa.refresh_from_db()
        assert parametro_paa.texto_pagina_paa_ue == '<p>Novo texto da página</p>'
        assert parametro_paa.introducao_do_paa_ue_1 == '<p>Nova introdução 1</p>'
        assert parametro_paa.introducao_do_paa_ue_2 == '<p>Nova introdução 2</p>'

    def test_patch_update_textos_paa_ue_partial_update(self, jwt_authenticated_client_sme, flag_paa, parametro_paa):
        """Testa PATCH update-textos-paa-ue atualizando apenas alguns campos"""

        parametro_paa.texto_pagina_paa_ue = '<p>Texto original</p>'
        parametro_paa.introducao_do_paa_ue_1 = '<p>Introdução original</p>'
        parametro_paa.save()


        data = {
            'texto_pagina_paa_ue': '<p>Texto atualizado</p>'
        }

        response = jwt_authenticated_client_sme.patch(
            '/api/parametros-paa/update-textos-paa-ue/',
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == status.HTTP_200_OK


        parametro_paa.refresh_from_db()
        assert parametro_paa.texto_pagina_paa_ue == '<p>Texto atualizado</p>'
        assert parametro_paa.introducao_do_paa_ue_1 == '<p>Introdução original</p>'

    def test_patch_update_textos_paa_ue_all_none_error(self, jwt_authenticated_client_sme, flag_paa, parametro_paa):
        """Testa PATCH update-textos-paa-ue com todos os campos None (deve retornar erro)"""
        data = {}

        response = jwt_authenticated_client_sme.patch(
            '/api/parametros-paa/update-textos-paa-ue/',
            data=json.dumps(data),
            content_type='application/json'
        )
        content = json.loads(response.content)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert content['erro'] == 'falta_de_informacoes'
        assert content['operacao'] == 'update_textos_paa_ue'
        assert content['mensagem'] == 'Pelo menos um campo deve ser enviado para atualização.'

    def test_patch_update_textos_paa_ue_with_empty_strings(self, jwt_authenticated_client_sme, flag_paa, parametro_paa):
        """Testa PATCH update-textos-paa-ue com strings vazias (deve funcionar)"""
        data = {
            'texto_pagina_paa_ue': '',
            'introducao_do_paa_ue_1': '   ',
            'introducao_do_paa_ue_2': ''
        }

        response = jwt_authenticated_client_sme.patch(
            '/api/parametros-paa/update-textos-paa-ue/',
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == status.HTTP_200_OK


        parametro_paa.refresh_from_db()
        assert parametro_paa.texto_pagina_paa_ue == ''
        assert parametro_paa.introducao_do_paa_ue_1 == '   '
        assert parametro_paa.introducao_do_paa_ue_2 == ''

    def test_patch_update_textos_paa_ue_mixed_none_and_values(self, jwt_authenticated_client_sme, flag_paa, parametro_paa):
        """Testa PATCH update-textos-paa-ue com alguns campos None e outros com valores"""
        data = {
            'texto_pagina_paa_ue': '<p>Texto atualizado</p>',
            'introducao_do_paa_ue_1': None,
            'introducao_do_paa_ue_2': '<p>Introdução 2 atualizada</p>'
        }

        response = jwt_authenticated_client_sme.patch(
            '/api/parametros-paa/update-textos-paa-ue/',
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == status.HTTP_200_OK


        parametro_paa.refresh_from_db()
        assert parametro_paa.texto_pagina_paa_ue == '<p>Texto atualizado</p>'
        assert parametro_paa.introducao_do_paa_ue_1 is None
        assert parametro_paa.introducao_do_paa_ue_2 == '<p>Introdução 2 atualizada</p>'


    def test_patch_update_textos_paa_ue_all_fields(self, jwt_authenticated_client_sme, flag_paa, parametro_paa):
        """Testa PATCH update-textos-paa-ue atualizando todos os campos"""
        data = {
            'texto_pagina_paa_ue': '<p>Texto completo 1</p>',
            'introducao_do_paa_ue_1': '<p>Introdução completa 1</p>',
            'introducao_do_paa_ue_2': '<p>Introdução completa 2</p>',
            'conclusao_do_paa_ue_1': '<p>Conclusão completa 1</p>',
            'conclusao_do_paa_ue_2': '<p>Conclusão completa 2</p>'
        }

        response = jwt_authenticated_client_sme.patch(
            '/api/parametros-paa/update-textos-paa-ue/',
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == status.HTTP_200_OK

        parametro_paa.refresh_from_db()
        assert parametro_paa.texto_pagina_paa_ue == '<p>Texto completo 1</p>'
        assert parametro_paa.introducao_do_paa_ue_1 == '<p>Introdução completa 1</p>'
        assert parametro_paa.introducao_do_paa_ue_2 == '<p>Introdução completa 2</p>'
        assert parametro_paa.conclusao_do_paa_ue_1 == '<p>Conclusão completa 1</p>'
        assert parametro_paa.conclusao_do_paa_ue_2 == '<p>Conclusão completa 2</p>'

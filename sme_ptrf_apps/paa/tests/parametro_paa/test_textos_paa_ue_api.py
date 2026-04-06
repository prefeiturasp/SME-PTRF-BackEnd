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
        }

        response = jwt_authenticated_client_sme.patch(
            '/api/parametros-paa/update-textos-paa-ue/',
            data=json.dumps(data),
            content_type='application/json'
        )
        content = json.loads(response.content)

        assert response.status_code == status.HTTP_200_OK
        assert content['detail'] == 'Textos atualizados com sucesso'

        parametro_paa.refresh_from_db()
        assert parametro_paa.texto_pagina_paa_ue == '<p>Novo texto da página</p>'

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
            'texto_atividades_previstas': '',
            'texto_levantamento_prioridades': '',
            'introducao_do_paa_ue_1': '',
            'introducao_do_paa_ue_2': '',
            'conclusao_do_paa_ue_1': '',
            'conclusao_do_paa_ue_2': ''
        }

        response = jwt_authenticated_client_sme.patch(
            '/api/parametros-paa/update-textos-paa-ue/',
            data=json.dumps(data),
            content_type='application/json'
        )
        content = json.loads(response.content)
        parametro_paa.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert content['detail'] == 'Textos atualizados com sucesso'

        assert parametro_paa.texto_pagina_paa_ue == ''
        assert parametro_paa.texto_atividades_previstas == ''
        assert parametro_paa.texto_levantamento_prioridades == ''
        assert parametro_paa.introducao_do_paa_ue_1 == ''
        assert parametro_paa.introducao_do_paa_ue_2 == ''
        assert parametro_paa.conclusao_do_paa_ue_1 == ''
        assert parametro_paa.conclusao_do_paa_ue_2 == ''

    def test_patch_update_textos_paa_ue_mixed_none_and_values(self, jwt_authenticated_client_sme, flag_paa,
                                                              parametro_paa):
        """Testa PATCH update-textos-paa-ue com alguns campos None e outros com valores"""
        data = {
            'texto_pagina_paa_ue': '<p>Texto atualizado</p>',
            'introducao_do_paa_ue_1': None,
        }

        response = jwt_authenticated_client_sme.patch(
            '/api/parametros-paa/update-textos-paa-ue/',
            data=json.dumps(data),
            content_type='application/json'
        )

        content = json.loads(response.content)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'introducao_do_paa_ue_1' in content
        assert content['introducao_do_paa_ue_1'][0] == 'O campo Introdução 1 da aba Relatórios não foi informado.'

    def test_patch_update_textos_paa_ue_none_values(self, jwt_authenticated_client_sme, flag_paa,
                                                    parametro_paa):
        """Testa PATCH update-textos-paa-ue com alguns campos None e outros com valores"""
        data = {
            'texto_pagina_paa_ue': None,
            'texto_atividades_previstas': None,
            'texto_levantamento_prioridades': None,
            'introducao_do_paa_ue_1': None,
            'introducao_do_paa_ue_2': None,
            'conclusao_do_paa_ue_1': None,
            'conclusao_do_paa_ue_2': None
        }

        response = jwt_authenticated_client_sme.patch(
            '/api/parametros-paa/update-textos-paa-ue/',
            data=json.dumps(data),
            content_type='application/json'
        )

        content = json.loads(response.content)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert content['texto_pagina_paa_ue'][0] == 'O campo Explicação sobre o PAA não foi informado.'
        assert content['texto_atividades_previstas'][0] == 'O campo Atividades previstas não foi informado.'
        assert content['texto_levantamento_prioridades'][0] == 'O campo Levantamento de Prioridades não foi informado.'
        assert content['introducao_do_paa_ue_1'][0] == 'O campo Introdução 1 da aba Relatórios não foi informado.'
        assert content['introducao_do_paa_ue_2'][0] == 'O campo Introdução 2 da aba Relatórios não foi informado.'
        assert content['conclusao_do_paa_ue_1'][0] == 'O campo Conclusão do PAA 1 não foi informado.'
        assert content['conclusao_do_paa_ue_2'][0] == 'O campo Conclusão da aba Relatórios não foi informado.'

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

from unittest.mock import patch, MagicMock
from django.test import override_settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.permissions import IsAuthenticated

from sme_ptrf_apps.paa.api.views.paa_dre_viewset import PaaDreViewSet
from sme_ptrf_apps.paa.models import Paa

User = get_user_model()


class TestPaaDreViewSet(APITestCase):

    def setUp(self):
        self.uuid = "62f300a3-8587-43d5-8cfd-da1edbfd2428"
        self.url_base = "/api/paa-dre/"
        self.url_retrieve = f"{self.url_base}{self.uuid}/"

        self.user = User.objects.create(username="teste")
        self.client.force_authenticate(user=self.user)

        # Sobrescreve as permissões customizadas para isolar o teste unitário
        PaaDreViewSet.permission_classes = [IsAuthenticated]

    @override_settings(WAFFLE_FLAG_DEFAULT=True)
    def test_list_deve_retornar_not_found(self):
        """Valida que o método list explicitamente não é permitido nesta rota."""
        response = self.client.get(self.url_base)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @override_settings(WAFFLE_FLAG_DEFAULT=True)
    @patch("sme_ptrf_apps.paa.api.views.paa_dre_viewset.PaaDreService.listar_paas")
    @patch("sme_ptrf_apps.paa.api.views.paa_dre_viewset.PaaDreFilter")
    def test_retrieve_deve_retornar_lista_de_paas_com_sucesso(
        self,
        mock_filter,
        mock_listar_paas
    ):
        filtro_mock = MagicMock()
        filtro_mock.is_valid.return_value = True
        filtro_mock.form.cleaned_data = {
            "periodo": "",
            "unidade": "",
            "tipo_unidade": "",
            "status": "",
        }
        mock_filter.return_value = filtro_mock

        retorno_mock = [
            {
                "uuid": "123",
                "nome": "PAA Teste"
            }
        ]
        mock_listar_paas.return_value = retorno_mock

        response = self.client.get(self.url_retrieve)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"] == retorno_mock
        assert response.data["count"] == 1

        mock_listar_paas.assert_called_once_with(
            self.uuid,
            filtro_mock.form.cleaned_data
        )

    @override_settings(WAFFLE_FLAG_DEFAULT=True)
    @patch("sme_ptrf_apps.paa.api.views.paa_dre_viewset.PaaDreService.obter_tabelas")
    def test_tabelas_deve_retornar_dados_auxiliares_com_sucesso(self, mock_obter_tabelas):
        """Valida a rota customizada 'tabelas'."""
        url_tabelas = f"{self.url_retrieve}tabelas/"
        mock_retorno = {"periodos": ["2026"], "status": ["Pendente"]}
        mock_obter_tabelas.return_value = mock_retorno

        response = self.client.get(url_tabelas)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == mock_retorno
        mock_obter_tabelas.assert_called_once_with(self.uuid)

    @override_settings(WAFFLE_FLAG_DEFAULT=True)
    @patch("sme_ptrf_apps.paa.api.views.paa_dre_viewset.RenderizadorPaaBuilder")
    def test_visualizar_documentos_paa_com_sucesso(self, mock_builder):
        """Valida a rota de visualização de documentos criando o mock do renderizador."""
        # Criamos o objeto real no banco de dados do teste já que a View dá um Paa.objects.get()
        Paa.objects.create(uuid=self.uuid)
        url_documentos = f"{self.url_retrieve}visualizar-documentos-paa/"

        # Mocka o comportamento do Builder (.build())
        mock_instance_builder = MagicMock()
        mock_instance_builder.build.return_value = {"html": "<h1>PAA VIGENTE</h1>"}
        mock_builder.return_value = mock_instance_builder

        response = self.client.get(url_documentos)

        assert response.status_code == status.HTTP_200_OK
        assert "vigente" in response.data
        assert response.data["vigente"] == {"html": "<h1>PAA VIGENTE</h1>"}

        mock_builder.assert_called_once()

    @override_settings(WAFFLE_FLAG_DEFAULT=True)
    def test_visualizar_documentos_paa_nao_encontrado(self):
        """Valida se retorna 404 caso o UUID passado não corresponda a nenhum PAA no banco."""
        uuid_inexistente = "00000000-0000-0000-0000-000000000000"
        url_documentos = f"{self.url_base}{uuid_inexistente}/visualizar-documentos-paa/"

        response = self.client.get(url_documentos)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["erro"] == "Objeto não encontrado."

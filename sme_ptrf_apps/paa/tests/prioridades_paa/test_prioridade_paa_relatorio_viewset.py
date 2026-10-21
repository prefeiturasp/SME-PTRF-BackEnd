import uuid as uuid_module
import pytest
from unittest.mock import patch

from rest_framework import status
from sme_ptrf_apps.paa.enums import PaaStatusEnum


@pytest.mark.django_db
class TestPrioridadePaaRelatorioGetSerializerContext:

    URL = '/api/prioridades-paa-relatorio/'
    PATCH_TARGET = 'sme_ptrf_apps.paa.api.views.prioridade_paa_viewset.RetificacaoPaaService'

    def test_sem_paa_uuid_nao_chama_servico_retificacao(
        self, jwt_authenticated_client_sme, flag_paa
    ):
        with patch(self.PATCH_TARGET) as mock_service:
            jwt_authenticated_client_sme.get(self.URL)
            mock_service.assert_not_called()

    def test_sem_paa_uuid_campo_alteracao_e_none(
        self, jwt_authenticated_client_sme, flag_paa, paa, prioridade_paa_factory
    ):
        prioridade_paa_factory(paa=paa)

        response = jwt_authenticated_client_sme.get(self.URL)
        result = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert result['results'][0]['alteracao'] is None

    def test_paa_uuid_inexistente_retorna_200_sem_erro(
        self, jwt_authenticated_client_sme, flag_paa
    ):
        uuid_invalido = uuid_module.uuid4()

        response = jwt_authenticated_client_sme.get(
            f'{self.URL}?paa__uuid={uuid_invalido}'
        )
        result = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert result['count'] == 0

    def test_paa_sem_replica_campo_alteracao_e_none(
        self, jwt_authenticated_client_sme, flag_paa, paa, prioridade_paa_factory
    ):
        prioridade_paa_factory(paa=paa)

        response = jwt_authenticated_client_sme.get(
            f'{self.URL}?paa__uuid={paa.uuid}'
        )
        result = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert result['results'][0]['alteracao'] is None

    def test_paa_em_retificacao_campo_alteracao_recebe_valor_do_servico(
        self, jwt_authenticated_client_sme, flag_paa, paa_factory, prioridade_paa_factory
    ):
        paa = paa_factory(status=PaaStatusEnum.EM_RETIFICACAO.name)
        prioridade = prioridade_paa_factory(paa=paa)
        alteracoes_mock = {
            'prioridades': {str(prioridade.uuid): {'acao': 'modificado'}}
        }

        with patch(self.PATCH_TARGET) as mock_service_class:
            mock_service_class.return_value.identificar_alteracoes.return_value = alteracoes_mock

            response = jwt_authenticated_client_sme.get(
                f'{self.URL}?paa__uuid={paa.uuid}'
            )

        result = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert result['results'][0]['alteracao'] == 'modificado'

    def test_paa_em_retificacao_prioridade_sem_alteracao_campo_e_none(
        self, jwt_authenticated_client_sme, flag_paa, paa_factory, prioridade_paa_factory
    ):
        paa = paa_factory(status=PaaStatusEnum.EM_RETIFICACAO.name)
        prioridade_paa_factory(paa=paa)

        with patch(self.PATCH_TARGET) as mock_service_class:
            mock_service_class.return_value.identificar_alteracoes.return_value = {
                'prioridades': {}
            }

            response = jwt_authenticated_client_sme.get(
                f'{self.URL}?paa__uuid={paa.uuid}'
            )

        result = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert result['results'][0]['alteracao'] is None

    def test_servico_retificacao_recebe_paa_e_usuario_corretos(
        self, jwt_authenticated_client_sme, flag_paa, paa
    ):
        with patch(self.PATCH_TARGET) as mock_service_class:
            mock_service_class.return_value.identificar_alteracoes.return_value = {}

            jwt_authenticated_client_sme.get(
                f'{self.URL}?paa__uuid={paa.uuid}'
            )

        call_kwargs = mock_service_class.call_args.kwargs
        assert call_kwargs['paa'] == paa
        assert call_kwargs['usuario'] is not None

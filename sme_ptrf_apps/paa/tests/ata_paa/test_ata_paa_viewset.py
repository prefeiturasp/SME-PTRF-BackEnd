import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from sme_ptrf_apps.paa.api.views.ata_paa_viewset import AtaPaaViewSet
from sme_ptrf_apps.paa.models import AtaPaa, Paa

User = get_user_model()

pytestmark = pytest.mark.django_db


def test_view_set_retrieve(ata_paa, usuario_permissao_sme, flag_paa):
    request = APIRequestFactory().get("")
    detalhe = AtaPaaViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_sme)
    response = detalhe(request, uuid=ata_paa.uuid)

    assert response.status_code == status.HTTP_200_OK


def test_view_set_tabelas(usuario_permissao_sme, flag_paa):
    request = APIRequestFactory().get("/api/atas-paa/tabelas/")
    tabelas = AtaPaaViewSet.as_view({'get': 'tabelas'})
    force_authenticate(request, user=usuario_permissao_sme)
    response = tabelas(request)

    assert response.status_code == status.HTTP_200_OK
    assert 'tipos_ata' in response.data
    assert 'tipos_reuniao' in response.data
    assert 'convocacoes' in response.data
    assert 'pareceres' in response.data


@patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.AtaPaaViewSet.permission_classes', [])
class TestAtaPaaViewSetIniciarAta:

    @pytest.fixture
    def factory(self):
        return APIRequestFactory()

    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='testpass123'
        )

    @pytest.fixture
    def paa(self):
        """Fixture para criar um PAA de teste"""
        return MagicMock(spec=Paa, uuid='paa-uuid-123')

    @pytest.fixture
    def ata_paa(self):
        """Fixture para criar uma AtaPaa de teste"""
        return MagicMock(
            spec=AtaPaa,
            uuid='ata-uuid-123',
            paa=MagicMock(uuid='paa-uuid-123')
        )

    @patch('waffle.mixins.flag_is_active', return_value=True)
    def test_iniciar_ata_get_sem_paa_uuid_retorna_400(self, mock_waffle, factory, user):
        """Testa GET sem informar paa_uuid"""
        view = AtaPaaViewSet.as_view({'get': 'iniciar_ata', 'post': 'iniciar_ata'})
        request = factory.get('/api/atas-paa/iniciar-ata/')
        force_authenticate(request, user=user)

        response = view(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['erro'] == 'parametros_requeridos'
        assert 'É necessário informar o uuid do PAA' in response.data['mensagem']

    @patch('waffle.mixins.flag_is_active', return_value=True)
    def test_iniciar_ata_post_sem_paa_uuid_retorna_400(self, mock_waffle, factory, user):
        """Testa POST sem informar paa_uuid"""
        view = AtaPaaViewSet.as_view({'get': 'iniciar_ata', 'post': 'iniciar_ata'})
        request = factory.post('/api/atas-paa/iniciar-ata/')
        force_authenticate(request, user=user)

        response = view(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['erro'] == 'parametros_requeridos'
        assert 'É necessário informar o uuid do PAA' in response.data['mensagem']

    @patch('waffle.mixins.flag_is_active', return_value=True)
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.Paa')
    def test_iniciar_ata_com_paa_inexistente_retorna_400(self, mock_paa_model, mock_waffle, factory, user):
        """Testa quando o PAA não existe na base"""
        mock_paa_model.DoesNotExist = Paa.DoesNotExist
        mock_paa_model.objects.get.side_effect = Paa.DoesNotExist

        view = AtaPaaViewSet.as_view({'get': 'iniciar_ata', 'post': 'iniciar_ata'})
        request = factory.get('/api/atas-paa/iniciar-ata/?paa_uuid=paa-inexistente')
        force_authenticate(request, user=user)

        response = view(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['erro'] == 'Objeto não encontrado.'
        assert 'paa-inexistente' in response.data['mensagem']
        mock_paa_model.objects.get.assert_called_once_with(uuid='paa-inexistente')

    @patch('waffle.mixins.flag_is_active', return_value=True)
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.AtaPaaLookUpSerializer')
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.AtaPaa')
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.Paa')
    def test_iniciar_ata_get_com_sucesso(self, mock_paa_model, mock_ata_paa_model, mock_lookup_serializer, mock_waffle,
                                         factory, user, paa, ata_paa):
        """Testa GET /iniciar-ata com sucesso"""
        mock_paa_model.objects.get.return_value = paa
        mock_ata_paa_model.iniciar.return_value = ata_paa
        mock_lookup_serializer.return_value.data = {'uuid': 'ata-uuid-123'}

        view = AtaPaaViewSet.as_view({'get': 'iniciar_ata', 'post': 'iniciar_ata'})
        request = factory.get('/api/atas-paa/iniciar-ata/?paa_uuid=paa-uuid-123')
        force_authenticate(request, user=user)

        response = view(request)

        assert response.status_code == status.HTTP_200_OK
        mock_paa_model.objects.get.assert_called_once_with(uuid='paa-uuid-123')
        mock_ata_paa_model.iniciar.assert_called_once_with(paa=paa)
        mock_lookup_serializer.assert_called_once_with(ata_paa, many=False)
        assert response.data == {'uuid': 'ata-uuid-123'}

    @patch('waffle.mixins.flag_is_active', return_value=True)
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.AtaPaaSerializer')
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.AtaPaa')
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.Paa')
    def test_iniciar_ata_post_com_sucesso(self, mock_paa_model, mock_ata_paa_model, mock_serializer, mock_waffle,
                                          factory, user, paa, ata_paa):
        """Testa POST /iniciar-ata com sucesso"""
        mock_paa_model.objects.get.return_value = paa
        mock_ata_paa_model.iniciar.return_value = ata_paa
        mock_serializer.return_value.data = {
            'uuid': 'ata-uuid-123',
            'tipo_ata': 'APRESENTACAO',
            'data_reuniao': '2025-02-05'
        }

        view = AtaPaaViewSet.as_view({'get': 'iniciar_ata', 'post': 'iniciar_ata'})
        request = factory.post('/api/atas-paa/iniciar-ata/?paa_uuid=paa-uuid-123')
        force_authenticate(request, user=user)

        response = view(request)

        assert response.status_code == status.HTTP_200_OK
        mock_paa_model.objects.get.assert_called_once_with(uuid='paa-uuid-123')
        mock_ata_paa_model.iniciar.assert_called_once_with(paa=paa)
        mock_serializer.assert_called_once_with(ata_paa, many=False)
        assert 'uuid' in response.data
        assert 'tipo_ata' in response.data

    @patch('waffle.mixins.flag_is_active', return_value=True)
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.AtaPaaSerializer')
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.AtaPaaLookUpSerializer')
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.AtaPaa')
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.Paa')
    def test_iniciar_ata_usa_serializers_diferentes_para_get_e_post(
            self, mock_paa_model, mock_ata_paa_model, mock_lookup_serializer, mock_full_serializer,
            mock_waffle, factory, user, paa, ata_paa):
        """Testa que GET usa AtaPaaLookUpSerializer e POST usa AtaPaaSerializer"""
        mock_paa_model.objects.get.return_value = paa
        mock_ata_paa_model.iniciar.return_value = ata_paa
        mock_lookup_serializer.return_value.data = {'uuid': 'ata-uuid-123'}
        mock_full_serializer.return_value.data = {
            'uuid': 'ata-uuid-123',
            'tipo_ata': 'APRESENTACAO'
        }

        # Testa GET
        view_get = AtaPaaViewSet.as_view({'get': 'iniciar_ata'})
        request_get = factory.get('/api/atas-paa/iniciar-ata/?paa_uuid=paa-uuid-123')
        force_authenticate(request_get, user=user)

        response_get = view_get(request_get)

        assert response_get.status_code == status.HTTP_200_OK
        assert mock_lookup_serializer.called

        # Reset mocks
        mock_lookup_serializer.reset_mock()
        mock_full_serializer.reset_mock()
        mock_paa_model.reset_mock()
        mock_ata_paa_model.reset_mock()

        # Reconfigura mocks
        mock_paa_model.objects.get.return_value = paa
        mock_ata_paa_model.iniciar.return_value = ata_paa

        # Testa POST
        view_post = AtaPaaViewSet.as_view({'post': 'iniciar_ata'})
        request_post = factory.post('/api/atas-paa/iniciar-ata/?paa_uuid=paa-uuid-123')
        force_authenticate(request_post, user=user)

        response_post = view_post(request_post)

        assert response_post.status_code == status.HTTP_200_OK
        assert mock_full_serializer.called
        assert not mock_lookup_serializer.called


@patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.AtaPaaViewSet.permission_classes', [])
class TestAtaPaaViewSetDownloadArquivoAtaPaa:

    @pytest.fixture
    def factory(self):
        return APIRequestFactory()

    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='testpass123'
        )

    @pytest.fixture
    def ata_paa_mock(self):
        """Fixture para criar um mock de AtaPaa com arquivo"""
        ata_paa = MagicMock(spec=AtaPaa)
        ata_paa.uuid = 'ata-uuid-123'
        ata_paa.arquivo_pdf = MagicMock()
        ata_paa.arquivo_pdf.path = '/fake/path/ata-paa.pdf'
        return ata_paa

    @patch('waffle.mixins.flag_is_active', return_value=True)
    def test_download_arquivo_sem_uuid_retorna_400(self, mock_waffle, factory, user):
        """Testa download sem informar ata-paa-uuid"""
        view = AtaPaaViewSet.as_view({'get': 'download_arquivo_ata_paa'})
        request = factory.get('/api/ata-paa/download-arquivo-ata-paa/')
        force_authenticate(request, user=user)

        response = view(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['erro'] == 'parametros_requeridos'
        assert 'É necessário enviar o uuid da ata PAA' in response.data['mensagem']

    @patch('waffle.mixins.flag_is_active', return_value=True)
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.AtaPaa')
    def test_download_arquivo_com_uuid_invalido_retorna_400(
        self,
        mock_ata_paa_model,
        mock_waffle,
        factory,
        user
    ):
        """Testa download com UUID inválido que gera ValidationError"""
        from django.core.exceptions import ValidationError
        mock_ata_paa_model.by_uuid.side_effect = ValidationError('UUID inválido')

        view = AtaPaaViewSet.as_view({'get': 'download_arquivo_ata_paa'})
        request = factory.get('/api/ata-paa/download-arquivo-ata-paa/?ata-paa-uuid=uuid-invalido')
        force_authenticate(request, user=user)

        response = view(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['erro'] == 'Objeto não encontrado.'
        assert 'uuid-invalido' in response.data['mensagem']
        mock_ata_paa_model.by_uuid.assert_called_once_with('uuid-invalido')

    @patch('waffle.mixins.flag_is_active', return_value=True)
    @patch('builtins.open', create=True)
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.AtaPaa')
    def test_download_arquivo_com_sucesso(
            self, mock_ata_paa_model, mock_open, mock_waffle, factory, user, ata_paa_mock):
        """Testa download de arquivo PDF com sucesso"""
        mock_ata_paa_model.by_uuid.return_value = ata_paa_mock
        mock_file = MagicMock()
        mock_file.read.return_value = b'%PDF-1.4 fake pdf content'
        mock_open.return_value = mock_file

        view = AtaPaaViewSet.as_view({'get': 'download_arquivo_ata_paa'})
        request = factory.get('/api/ata-paa/download-arquivo-ata-paa/?ata-paa-uuid=ata-uuid-123')
        force_authenticate(request, user=user)

        response = view(request)

        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'application/pdf'
        assert 'attachment' in response['Content-Disposition']
        assert 'ata-paa.pdf' in response['Content-Disposition']
        mock_ata_paa_model.by_uuid.assert_called_once_with('ata-uuid-123')
        mock_open.assert_called_once_with('/fake/path/ata-paa.pdf', 'rb')

    @patch('waffle.mixins.flag_is_active', return_value=True)
    @patch('builtins.open', create=True)
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.AtaPaa')
    def test_download_arquivo_quando_arquivo_nao_existe_retorna_404(
            self, mock_ata_paa_model, mock_open, mock_waffle, factory, user, ata_paa_mock):
        """Testa download quando o arquivo PDF não existe no sistema"""
        mock_ata_paa_model.by_uuid.return_value = ata_paa_mock
        mock_open.side_effect = FileNotFoundError('Arquivo não encontrado')

        view = AtaPaaViewSet.as_view({'get': 'download_arquivo_ata_paa'})
        request = factory.get('/api/ata-paa/download-arquivo-ata-paa/?ata-paa-uuid=ata-uuid-123')
        force_authenticate(request, user=user)

        response = view(request)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['erro'] == 'arquivo_nao_gerado'
        assert 'Arquivo não encontrado' in response.data['mensagem']


@patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.AtaPaaViewSet.permission_classes', [])
class TestAtaPaaViewSetGerarAta:

    @pytest.fixture
    def factory(self):
        return APIRequestFactory()

    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='testpass123'
        )

    @pytest.fixture
    def paa_mock(self):
        """Fixture para criar um mock de Paa"""
        paa = MagicMock(spec=Paa)
        paa.uuid = 'paa-uuid-123'
        return paa

    @pytest.fixture
    def ata_paa_mock(self):
        """Fixture para criar um mock de AtaPaa"""
        ata_paa = MagicMock(spec=AtaPaa)
        ata_paa.uuid = 'ata-uuid-123'
        ata_paa.paa = MagicMock(uuid='paa-uuid-123')
        return ata_paa

    @patch('waffle.mixins.flag_is_active', return_value=True)
    def test_gerar_ata_sem_paa_uuid_retorna_400(self, mock_waffle, factory, user):
        """Testa gerar ata sem informar paa_uuid"""
        view = AtaPaaViewSet.as_view({'post': 'gerar_ata'})
        request = factory.post('/api/ata-paa/gerar-ata/', {})
        force_authenticate(request, user=user)

        response = view(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['erro'] == 'parametros_requeridos'
        assert 'É necessário informar o uuid do PAA' in response.data['mensagem']

    @patch('waffle.mixins.flag_is_active', return_value=True)
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.logger')
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.Paa')
    def test_gerar_ata_loga_erro_quando_paa_nao_encontrado(
            self, mock_paa_model, mock_logger, mock_waffle, factory, user):
        """Testa que erro é logado quando PAA não é encontrado"""
        mock_paa_model.DoesNotExist = Paa.DoesNotExist
        mock_paa_model.objects.get.side_effect = Paa.DoesNotExist

        view = AtaPaaViewSet.as_view({'post': 'gerar_ata'})
        request = factory.post('/api/ata-paa/gerar-ata/', {'paa_uuid': 'paa-inexistente'})
        force_authenticate(request, user=user)

        response = view(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args[0]
        assert 'Erro:' in call_args[0]

    @patch('waffle.mixins.flag_is_active', return_value=True)
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.AtaPaa')
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.Paa')
    def test_gerar_ata_quando_ata_paa_nao_existe_retorna_400(
            self, mock_paa_model, mock_ata_paa_model, mock_waffle, factory, user, paa_mock):
        """Testa quando a ata PAA não existe para o PAA informado"""
        mock_paa_model.objects.get.return_value = paa_mock
        mock_ata_paa_model.DoesNotExist = AtaPaa.DoesNotExist
        mock_ata_paa_model.objects.get.side_effect = AtaPaa.DoesNotExist
        mock_ata_paa_model.ATA_APRESENTACAO = 'APRESENTACAO'

        view = AtaPaaViewSet.as_view({'post': 'gerar_ata'})
        request = factory.post('/api/ata-paa/gerar-ata/', {'paa_uuid': 'paa-uuid-123'})
        force_authenticate(request, user=user)

        response = view(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['erro'] == 'Objeto não encontrado.'
        assert 'Ata PAA não encontrada' in response.data['mensagem']
        assert 'É necessário criar a ata antes de gerar' in response.data['mensagem']

    @patch('waffle.mixins.flag_is_active', return_value=True)
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.validar_geracao_ata_paa')
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.AtaPaa')
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.Paa')
    def test_gerar_ata_sem_confirmacao_retorna_400(
            self, mock_paa_model, mock_ata_paa_model, mock_validar, mock_waffle, factory, user, paa_mock, ata_paa_mock):
        """Testa quando o usuário não confirma a geração"""
        mock_paa_model.objects.get.return_value = paa_mock
        mock_ata_paa_model.objects.get.return_value = ata_paa_mock
        mock_ata_paa_model.ATA_APRESENTACAO = 'APRESENTACAO'
        mock_validar.return_value = {'is_valid': True}

        view = AtaPaaViewSet.as_view({'post': 'gerar_ata'})
        request = factory.post('/api/ata-paa/gerar-ata/', {'paa_uuid': 'paa-uuid-123'})
        force_authenticate(request, user=user)

        response = view(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'É necessário confirmar a geração da ata' in response.data['mensagem']
        assert response.data['confirmar'] is True

    @patch('waffle.mixins.flag_is_active', return_value=True)
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.validar_geracao_ata_paa')
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.AtaPaa')
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.Paa')
    def test_gerar_ata_quando_validacao_falha_retorna_400(
            self, mock_paa_model, mock_ata_paa_model, mock_validar, mock_waffle, factory, user, paa_mock, ata_paa_mock):
        """Testa quando a validação da geração falha"""
        mock_paa_model.objects.get.return_value = paa_mock
        mock_ata_paa_model.objects.get.return_value = ata_paa_mock
        mock_ata_paa_model.ATA_APRESENTACAO = 'APRESENTACAO'
        mock_validar.return_value = {
            'is_valid': False,
            'mensagem': 'Ata PAA está incompleta. Preencha todos os campos obrigatórios.'
        }

        view = AtaPaaViewSet.as_view({'post': 'gerar_ata'})
        request = factory.post('/api/ata-paa/gerar-ata/', {'paa_uuid': 'paa-uuid-123'})
        force_authenticate(request, user=user)

        response = view(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Ata PAA está incompleta' in response.data['mensagem']
        assert response.data['confirmar'] is False
        mock_validar.assert_called_once_with(ata_paa_mock)

    @patch('waffle.mixins.flag_is_active', return_value=True)
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.logger')
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.gerar_ata_paa_async')
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.validar_geracao_ata_paa')
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.AtaPaa')
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.Paa')
    def test_gerar_ata_com_sucesso(
            self, mock_paa_model, mock_ata_paa_model, mock_validar, mock_gerar_async, mock_logger, mock_waffle,
            factory, user, paa_mock, ata_paa_mock):
        """Testa geração de ata com sucesso"""
        mock_paa_model.objects.get.return_value = paa_mock
        mock_ata_paa_model.objects.get.return_value = ata_paa_mock
        mock_ata_paa_model.ATA_APRESENTACAO = 'APRESENTACAO'
        mock_validar.return_value = {'is_valid': True}
        mock_async_result = MagicMock()
        mock_gerar_async.apply_async.return_value = mock_async_result

        view = AtaPaaViewSet.as_view({'post': 'gerar_ata'})
        request = factory.post('/api/ata-paa/gerar-ata/', {
            'paa_uuid': 'paa-uuid-123',
            'confirmar': 1
        })
        force_authenticate(request, user=user)

        response = view(request)

        assert response.status_code == status.HTTP_200_OK
        assert 'Geração da ata final iniciada' in response.data['mensagem']
        assert response.data['status'] == 'EM_PROCESSAMENTO'
        mock_gerar_async.apply_async.assert_called_once_with(
            args=['ata-uuid-123', 'test_user']
        )
        mock_logger.info.assert_called_once()

    @patch('waffle.mixins.flag_is_active', return_value=True)
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.logger')
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.gerar_ata_paa_async')
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.validar_geracao_ata_paa')
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.AtaPaa')
    @patch('sme_ptrf_apps.paa.api.views.ata_paa_viewset.Paa')
    def test_gerar_ata_quando_task_falha_retorna_500(
            self, mock_paa_model, mock_ata_paa_model, mock_validar, mock_gerar_async, mock_logger, mock_waffle,
            factory, user, paa_mock, ata_paa_mock):
        """Testa quando a task assíncrona falha ao ser iniciada"""
        mock_paa_model.objects.get.return_value = paa_mock
        mock_ata_paa_model.objects.get.return_value = ata_paa_mock
        mock_ata_paa_model.ATA_APRESENTACAO = 'APRESENTACAO'
        mock_validar.return_value = {'is_valid': True}
        mock_gerar_async.apply_async.side_effect = Exception('Erro ao conectar com Celery')

        view = AtaPaaViewSet.as_view({'post': 'gerar_ata'})
        request = factory.post('/api/ata-paa/gerar-ata/', {
            'paa_uuid': 'paa-uuid-123',
            'confirmar': 1
        })
        force_authenticate(request, user=user)

        response = view(request)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['erro'] == 'erro_ao_iniciar_geracao'
        assert 'Erro ao conectar com Celery' in response.data['mensagem']
        mock_logger.error.assert_called_once()

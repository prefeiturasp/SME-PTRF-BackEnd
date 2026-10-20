import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from sme_ptrf_apps.core.fixtures.factories.recurso_factory import RecursoFactory
from sme_ptrf_apps.dre.fixtures.factories.comissao_factory import ComissaoFactory

from ...api.views.comissoes_viewset import ComissoesParametrizacaoViewSet
from ...models import Comissao, MembroComissao

pytestmark = pytest.mark.django_db


def test_comissoes_parametrizacao_viewset_list_filters_by_comissao_uuid_and_responsavel_analise_pc(usuario_permissao_atribuicao):
    comissao_filtrada = ComissaoFactory(nome='Comissão A', responsavel_analise_pc=True)
    ComissaoFactory(nome='Comissão B', responsavel_analise_pc=False)

    request = APIRequestFactory().get(
        '/api/comissoes-parametrizacao/',
        {
            'comissoes_uuid': str(comissao_filtrada.uuid),
            'responsavel_analise_pc': 'true',
        },
    )
    view = ComissoesParametrizacaoViewSet.as_view({'get': 'list'})

    force_authenticate(request, user=usuario_permissao_atribuicao)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    resultado = response.data['results'][0]
    assert resultado['uuid'] == str(comissao_filtrada.uuid)
    assert resultado['id'] == comissao_filtrada.id
    assert resultado['nome'] == comissao_filtrada.nome
    assert resultado['responsavel_analise_pc'] is True
    assert resultado['recursos'][0]['uuid'] == str(comissao_filtrada.recursos.first().uuid)
    assert resultado['recursos'][0]['nome'] == comissao_filtrada.recursos.first().nome


def test_comissoes_parametrizacao_viewset_list_filters_by_recursos_uuid(usuario_permissao_atribuicao):
    recurso = RecursoFactory()
    comissao_filtrada = ComissaoFactory(nome='Comissão C', recursos=[recurso])
    ComissaoFactory(nome='Comissão D')

    request = APIRequestFactory().get(
        '/api/comissoes-parametrizacao/',
        {
            'recursos_uuid': str(recurso.uuid),
        },
    )
    view = ComissoesParametrizacaoViewSet.as_view({'get': 'list'})

    force_authenticate(request, user=usuario_permissao_atribuicao)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['results'][0]['uuid'] == str(comissao_filtrada.uuid)
    assert response.data['results'][0]['nome'] == comissao_filtrada.nome
    assert response.data['results'][0]['recursos'][0]['uuid'] == str(recurso.uuid)
    assert response.data['results'][0]['recursos'][0]['nome'] == recurso.nome


def test_comissoes_parametrizacao_viewset_list_invalid_comissoes_uuid(usuario_permissao_atribuicao):
    request = APIRequestFactory().get(
        '/api/comissoes-parametrizacao/',
        {
            'comissoes_uuid': 'uuid-invalido',
        },
    )
    view = ComissoesParametrizacaoViewSet.as_view({'get': 'list'})

    force_authenticate(request, user=usuario_permissao_atribuicao)
    response = view(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Por favor, forneça UUIDs de comissões válidos, separados por vírgula.' in str(response.data['non_field_errors'])


def test_comissoes_parametrizacao_viewset_filtro_por_nome(usuario_permissao_atribuicao):
    comissao_encontrada = ComissaoFactory(nome='Comissão de Exame de Contas')
    ComissaoFactory(nome='Comissão de Prestação de Contas')

    request = APIRequestFactory().get(
        '/api/comissoes-parametrizacao/filtro-por-nome/',
        {
            'nome': 'exame',
        },
    )
    view = ComissoesParametrizacaoViewSet.as_view({'get': 'filtro_por_nome'})

    force_authenticate(request, user=usuario_permissao_atribuicao)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == [
        {
            'uuid': str(comissao_encontrada.uuid),
            'id': comissao_encontrada.id,
            'nome': comissao_encontrada.nome,
            'responsavel_analise_pc': False,
            'recursos': [
                {
                    'uuid': str(comissao_encontrada.recursos.first().uuid),
                    'nome': comissao_encontrada.recursos.first().nome,
                    'nome_exibicao': comissao_encontrada.recursos.first().nome_exibicao,
                }
            ],
        }
    ]


def test_comissoes_parametrizacao_viewset_create_rejects_duplicate_name_for_same_recurso(
    usuario_permissao_atribuicao,
):
    recurso = RecursoFactory()
    ComissaoFactory(nome='Comissão Repetida', recursos=[recurso])

    request = APIRequestFactory().post(
        '/api/comissoes-parametrizacao/',
        {
            'nome': '  Comissão  Repetida  ',
            'responsavel_analise_pc': False,
            'recursos': [str(recurso.uuid)],
        },
        format='json',
    )
    view = ComissoesParametrizacaoViewSet.as_view({'post': 'create'})

    force_authenticate(request, user=usuario_permissao_atribuicao)
    response = view(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Já existe uma comissão com o mesmo nome no recurso selecionado.' in str(
        response.data['non_field_errors']
    )


def test_comissoes_parametrizacao_viewset_destroy_without_members(usuario_permissao_atribuicao):
    comissao = ComissaoFactory(nome='Comissão E')
    request = APIRequestFactory().delete(f'/api/comissoes/{comissao.uuid}/')
    view = ComissoesParametrizacaoViewSet.as_view({'delete': 'destroy'})

    force_authenticate(request, user=usuario_permissao_atribuicao)
    response = view(request, uuid=comissao.uuid)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Comissao.objects.filter(uuid=comissao.uuid).exists()


def test_comissoes_parametrizacao_viewset_destroy_with_members_returns_error(usuario_permissao_atribuicao, dre):
    comissao = ComissaoFactory(nome='Comissão F')
    membro = MembroComissao.objects.create(
        rf='1234567',
        nome='Membro Teste',
        email='membro.teste@sme.prefeitura.sp.gov.br',
        dre=dre,
        cargo='Analista',
    )
    membro.comissoes.add(comissao)

    request = APIRequestFactory().delete(f'/api/comissoes/{comissao.uuid}/')
    view = ComissoesParametrizacaoViewSet.as_view({'delete': 'destroy'})

    force_authenticate(request, user=usuario_permissao_atribuicao)
    response = view(request, uuid=comissao.uuid)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {
        'mensagem': (
            'Há membros associados a esta comissão. Remova os membros antes de excluir a comissão.'
        )
    }




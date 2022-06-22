import pytest

from ...services import get_unidades_do_usuario, criar_acesso_de_suporte

pytestmark = pytest.mark.django_db


def test_obtem_lista_de_unidades_do_usuario_sem_acesso_suporte(
    unidade_do_suporte,
    usuario_do_suporte,
    visao_ue, visao_dre, visao_sme,
    dre
):
    unidades_esperadas = [
        {
            'associacao':
                {
                    'nome': '',
                    'uuid': ''
                },
            'nome': 'DRE teste',
            'notificacao_uuid': None,
            'notificar_devolucao_pc_uuid': None,
            'notificar_devolucao_referencia': None,
            'tipo_unidade': 'DRE',
            'uuid': dre.uuid,
            'acesso_de_suporte': False
        },
        {
            'associacao': {
                'nome': '',
                'uuid': ''
            },
            'nome': 'Secretaria Municipal de Educação',
            'notificacao_uuid': None,
            'notificar_devolucao_pc_uuid': None,
            'notificar_devolucao_referencia': None,
            'tipo_unidade': 'SME',
            'uuid': '8919f454-bee5-419c-ad54-b2df27bf8007',
            'acesso_de_suporte': False
        }
    ]

    unidades_do_usuario = get_unidades_do_usuario(usuario_do_suporte)

    assert unidades_do_usuario == unidades_esperadas


def test_obtem_lista_de_unidades_do_usuario_com_acesso_suporte(
    unidade_do_suporte,
    usuario_do_suporte,
    visao_ue, visao_dre, visao_sme,
    dre,
    associacao_em_suporte
):
    unidades_esperadas = [
        {
            'associacao':
                {
                    'nome': '',
                    'uuid': ''
                },
            'nome': 'DRE teste',
            'notificacao_uuid': None,
            'notificar_devolucao_pc_uuid': None,
            'notificar_devolucao_referencia': None,
            'tipo_unidade': 'DRE',
            'uuid': dre.uuid,
            'acesso_de_suporte': False
        },
        {
            'associacao': {
                'nome': 'Escola Teste Suporte',
                'uuid': associacao_em_suporte.uuid
            },
            'nome': 'Escola Unidade Diferente',
            'notificacao_uuid': None,
            'notificar_devolucao_pc_uuid': None,
            'notificar_devolucao_referencia': None,
            'tipo_unidade': 'EMEI',
            'uuid': unidade_do_suporte.uuid,
            'acesso_de_suporte': True
        },
        {
            'associacao': {
                'nome': '',
                'uuid': ''
            },
            'nome': 'Secretaria Municipal de Educação',
            'notificacao_uuid': None,
            'notificar_devolucao_pc_uuid': None,
            'notificar_devolucao_referencia': None,
            'tipo_unidade': 'SME',
            'uuid': '8919f454-bee5-419c-ad54-b2df27bf8007',
            'acesso_de_suporte': False
        }
    ]

    criar_acesso_de_suporte(
        unidade_do_suporte=unidade_do_suporte,
        usuario_do_suporte=usuario_do_suporte
    )

    unidades_do_usuario = get_unidades_do_usuario(usuario_do_suporte)

    assert unidades_do_usuario == unidades_esperadas

from sme_ptrf_apps.core.models import Associacao, Notificacao
from sme_ptrf_apps.users.models import UnidadeEmSuporte

from waffle import get_waffle_flag_model


def get_unidades_do_usuario(user, suporte=False):
    flags = get_waffle_flag_model()

    novo_suporte_unidade = flags.objects.filter(name='novo-suporte-unidades', everyone=True).exists()

    # Constante que representa o UUID da unidade Secretaria Municipal de Educação
    UUID_SME = "8919f454-bee5-419c-ad54-b2df27bf8007"
    UNIDADE_SME = {
        'uuid': UUID_SME,
        'nome': 'Secretaria Municipal de Educação',
        'tipo_unidade': 'SME',
        'associacao': {
            'uuid': '',
            'nome': ''
        },
        'notificar_devolucao_por_recurso': {},
        'acesso_de_suporte': False
    }

    unidades = []
    for unidade in user.unidades.all().order_by("nome"):
        acesso_de_suporte = UnidadeEmSuporte.objects.filter(unidade=unidade, user=user).exists()

        associacao = Associacao.objects.filter(unidade__uuid=unidade.uuid).first()

        notificacao_usuario_unidade = Notificacao.objects.filter(
            usuario=user,
            categoria=Notificacao.CATEGORIA_NOTIFICACAO_DEVOLUCAO_PC,
            unidade=unidade,
            lido=False
        ).select_related('prestacao_conta', 'prestacao_conta__periodo', 'prestacao_conta__periodo__recurso').distinct('prestacao_conta__periodo__recurso__uuid')

        notificar_devolucao_por_recurso = {}

        for notificacao in notificacao_usuario_unidade:
            if notificacao and notificacao.prestacao_conta:
                key = f'recurso_{notificacao.prestacao_conta.periodo.recurso.uuid}'

                notificar_devolucao_por_recurso[key] = {
                    'notificar_devolucao_referencia': notificacao.prestacao_conta.periodo.referencia,
                    'notificar_devolucao_pc_uuid': notificacao.prestacao_conta.uuid,
                    'notificacao_uuid': notificacao.uuid,
                }

        if novo_suporte_unidade:
            if suporte and acesso_de_suporte or not suporte and not acesso_de_suporte:
                unidades.append({
                    'uuid': unidade.uuid,
                    'nome': unidade.nome,
                    'tipo_unidade': unidade.tipo_unidade,
                    'associacao': {
                        'uuid': associacao.uuid if associacao else '',
                        'nome': associacao.nome if associacao else ''
                    },
                    'acesso_de_suporte': acesso_de_suporte,
                    'notificar_devolucao_por_recurso': notificar_devolucao_por_recurso
                })
        else:
            unidades.append({
                    'uuid': unidade.uuid,
                    'nome': unidade.nome,
                    'tipo_unidade': unidade.tipo_unidade,
                    'associacao': {
                        'uuid': associacao.uuid if associacao else '',
                        'nome': associacao.nome if associacao else ''
                    },
                    'acesso_de_suporte': acesso_de_suporte,
                    'notificar_devolucao_por_recurso': notificar_devolucao_por_recurso
                })

    # Como a visão SME não tem uma Unidade real, cria a unidade caso o usuário tenha essa visão
    if novo_suporte_unidade:
        if user.visoes.filter(nome='SME').exists() and not suporte:
            unidades.append(UNIDADE_SME)
    else:
        if user.visoes.filter(nome='SME').exists():
            unidades.append(UNIDADE_SME)

    return unidades

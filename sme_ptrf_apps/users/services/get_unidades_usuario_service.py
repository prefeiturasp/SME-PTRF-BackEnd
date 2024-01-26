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
        'notificacao_uuid': None,
        'notificar_devolucao_pc_uuid': None,
        'notificar_devolucao_referencia': None,
        'acesso_de_suporte': False
    }

    unidades = []
    for unidade in user.unidades.all().order_by("nome"):
        acesso_de_suporte = UnidadeEmSuporte.objects.filter(unidade=unidade, user=user).exists()
        
        associacao = Associacao.objects.filter(unidade__uuid=unidade.uuid).first()

        notificao_devolucao_pc = Notificacao.objects.filter(
            usuario=user,
            categoria=Notificacao.CATEGORIA_NOTIFICACAO_DEVOLUCAO_PC,
            unidade=unidade,
            lido=False
        ).first()

        if notificao_devolucao_pc and notificao_devolucao_pc.prestacao_conta:
            notificar_devolucao_referencia = notificao_devolucao_pc.prestacao_conta.periodo.referencia
            notificar_devolucao_pc_uuid = notificao_devolucao_pc.prestacao_conta.uuid
            notificacao_uuid = notificao_devolucao_pc.uuid
        else:
            notificar_devolucao_referencia = None
            notificacao_uuid = None
            notificar_devolucao_pc_uuid = None
        
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
                    'notificar_devolucao_referencia': notificar_devolucao_referencia,
                    'notificar_devolucao_pc_uuid': notificar_devolucao_pc_uuid,
                    'notificacao_uuid': notificacao_uuid,
                    'acesso_de_suporte': acesso_de_suporte
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
                    'notificar_devolucao_referencia': notificar_devolucao_referencia,
                    'notificar_devolucao_pc_uuid': notificar_devolucao_pc_uuid,
                    'notificacao_uuid': notificacao_uuid,
                    'acesso_de_suporte': acesso_de_suporte
                })
    
    # Como a visão SME não tem uma Unidade real, cria a unidade caso o usuário tenha essa visão
    if novo_suporte_unidade:
        if user.visoes.filter(nome='SME').exists() and not suporte:
            unidades.append(UNIDADE_SME)
    else:
        if user.visoes.filter(nome='SME').exists():
            unidades.append(UNIDADE_SME)

    return unidades

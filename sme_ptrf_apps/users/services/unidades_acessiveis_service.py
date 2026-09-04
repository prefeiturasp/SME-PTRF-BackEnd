from django.db.models import Q

from sme_ptrf_apps.core.models import Associacao, Unidade

# Mesmo UUID usado em get_unidades_do_usuario (visão SME não é uma Unidade real).
UUID_SME = "8919f454-bee5-419c-ad54-b2df27bf8007"


def unidades_acessiveis_do_usuario(user):
    """Unidades cuja despesa/receita o usuário pode ver ou alterar.

    - UE e suporte: unidades vinculadas em ``user.unidades``.
    - DRE: as DREs vinculadas e todas as UEs dessas DREs.
    - SME: todas as unidades (visão SME ou ``pode_acessar_sme``).

    Usado no recorte de retrieve/update/destroy (404 se a UE não estiver aqui)
    para não confirmar existência do UUID a quem não pode acessar a unidade.
    """
    if user is None or not getattr(user, 'is_authenticated', False):
        return Unidade.objects.none()

    tem_visao_sme = user.visoes.filter(nome='SME').exists()
    if tem_visao_sme or getattr(user, 'pode_acessar_sme', False):
        return Unidade.objects.all()

    unidades_diretas = user.unidades.all()
    dres = unidades_diretas.filter(tipo_unidade='DRE')

    return Unidade.objects.filter(
        Q(pk__in=unidades_diretas.values('pk')) | Q(dre__in=dres)
    ).distinct()


def filtrar_queryset_pelo_contexto_selecionado(qs, contexto_uuid, user):
    """Restringe o queryset à associação/unidade atualmente selecionada.

    ``contexto_uuid`` vem do front (localStorage ASSOCIACAO_UUID):
    - UUID de associação (visão UE / suporte numa escola);
    - UUID de unidade DRE (visão DRE);
    - UUID da SME.
    """
    if not contexto_uuid:
        return qs

    contexto_uuid = str(contexto_uuid)

    if contexto_uuid in (UUID_SME, 'SME'):
        if user.visoes.filter(nome='SME').exists() or getattr(user, 'pode_acessar_sme', False):
            return qs
        return qs.none()

    acessiveis = unidades_acessiveis_do_usuario(user)

    associacao = Associacao.objects.filter(uuid=contexto_uuid).first()
    if associacao:
        if not acessiveis.filter(pk=associacao.unidade_id).exists():
            return qs.none()
        return qs.filter(associacao=associacao)

    unidade = Unidade.objects.filter(uuid=contexto_uuid).first()
    if not unidade or not acessiveis.filter(pk=unidade.pk).exists():
        return qs.none()

    if unidade.tipo_unidade == 'DRE':
        return qs.filter(associacao__unidade__dre=unidade)
    return qs.filter(associacao__unidade=unidade)

from sme_ptrf_apps.core.models import Unidade, Periodo
from sme_ptrf_apps.dre.models import Atribuicao, TecnicoDre


def salvar_atualizar_atribuicao_em_lote(dados_atribuicoes):
    if not dados_atribuicoes.get('tecnico') or not dados_atribuicoes.get('periodo') or not dados_atribuicoes.get('unidades'):
        raise Exception("Os parâmetros não podem ser vazios ou nulos.")

    tecnico = TecnicoDre.by_uuid(dados_atribuicoes.get('tecnico'))
    periodo = Periodo.by_uuid(dados_atribuicoes.get('periodo'))

    for unidade_dict in dados_atribuicoes.get('unidades'):
        unidade = Unidade.by_uuid(unidade_dict['uuid'])
        kwargs = {"unidade__uuid": unidade_dict['uuid'], "periodo__uuid": periodo.uuid}
        atribuicao = Atribuicao.search(**kwargs).first()
        if atribuicao:
            atribuicao.tecnico = tecnico
            atribuicao.save()
        else:
            Atribuicao.objects.create(
                tecnico=tecnico,
                unidade=unidade,
                periodo=periodo
            )


def desatribuir_em_lote_por_unidade(dados_atribuicoes):
    if not dados_atribuicoes.get('periodo') or not dados_atribuicoes.get('unidades'):
        raise Exception("Os parâmetros não podem ser vazios ou nulos.")

    for unidade_dict in dados_atribuicoes.get('unidades'):
        kwargs = {"unidade__uuid": unidade_dict['uuid'], "periodo__uuid": dados_atribuicoes.get('periodo')}
        atribuicao = Atribuicao.search(**kwargs).first()
        if atribuicao:
            atribuicao.delete()


def troca_atribuicao_em_lote(dados_atribuicoes):
    if not dados_atribuicoes.get('tecnico_atual'):
        raise Exception("Os parâmetros não podem ser vazios ou nulos.")

    kwargs = {"tecnico__uuid": dados_atribuicoes.get('tecnico_atual')}
    atribuicoes = Atribuicao.search(**kwargs).all()
    tecnico_novo = TecnicoDre.objects.filter(uuid=dados_atribuicoes.get('tecnico_novo')).first()

    for atribuicao in atribuicoes:
        if tecnico_novo:
            atribuicao.tecnico = tecnico_novo
            atribuicao.save()
        else:
            atribuicao.delete()


def copia_atribuicoes_de_um_periodo(dados):
    if not dados.get('periodo_atual') or not dados.get('periodo_copiado') or not dados.get('dre_uuid'):
        raise Exception("Os parâmetros não podem ser vazios ou nulos.")

    for unidade in Unidade.objects.filter(dre__uuid=dados.get('dre_uuid')):
        kwargs = {"unidade__uuid": unidade.uuid, "periodo__uuid": dados.get('periodo_copiado')}
        atribuicao = Atribuicao.search(**kwargs).first()
        if atribuicao:
            kwargs = {"unidade__uuid": unidade.uuid, "periodo__uuid": dados.get('periodo_atual')}
            atribuicao_atual = Atribuicao.search(**kwargs).first()

            periodo_atual = Periodo.by_uuid(dados.get('periodo_atual'))
            if atribuicao_atual:
                atribuicao_atual.tecnico = atribuicao.tecnico
                atribuicao_atual.periodo = periodo_atual
                atribuicao_atual.save()
            else:
                Atribuicao.objects.create(
                    tecnico=atribuicao.tecnico,
                    unidade=atribuicao.unidade,
                    periodo=periodo_atual
                )
        else:
            kwargs = {"unidade__uuid": unidade.uuid, "periodo__uuid": dados.get('periodo_atual')}
            atribuicao_atual = Atribuicao.search(**kwargs).first()
            if atribuicao_atual:
                atribuicao_atual.delete()

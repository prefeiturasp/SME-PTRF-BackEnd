from sme_ptrf_apps.core.models import Unidade
from sme_ptrf_apps.dre.models import Atribuicao
from sme_ptrf_apps.dre.api.serializers.tecnico_dre_serializer import TecnicoDreLookUpSerializer


def monta_unidade_para_atribuicao(queryset, dre_uuid, periodo):
    list_unidades = []
    for unidade in queryset.filter(dre__uuid=dre_uuid).all():
        atribuicao = Atribuicao.objects.filter(unidade__uuid=unidade.uuid, periodo__uuid=periodo).first()
        d = {
            "uuid": str(unidade.uuid),
            "codigo_eol": unidade.codigo_eol,
            "nome": f'{unidade.tipo_unidade} {unidade.nome}',
            "atribuicao": {
                "id": atribuicao.id if atribuicao else "",
                "tecnico": TecnicoDreLookUpSerializer(atribuicao.tecnico).data if atribuicao else {}
            }
        }
        list_unidades.append(d)

    return list_unidades

from ..models import (GrupoVerificacaoRegularidade, VerificacaoRegularidadeAssociacao)
from ...core.models import Associacao


def verifica_regularidade_associacao(associacao_uuid):
    associacao = Associacao.by_uuid(associacao_uuid)

    grupos = []
    for grupo in GrupoVerificacaoRegularidade.objects.all():
        listas = []
        for lista in grupo.listas_de_verificacao.all():
            itens = []
            qtd_irregulares = 0
            for item in lista.itens_de_verificacao.all():
                verificacao = VerificacaoRegularidadeAssociacao.objects.filter(associacao=associacao,
                                                                               item_verificacao=item).first()
                if not verificacao or not verificacao.regular:
                    qtd_irregulares += 1

                itens.append(
                    {
                        'descricao': item.descricao,
                        'regular': verificacao.regular if verificacao else False,
                        'uuid': f'{item.uuid}'
                    }
                )
            listas.append(
                {
                    'itens_verificacao': itens,
                    'status_lista_verificacao': 'Regular' if qtd_irregulares == 0 else 'Pendente',
                    'titulo': lista.titulo,
                    'uuid': f'{lista.uuid}'
                }
            )
        grupos.append(
            {
                'listas_verificacao': listas,
                'titulo': grupo.titulo,
                'uuid': f'{grupo.uuid}'
            }
        )

    result = {
        'uuid': f'{associacao.uuid}',
        'verificacao_regularidade': {
            'grupos_verificacao': grupos
        }
    }
    return result

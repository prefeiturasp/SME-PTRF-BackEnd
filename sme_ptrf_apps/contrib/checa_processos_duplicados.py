from django.db.models import Count
from sme_ptrf_apps.core.models import ProcessoAssociacao  # Ajuste 'seu_app' para o nome real do seu app


def verificar_numeros_processo_duplicados():
    # Agrega os números de processo, contando quantas vezes cada um aparece
    duplicados = ProcessoAssociacao.objects.values('numero_processo')\
        .annotate(num_count=Count('numero_processo'))\
        .filter(num_count__gt=1)

    total_duplicados = 0

    if duplicados:
        print("Encontrados números de processo duplicados:")
        for item in duplicados:
            print(f"Numero de Processo: {item['numero_processo']}, Contagem: {item['num_count']}")
            total_duplicados += item['num_count'] - 1  # Contando apenas as entradas extras como duplicadas

            # Listando as instâncias específicas que têm números duplicados
            processos = ProcessoAssociacao.objects.filter(numero_processo=item['numero_processo'])
            for processo in processos:
                print(f" - ID: {processo.id}, Ano: {processo.ano}, UE: {processo.associacao.unidade.codigo_eol}-{processo.associacao.unidade.nome}")
    else:
        print("Não foram encontrados números de processo duplicados.")

    print(f"Total de casos de duplicidade: {total_duplicados}")

import datetime
import logging
from sme_ptrf_apps.core.models import PrestacaoConta
from sme_ptrf_apps.dre.models import PresenteAtaDre
from sme_ptrf_apps.dre.services.ata_pdf_parecer_tecnico_service import gerar_arquivo_ata_parecer_tecnico_pdf
from sme_ptrf_apps.core.services.ata_dados_service import data_por_extenso
from sme_ptrf_apps.core.services.dados_demo_financeiro_service import formata_data
from sme_ptrf_apps.utils.numero_por_extenso import real
from django.db.models import Q

LOGGER = logging.getLogger(__name__)


def gerar_arquivo_ata_parecer_tecnico(ata=None, dre=None, periodo=None, usuario=None, parcial=None):
    LOGGER.info(f"Gerando Arquivo da Ata, Ata {ata}, DRE {dre} e Período {periodo}")

    ata.arquivo_pdf_iniciar()

    try:
        dados_da_ata = informacoes_execucao_financeira_unidades_ata_parecer_tecnico_consolidado_dre(
            dre,
            periodo,
            ata_de_parecer_tecnico=ata,
            usuario=usuario,
            parcial=parcial
        )
        gerar_arquivo_ata_parecer_tecnico_pdf(dados_da_ata, ata)
        LOGGER.info(f'Gerando arquivo ata parecer técnico em PDF')
        ata.arquivo_pdf_concluir()
        return ata

    except Exception as e:
        LOGGER.info(f'FALHA AO GERAR O ARQUIVO DA ATA', e)
        ata.arquivo_pdf_nao_gerado()
        return None


def informacoes_execucao_financeira_unidades_ata_parecer_tecnico_consolidado_dre(dre, periodo, ata_de_parecer_tecnico=None, usuario=None, parcial=None):
    lista_contas_aprovadas = []  # PCs aprovadas precisam ser separadas por conta
    lista_contas_aprovadas_ressalva = []  # PCs aprovadas com ressalva precisam ser separadas por conta
    lista_contas_reprovadas = []  # PCs reprovadas precisam ser separadas por conta
    lista_motivos_aprovadas_ressalva = []
    lista_motivos_reprovacao = []

    titulo_sequencia_publicacao = None
    if parcial:
        eh_parcial = "Parcial" if parcial['parcial'] else "Final"

        sequencia_de_publicacao = parcial['sequencia_de_publicacao_atual']

        if eh_parcial == "Parcial":
            titulo_sequencia_publicacao = f'Publicação Parcial #{sequencia_de_publicacao}'
        else:
            titulo_sequencia_publicacao = "Publicação Única"

    motivo_retificacao = None
    eh_retificacao = False
    if ata_de_parecer_tecnico and ata_de_parecer_tecnico.consolidado_dre:
        if ata_de_parecer_tecnico.consolidado_dre.eh_retificacao:
            eh_retificacao = True
            motivo_retificacao = ata_de_parecer_tecnico.consolidado_dre.motivo_retificacao
            publicacao_parcial_que_gerou_a_retificacao = ata_de_parecer_tecnico.consolidado_dre.consolidado_retificado
            data_publicacao = publicacao_parcial_que_gerou_a_retificacao.data_publicacao if publicacao_parcial_que_gerou_a_retificacao and publicacao_parcial_que_gerou_a_retificacao.data_publicacao else ''
            titulo_sequencia_publicacao = f"Retificação da publicação de {data_publicacao.strftime('%d/%m/%Y')}"

    cabecalho = {
        "titulo": "Programa de Transferência de Recursos Financeiros -  PTRF",
        "sub_titulo": f"Diretoria Regional de Educação - {formata_nome_dre(dre.nome)}",
        "nome_ata": f"Ata de Parecer Técnico Conclusivo",
        "nome_dre": f"{formata_nome_dre(dre.nome)}",
        "data_geracao_documento": cria_data_geracao_documento(usuario, dre.nome),
        "numero_portaria": ata_de_parecer_tecnico.numero_portaria if ata_de_parecer_tecnico and ata_de_parecer_tecnico.numero_portaria else "--",
        "data_portaria": ata_de_parecer_tecnico.data_portaria if ata_de_parecer_tecnico and ata_de_parecer_tecnico.data_portaria else "--",
        "titulo_sequencia_publicacao": titulo_sequencia_publicacao,
    }
    dados_texto_da_ata = {
        "data_reuniao_por_extenso": data_por_extenso(ata_de_parecer_tecnico.data_reuniao) if ata_de_parecer_tecnico and ata_de_parecer_tecnico.data_reuniao else "---",
        "hora_reuniao": hora_por_extenso(ata_de_parecer_tecnico.hora_reuniao) if ata_de_parecer_tecnico and ata_de_parecer_tecnico.hora_reuniao else "---",
        "numero_ata": ata_de_parecer_tecnico.numero_ata if ata_de_parecer_tecnico and ata_de_parecer_tecnico.numero_ata else "---",
        'data_reuniao': ata_de_parecer_tecnico.data_reuniao if ata_de_parecer_tecnico and ata_de_parecer_tecnico.data_reuniao else "---",
        "periodo_data_inicio": formata_data(periodo.data_inicio_realizacao_despesas),
        "periodo_data_fim": formata_data(periodo.data_fim_realizacao_despesas),
        "comentarios": ata_de_parecer_tecnico.comentarios,
        "motivo_retificacao": motivo_retificacao
    }
    presentes_na_ata = {
        "presentes": get_presentes_na_ata(ata_de_parecer_tecnico)
    }

    lista_aprovadas = []  # Lista usada para separar por status aprovada
    lista_aprovadas_ressalva = []  # Lista usada para separar por status aprovada com ressalva
    lista_reprovadas = []  # Lista usada para separar por status reprovada

    informacoes = informacoes_pcs_aprovadas_aprovadas_com_ressalva_reprovadas_consolidado_dre(
        dre=dre,
        periodo=periodo,
        ata_de_parecer_tecnico=ata_de_parecer_tecnico
    )

    for info in informacoes:
        if info["status_prestacao_contas"] == "APROVADA":
            lista_aprovadas.append(info)  # Separando por aprovadas

        elif info["status_prestacao_contas"] == "APROVADA_RESSALVA":
            lista_aprovadas_ressalva.append(info)  # Separando por aprovadas com ressalva
            motivos = motivos_aprovacao_ressalva(info["uuid_pc"])
            lista_motivos_aprovadas_ressalva.append(motivos)

        elif info["status_prestacao_contas"] == "REPROVADA":
            lista_reprovadas.append(info)  # Separando por reprovadas
            motivos = motivos_reprovacao(info["uuid_pc"])
            lista_motivos_reprovacao.append(motivos)

    if len(lista_aprovadas) > 0:
        dados_aprovadas = {
            "info": lista_aprovadas
        }
        # Inserindo lista de PCs aprovadas por conta
        lista_contas_aprovadas.append(dados_aprovadas)

    if len(lista_aprovadas_ressalva) > 0:
        dados_aprovadas_ressalva = {
            "info": lista_aprovadas_ressalva
        }
        # Inserindo lista de PCs aprovadas com ressalva por conta
        lista_contas_aprovadas_ressalva.append(dados_aprovadas_ressalva)

    if len(lista_reprovadas) > 0:
        dados_reprovadas = {
            "info": lista_reprovadas
        }
        # Inserindo lista de PCs reprovadas com ressalva por conta
        lista_contas_reprovadas.append(dados_reprovadas)

    dado = {
        "cabecalho": cabecalho,
        "eh_retificacao": eh_retificacao,
        "dados_texto_da_ata": dados_texto_da_ata,
        "presentes_na_ata": presentes_na_ata,
        "aprovadas": {
            "contas": lista_contas_aprovadas
        },
        "aprovadas_ressalva": {
            "contas": lista_contas_aprovadas_ressalva,
            "motivos": lista_motivos_aprovadas_ressalva
        },
        "reprovadas": {
            "contas": lista_contas_reprovadas,
            "motivos": lista_motivos_reprovacao
        }
    }

    return dado


def informacoes_pcs_aprovadas_aprovadas_com_ressalva_reprovadas_consolidado_dre(dre, periodo, ata_de_parecer_tecnico):

    from ..services.relatorio_consolidado_service import get_teste_motivos_reprovacao, get_motivos_aprovacao_ressalva

    consolidado_dre = None

    # TODO remover comentários após testes
    # Tratativa dos Bugs: 91797, 93549 e 93018 da Sprint 65
    # Gerava divergência em Tela da  Visualização da Ata Parecer Técnico em Tela
    # Quando uma prévia era gerada com um número X de PCS e depois concluisse mais PCS sempre olhava para o numero
    # Que já estava na Prévia, não levava em consideração as novas PCs concluídas
    # Foi adicionado and consolidado_dre.versao == "FINAL" para verificar se passa ou não o consolidado

    if ata_de_parecer_tecnico:
        consolidado_dre = ata_de_parecer_tecnico.consolidado_dre

    if consolidado_dre and consolidado_dre.versao == "FINAL":
        prestacoes = consolidado_dre.pcs_do_consolidado.all().order_by("associacao__unidade__tipo_unidade", "associacao__unidade__nome")
    else:
        prestacoes = PrestacaoConta.objects.filter(
            periodo=periodo,
            associacao__unidade__dre=dre,
        )
        prestacoes = prestacoes.filter(
            Q(status=PrestacaoConta.STATUS_APROVADA) |
            Q(status=PrestacaoConta.STATUS_APROVADA_RESSALVA) |
            Q(status=PrestacaoConta.STATUS_REPROVADA)
        )
        prestacoes = prestacoes.filter(publicada=False)
        prestacoes = prestacoes.order_by("associacao__unidade__tipo_unidade", "associacao__unidade__nome")

    resultado = []
    for prestacao in prestacoes:

        status_prestacao_conta = prestacao.status if not prestacao.em_retificacao else prestacao.status_anterior_a_retificacao

        dado = {
            'unidade': {
                'uuid': f'{prestacao.associacao.unidade.uuid}',
                'codigo_eol': prestacao.associacao.unidade.codigo_eol,
                'tipo_unidade': prestacao.associacao.unidade.tipo_unidade,
                'nome': prestacao.associacao.unidade.nome,
                'sigla': prestacao.associacao.unidade.sigla,
            },

            'status_prestacao_contas': status_prestacao_conta,
            'uuid_pc': prestacao.uuid,
        }

        if status_prestacao_conta == "REPROVADA":
            dado["motivos_reprovacao"] = get_teste_motivos_reprovacao(prestacao)
        elif status_prestacao_conta == "APROVADA_RESSALVA":
            dado["motivos_aprovada_ressalva"] = get_motivos_aprovacao_ressalva(prestacao)
            dado["recomendacoes"] = prestacao.recomendacoes

        resultado.append(dado)

    resultado = sorted(resultado, key=lambda row: row['status_prestacao_contas'])

    return resultado


def get_presentes_na_ata(ata):
    ata_id = ata.id if ata and ata.id else None
    presentes_na_ata = []

    if ata_id:
        queryset_presentes_na_ata = PresenteAtaDre.objects.filter(ata=ata_id)
        for presente in queryset_presentes_na_ata:
            dados_presentes = {
                "nome": presente.nome if presente.nome else "",
                "rf": presente.rf if presente.rf else "",
                "cargo": presente.cargo if presente.cargo else ""
            }
            presentes_na_ata.append(dados_presentes)

    return presentes_na_ata


def cria_data_geracao_documento(usuario, dre_nome):
    data_geracao = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    quem_gerou = "" if usuario == "" else f"pelo usuário {usuario}"
    texto = f"DRE {formata_nome_dre(dre_nome)} - Ata gerada {quem_gerou}, via SIG-Escola, em {data_geracao}"

    return texto


def hora_por_extenso(hora_da_reuniao):
    hora_reuniao = hora_da_reuniao.strftime('%H:%M')
    hora, minuto = hora_reuniao.split(":")

    # Corrigindo os plurais de hora e minuto
    if hora == "01" or hora == "00":
        texto_hora = "hora"
    else:
        texto_hora = "horas"

    if minuto == "01" or minuto == "00":
        texto_minuto = "minuto"
    else:
        texto_minuto = "minutos"

    # Corrigindo o genero de hora
    hora_genero = real(hora).replace("um", "uma").replace("dois", "duas")

    if real(minuto) == "zero":
        hora_extenso = f'{hora_genero} {texto_hora}'
    else:
        hora_extenso = f'{hora_genero} {texto_hora} e {real(minuto)} {texto_minuto}'

    return hora_extenso


def formata_nome_dre(nome):
    if nome:
        nome_dre = nome.upper()
        if "DIRETORIA REGIONAL DE EDUCACAO" in nome_dre:
            nome_dre = nome_dre.replace("DIRETORIA REGIONAL DE EDUCACAO", "")
            nome_dre = nome_dre.strip()

        return nome_dre
    else:
        return ""


def motivos_aprovacao_ressalva(uuid_pc):
    pc = PrestacaoConta.objects.filter(uuid=uuid_pc).first()
    lista_motivos_e_outros = []

    motivos = pc.motivos_aprovacao_ressalva.values("motivo")
    for motivo in motivos:
        lista_motivos_e_outros.append(motivo["motivo"])

    outros_motivos = pc.outros_motivos_aprovacao_ressalva
    if outros_motivos:
        lista_motivos_e_outros.append(outros_motivos)

    dados = {
        "unidade": {
            'codigo_eol': pc.associacao.unidade.codigo_eol,
            'tipo_unidade': pc.associacao.unidade.tipo_unidade,
            'nome': pc.associacao.unidade.nome,
        },
        "motivos": lista_motivos_e_outros,
        "recomendacoes": pc.recomendacoes
    }

    return dados


def motivos_reprovacao(uuid_pc):
    pc = PrestacaoConta.objects.filter(uuid=uuid_pc).first()
    lista_motivos_e_outros = []

    motivos = pc.motivos_reprovacao.values("motivo")
    for motivo in motivos:
        lista_motivos_e_outros.append(motivo["motivo"])

    outros_motivos = pc.outros_motivos_reprovacao
    if outros_motivos:
        lista_motivos_e_outros.append(outros_motivos)

    dados = {
        "unidade": {
            'codigo_eol': pc.associacao.unidade.codigo_eol,
            'tipo_unidade': pc.associacao.unidade.tipo_unidade,
            'nome': pc.associacao.unidade.nome,
        },
        "motivos": lista_motivos_e_outros
    }

    return dados

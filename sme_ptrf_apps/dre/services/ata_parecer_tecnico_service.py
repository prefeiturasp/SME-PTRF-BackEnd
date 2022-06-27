import datetime
import logging
from sme_ptrf_apps.core.models import TipoConta, PrestacaoConta
from sme_ptrf_apps.dre.models import PresenteAtaDre
from sme_ptrf_apps.dre.services import informacoes_pcs_do_consolidado_dre
from sme_ptrf_apps.dre.services.ata_pdf_parecer_tecnico_service import gerar_arquivo_ata_parecer_tecnico_pdf
from sme_ptrf_apps.core.services.ata_dados_service import data_por_extenso
from sme_ptrf_apps.core.services.dados_demo_financeiro_service import formata_data
from sme_ptrf_apps.utils.numero_por_extenso import real

LOGGER = logging.getLogger(__name__)


def gerar_arquivo_ata_parecer_tecnico(ata=None, dre=None, periodo=None, usuario=None):
    LOGGER.info(f"Gerando Arquivo da Ata, Ata {ata}, DRE {dre} e Período {periodo}")

    ata.arquivo_pdf_iniciar()

    try:
        dados_da_ata = informacoes_execucao_financeira_unidades_ata_parecer_tecnico(dre, periodo, ata, usuario)
        gerar_arquivo_ata_parecer_tecnico_pdf(dados_da_ata, ata)
        LOGGER.info(f'Gerando arquivo ata parecer técnico em PDF')
        ata.arquivo_pdf_concluir()
        return ata

    except Exception as e:
        LOGGER.info(f'FALHA AO GERAR O ARQUIVO DA ATA', e)
        ata.arquivo_pdf_nao_gerado()
        return None


def informacoes_execucao_financeira_unidades_ata_parecer_tecnico(dre, periodo, ata=None, usuario=None):
    # Está primeira conta encontrada será usada para PCs reprovadas, pois não necessitam de distinção por conta
    primeira_conta_encontrada = TipoConta.objects.first()

    contas = TipoConta.objects.all()

    lista_contas_aprovadas = []  # PCs aprovadas precisam ser separadas por conta
    lista_contas_aprovadas_ressalva = []  # PCs aprovadas com ressalva precisam ser separadas por conta
    lista_contas_reprovadas = []  # PCs reprovadas precisam ser separadas por conta
    lista_motivos_aprovadas_ressalva = []
    lista_motivos_reprovacao = []

    # lista utilizada para não duplicar contas reprovadas, remover ao refatorar
    # lista_reprovadas = []  # PCs reprovadas não precisam ser separadas por conta

    cabecalho = {
        "titulo": "Programa de Transferência de Recursos Financeiros -  PTRF",
        "sub_titulo": f"Diretoria Regional de Educação - {formata_nome_dre(dre.nome)}",
        "nome_ata": f"Ata de Parecer Técnico Conclusivo",
        "nome_dre": f"{formata_nome_dre(dre.nome)}",
        "data_geracao_documento": cria_data_geracao_documento(usuario, dre.nome),
        "numero_portaria": ata.numero_portaria if ata and ata.numero_portaria else "--",
        "data_portaria": ata.data_portaria if ata and ata.data_portaria else "--",
    }
    dados_texto_da_ata = {
        "data_reuniao_por_extenso": data_por_extenso(ata.data_reuniao) if ata and ata.data_reuniao else "---",
        "hora_reuniao": hora_por_extenso(ata.hora_reuniao) if ata and ata.hora_reuniao else "---",
        "numero_ata": ata.numero_ata if ata and ata.numero_ata else "---",
        'data_reuniao': ata.data_reuniao if ata and ata.data_reuniao else "---",
        "periodo_data_inicio": formata_data(periodo.data_inicio_realizacao_despesas),
        "periodo_data_fim": formata_data(periodo.data_fim_realizacao_despesas),
    }
    presentes_na_ata = {
        "presentes": get_presentes_na_ata(ata)
    }

    for conta in contas:
        lista_aprovadas = []  # Lista usada para separar por status aprovada
        lista_aprovadas_ressalva = []  # Lista usada para separar por status aprovada com ressalva
        lista_reprovadas = []  # Lista usada para separar por status reprovada

        informacoes = informacoes_pcs_do_consolidado_dre(
            dre=dre,
            periodo=periodo,
            tipo_conta=conta,
        )

        for info in informacoes:
            if info["status_prestacao_contas"] == "APROVADA":
                lista_aprovadas.append(info)  # Separando por aprovadas
            elif info["status_prestacao_contas"] == "APROVADA_RESSALVA":
                lista_aprovadas_ressalva.append(info)  # Separando por aprovadas com ressalva

                if not conta.nome == primeira_conta_encontrada.nome:
                    continue

                motivos = motivos_aprovacao_ressalva(info["uuid_pc"])
                lista_motivos_aprovadas_ressalva.append(motivos)
            elif info["status_prestacao_contas"] == "REPROVADA":
                lista_reprovadas.append(info)  # Separando por reprovadas

                if not conta.nome == primeira_conta_encontrada.nome:
                    continue

                motivos = motivos_reprovacao(info["uuid_pc"])
                lista_motivos_reprovacao.append(motivos)

                # Essa lógica estava sendo utilizada para não duplicar informações de contas reprovadas, pois não eram
                # separadas por tipo de conta, agora serão separadas por tipo de conta, ao refatorar,
                # remover essa logica
                # PCs com status de reprovada não necessitam de distinção por conta
                # if not conta.nome == primeira_conta_encontrada.nome:
                #     continue
                #
                # lista_reprovadas.append(info)
                # motivos = motivos_reprovacao(info["uuid_pc"])
                # lista_motivos_reprovacao.append(motivos)

        if len(lista_aprovadas) > 0:
            dados_aprovadas = {
                "nome": f"{conta.nome}",
                "info": lista_aprovadas
            }
            # Inserindo lista de PCs aprovadas por conta
            lista_contas_aprovadas.append(dados_aprovadas)

        if len(lista_aprovadas_ressalva) > 0:
            dados_aprovadas_ressalva = {
                "nome": f"{conta.nome}",
                "info": lista_aprovadas_ressalva
            }
            # Inserindo lista de PCs aprovadas com ressalva por conta
            lista_contas_aprovadas_ressalva.append(dados_aprovadas_ressalva)

        if len(lista_reprovadas) > 0:
            dados_reprovadas = {
                "nome": f"{conta.nome}",
                "info": lista_reprovadas
            }
            # Inserindo lista de PCs reprovadas com ressalva por conta
            lista_contas_reprovadas.append(dados_reprovadas)

    dado = {
        "cabecalho": cabecalho,
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
    data_geracao = datetime.date.today().strftime("%d/%m/%Y")
    quem_gerou = "" if usuario == "" else f"pelo usuário {usuario}"
    texto = f"Ata PDF gerada pelo Sig_Escola em {data_geracao} {quem_gerou} para a DIRETORIA REGIONAL DE EDUCAÇÃO {formata_nome_dre(dre_nome)}"

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

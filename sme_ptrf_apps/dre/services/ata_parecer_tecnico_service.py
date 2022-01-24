from sme_ptrf_apps.core.models import TipoConta, PrestacaoConta
from sme_ptrf_apps.dre.services import informacoes_execucao_financeira_unidades


def informacoes_execucao_financeira_unidades_ata_parecer_tecnico(dre, periodo):
    # Está primeira conta encontrada será usada para PCs reprovadas, pois não necessitam de distinção por conta
    primeira_conta_encontrada = TipoConta.objects.first()

    contas = TipoConta.objects.all()

    lista_contas_aprovadas = []  # PCs aprovadas precisam ser separadas por conta
    lista_contas_aprovadas_ressalva = []  # PCs aprovadas com ressalva precisam ser separadas por conta
    lista_motivos_aprovadas_ressalva = []
    lista_motivos_reprovacao = []
    lista_reprovadas = []  # PCs reprovadas não precisam ser separadas por conta

    for conta in contas:
        lista_aprovadas = []  # Lista usada para separar por status aprovada
        lista_aprovadas_ressalva = []  # Lista usada para separar por status aprovada com ressalva

        informacoes = informacoes_execucao_financeira_unidades(
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

                teste = motivos_aprovacao_ressalva(info["uuid_pc"])
                lista_motivos_aprovadas_ressalva.append(teste)
            elif info["status_prestacao_contas"] == "REPROVADA":
                # PCs com status de reprovada não necessitam de distinção por conta
                if not conta.nome == primeira_conta_encontrada.nome:
                    continue

                lista_reprovadas.append(info)
                teste = motivos_reprovacao(info["uuid_pc"])
                lista_motivos_reprovacao.append(teste)

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

    dado = {
        "aprovadas": {
            "contas": lista_contas_aprovadas
        },
        "aprovadas_ressalva": {
            "contas": lista_contas_aprovadas_ressalva,
            "motivos": lista_motivos_aprovadas_ressalva
        },
        "reprovadas": {
            "info": lista_reprovadas,
            "motivos": lista_motivos_reprovacao
        }
    }

    return dado


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
        "motivos": lista_motivos_e_outros
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



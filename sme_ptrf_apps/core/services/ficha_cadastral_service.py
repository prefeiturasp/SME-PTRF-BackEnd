from waffle import flag_is_active

from sme_ptrf_apps.core.services.exporta_associacao import _email_para_planilha
from sme_ptrf_apps.users.permissoes import PermissaoCRUD

PERMISSAO_FICHA_CADASTRAL_SEM_ANONIMIZACAO = 'access_ficha_cadastral_sem_anonimizacao'
DIGITOS_VISIVEIS_CEP = 3


def dados_presidente_para_ficha(associacao, request):
    """Presidente da lista atual do mandato vigente, conforme a flag de membros.

    historico-de-membros-v2 tem prioridade. Sem flags, usa a lista de membros atual.
    """
    if flag_is_active(request, 'historico-de-membros-v2'):
        return associacao.dados_presidente_composicao_vigente_vacancia()
    if flag_is_active(request, 'historico-de-membros'):
        return associacao.dados_presidente_composicao_vigente()
    return _dados_presidente_da_lista_atual(associacao)


def dados_presidente_ficha_para_usuario(associacao, request):
    dados = dados_presidente_para_ficha(associacao, request)
    if PermissaoCRUD().has_perm(PERMISSAO_FICHA_CADASTRAL_SEM_ANONIMIZACAO, request.user):
        return dados
    return anonimizar_dados_presidente(dados)


def _dados_presidente_da_lista_atual(associacao):
    presidente = associacao.presidente_associacao or {}
    dados = {
        "nome": "",
        "cargo_educacao": "",
        "telefone": "",
        "email": "",
        "endereco": "",
        "complemento": "",
        "bairro": "",
        "cep": "",
        "municipio": "",
        "uf": "",
    }
    dados["nome"] = presidente.get("nome") or ""
    dados["cargo_educacao"] = presidente.get("cargo_educacao") or ""
    dados["telefone"] = presidente.get("telefone") or ""
    dados["email"] = presidente.get("email") or ""
    dados["endereco"] = presidente.get("endereco") or ""
    dados["complemento"] = presidente.get("complemento") or ""
    dados["bairro"] = presidente.get("bairro") or ""
    dados["cep"] = presidente.get("cep") or ""
    dados["municipio"] = presidente.get("municipio") or ""
    dados["uf"] = presidente.get("uf") or ""
    return dados


def anonimizar_dados_presidente(dados):
    dados = dados or {}
    return {
        "nome": dados.get("nome") or "",
        "cargo_educacao": dados.get("cargo_educacao") or "",
        "telefone": anonimizar_telefone(dados.get("telefone")),
        "email": _email_para_planilha(dados.get("email")),
        "endereco": anonimizar_extremidades(dados.get("endereco"), 2, 2),
        "complemento": anonimizar_extremidades(dados.get("complemento"), 2, 2),
        "bairro": anonimizar_extremidades(dados.get("bairro"), 1, 1),
        "cep": anonimizar_cep(dados.get("cep")),
        "municipio": anonimizar_extremidades(dados.get("municipio"), 2, 2),
        "uf": dados.get("uf") or "",
    }


def anonimizar_extremidades(valor, inicio, fim):
    texto = _texto(valor)
    if not texto:
        return ""
    if len(texto) <= inicio + fim:
        return "X" * len(texto)
    return f"{texto[:inicio]}{'X' * (len(texto) - inicio - fim)}{texto[-fim:]}"


def anonimizar_telefone(telefone):
    """Mantém o DDD e as 2 primeiras e 2 últimas posições do número.

    (11)99550-9090 -> (11)99XXX-XX90
    """
    texto = _texto(telefone)
    if not texto:
        return ""

    indices_digitos = [indice for indice, caractere in enumerate(texto) if caractere.isdigit()]
    if not indices_digitos:
        return texto

    if len(indices_digitos) >= 10:
        manter = set(indices_digitos[:2])
        restante = indices_digitos[2:]
    else:
        manter = set()
        restante = indices_digitos

    if len(restante) > 4:
        manter.update(restante[:2])
        manter.update(restante[-2:])
    else:
        manter.update(restante)

    caracteres = list(texto)
    for indice in indices_digitos:
        if indice not in manter:
            caracteres[indice] = "X"
    return "".join(caracteres)


def anonimizar_cep(cep):
    texto = _texto(cep)
    if not texto:
        return ""

    digitos_vistos = 0
    caracteres = []
    for caractere in texto:
        if caractere.isdigit():
            digitos_vistos += 1
            caracteres.append(caractere if digitos_vistos <= DIGITOS_VISIVEIS_CEP else "X")
        else:
            caracteres.append(caractere)
    return "".join(caracteres)


def _texto(valor):
    if valor is None:
        return ""
    return str(valor).strip()

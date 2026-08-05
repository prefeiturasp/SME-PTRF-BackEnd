from django.utils.safestring import mark_safe


def text_fixed_default_text_a_b_c():
    return "as prestações de contas das Associações das unidades abaixo relacionadas"


def fixed_text_introducao_ata():
    return "___ dias do mês de ___ de ___, às zero hora, reuniu-se a [exibe nome da comissão responsável pela" \
        "análise de PC do recurso] da Diretoria Regional de Educação [exibe a DRE correspondente do consolidado], "\
        "instituída pela Portaria DRE-[exibe a DRE correspondente do consolidado] nº _______ de __________, " \
        "para análise das prestações de contas dos recursos transferidos pelo [exibe o recurso correspondente], " \
        "período de [exibe o período correspondente do consolidado]"


def add_text_parameterized_text(parameterized_text):
    if parameterized_text:
        return f", {parameterized_text}"

    return "."


def fixed_text_texto_letra(letter="A", parameterized_text="", habilita_aprovacao_com_ressalva=False):
    text_letter = "a) <strong style='color: #297805;'>APROVAR</strong>"

    if letter == "B":
        text_letter = "b) <strong style='color: #297805;'>APROVAR COM RESSALVAS</strong>"

    if letter == "C":
        alt_letter = "c" if habilita_aprovacao_com_ressalva else "b"
        text_letter = f"{alt_letter}) <strong style='color: #b40c02;'>REJEITAR</strong>"

    return mark_safe(
        f"<p style='display: inline;'>{text_letter} "
        f"{text_fixed_default_text_a_b_c()}{add_text_parameterized_text(parameterized_text)}</p>")


def process_texto_letra_d(text, habilita_aprovacao_com_ressalva=False):
    if not text:
        return ""

    letter = "d" if habilita_aprovacao_com_ressalva else "c"

    return mark_safe(
        f"<p style='display: inline;'>{letter}) {text}</p>")


def process_texto_introducao(text):
    if not text:
        return "."

    return f", {text}"

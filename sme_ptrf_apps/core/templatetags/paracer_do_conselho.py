from django import template

import logging

register = template.Library()

LOGGER = logging.getLogger(__name__)


@register.simple_tag(name='parecer_do_conselho')
def parecer_do_conselho(parecer_conselho):
    texto_parecer = ""

    if parecer_conselho == "APROVADA":
        texto_parecer = "Os membros do Conselho Fiscal, à vista dos registros contábeis e verificando nos documentos apresentados a exatidão das despesas realizadas, julgaram exata a presente prestação de contas considerando-a em condições de ser aprovada e emitindo parecer favorável à sua aprovação."
    elif parecer_conselho == "REJEITADA":
        texto_parecer = "Os membros do Conselho Fiscal, à vista dos registros contábeis e verificando nos documentos apresentados, não consideram a presente prestação de contas em condições de ser aprovada emitindo parecer contrário à sua aprovação."

    return texto_parecer

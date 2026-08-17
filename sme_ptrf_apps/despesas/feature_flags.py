from waffle import flag_is_active


def despesas_pipeline_ativa(request) -> bool:
    """
        True quando a flag 'despesas-pipeline' vale para ESTE request —
        respeita everyone, percentual, grupo, usuário e staff/superuser.
        Substitui o filtro manual `Flag.objects.filter(everyone=True)`,
        que ignora todo o resto do targeting do waffle.
    """
    if request is None:
        return False
    return flag_is_active(request, "despesas-pipeline")

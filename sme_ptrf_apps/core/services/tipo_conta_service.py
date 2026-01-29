from django.apps import apps
from functools import lru_cache
from django.db import models
from django.core.exceptions import ValidationError

from sme_ptrf_apps.core.models.tipo_conta import TipoConta


@lru_cache
def _models_com_fk_para_tipo_conta():
    TipoConta = apps.get_model('core', 'TipoConta')
    refs = []

    for model in apps.get_models():
        for field in model._meta.fields:
            if (
                isinstance(field, models.ForeignKey) and
                field.related_model == TipoConta
            ):
                refs.append((model, field.name))

    return refs


def tipo_conta_em_uso(tipo_conta):
    for model, field_name in _models_com_fk_para_tipo_conta():
        if model.objects.filter(**{field_name: tipo_conta}).exists():
            return True
    return False


def validar_troca_recurso(tipo_conta, recurso_novo):
    if not tipo_conta.pk:
        return

    recurso_antigo_id = (
        TipoConta.objects.filter(pk=tipo_conta.pk).values_list('recurso_id', flat=True).first()
    )

    if recurso_antigo_id == recurso_novo.id:
        return

    if tipo_conta_em_uso(tipo_conta):
        raise ValidationError(
            "Não é possível alterar o recurso de um tipo de conta já utilizado."
        )

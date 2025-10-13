from django.db import models


class StatusChoices(models.IntegerChoices):
    ATIVO = 1, "Ativo"
    INATIVO = 0, "Inativo"

    @classmethod
    def to_dict(cls):
        return [dict(key=key.value, value=key.label) for key in cls]

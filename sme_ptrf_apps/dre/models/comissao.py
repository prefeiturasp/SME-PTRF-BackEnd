from django.core.exceptions import ValidationError
from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class Comissao(ModeloIdNome):
    history = AuditlogHistoryField()

    recursos = models.ManyToManyField('core.Recurso', related_name='comissoes', blank=False)

    responsavel_analise_pc = models.BooleanField(
        default=False,
        verbose_name="Responsável pela análise de prestação de contas?",
        help_text="Indica se esta comissão é responsável pela análise de prestação de contas do recurso"
    )

    class Meta:
        verbose_name = "Comissão"
        verbose_name_plural = "Comissões"

    @classmethod
    def is_valid_data(cls, nome, recursos=None, responsavel_analise_pc=False, instance_id=None):
        nome = ' '.join(nome.split()) if nome else ''

        if not nome:
            return False, "O campo 'nome' é obrigatório."

        if recursos is None or not isinstance(recursos, list) or len(recursos) <= 0:
            return False, "O campo 'recursos' é obrigatório"

        already_exists_with_same_name_and_recursos = cls.objects.filter(
            nome=nome,
            recursos__in=recursos
        ).exclude(id=instance_id).exists()

        if already_exists_with_same_name_and_recursos:
            return False, "Já existe uma comissão com o mesmo nome no recurso selecionado."

        if responsavel_analise_pc:
            already_exists_responsavel_analise_pc = cls.objects.filter(
                responsavel_analise_pc=responsavel_analise_pc,
                recursos__in=recursos
            ).exclude(id=instance_id).exists()

            if already_exists_responsavel_analise_pc:
                return False, "Um ou mais recursos selecionados já estão associados a uma comissão de análise de prestação de contas."

        return True, ""


    def _recursos_para_validacao(self):
        recursos = getattr(self, '_recursos_validacao', None)

        if recursos is not None:
            return list(recursos)

        if self.pk is None:
            return []

        return list(self.recursos.all())

    def clean(self):
        self.nome = ' '.join(self.nome.split()) if self.nome else ''

        is_valid, error_message = self.is_valid_data(
            nome=self.nome,
            recursos=self._recursos_para_validacao(),
            responsavel_analise_pc=self.responsavel_analise_pc,
            instance_id=self.pk
        )

        if not is_valid:
            raise ValidationError(error_message)



auditlog.register(Comissao)

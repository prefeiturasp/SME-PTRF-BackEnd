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

    @staticmethod
    def get_membros_comissao(comissao_instance):
        return comissao_instance.membros.all()

    @classmethod
    def verifica_dres_membros_comissao_tem_recursos(cls, comissao_instance, recursos):
        from sme_ptrf_apps.core.services.recursos_service import RecursoService

        membros_comissao = cls.get_membros_comissao(comissao_instance)
        list_recursos_id = [recurso.id for recurso in recursos]

        for membro in membros_comissao:
            recursos_dre_membro = RecursoService.por_dre(membro.dre).values_list('id', flat=True)

            existe_recurso_comum = any(recurso_id in list_recursos_id for recurso_id in recursos_dre_membro)
            if not existe_recurso_comum:
                return False

        return True

    @classmethod
    def is_valid_data(cls, nome, recursos=None, responsavel_analise_pc=False, instance_id=None):
        comissao = None
        nome = ' '.join(nome.split()) if nome else ''

        if not nome:
            return False, "O campo 'nome' é obrigatório."

        if instance_id:
            try:
                comissao = cls.objects.get(pk=instance_id)
            except cls.DoesNotExist:
                return False, "Comissão não encontrada para o ID fornecido."
            except Exception:
                return False, "Ocorreu um erro ao validar a comissão."

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

        if instance_id and len(cls.get_membros_comissao(comissao)) > 0:
            if not cls.verifica_dres_membros_comissao_tem_recursos(comissao, recursos):
                return False, "Não é possível editar esta comissão, pois ela já possui membros associados que não têm acesso aos recursos selecionados."

        return True, ""

    @classmethod
    def get_comissao_responsavel_analise_pc_por_recurso(cls, recurso):
        comissoes = cls.objects.filter(recursos=recurso, responsavel_analise_pc=True)

        if comissoes.exists():
            return comissoes.first()

        return None

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

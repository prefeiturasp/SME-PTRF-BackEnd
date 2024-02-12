from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.core.exceptions import ValidationError
from datetime import date


class Mandato(ModeloBase):
    history = AuditlogHistoryField()
    referencia_mandato = models.CharField('Referência do mandato', max_length=50)
    data_inicial = models.DateField(verbose_name='Data de início do mandato')
    data_final = models.DateField(verbose_name='Data de término do mandato')

    class Meta:
        verbose_name = 'Mandato'
        verbose_name_plural = 'Mandatos'

    def __str__(self):
        return self.referencia_mandato


    def clean(self):
        super().clean()

        # Verificar se a data final é menor que a data inicial
        if self.data_final < self.data_inicial:
            raise ValidationError('A data final não pode ser menor que a data inicial')

        # Verificar se a data inicial está dentro de outro mandato existente
        if self.data_inicial is not None and self.data_final is not None:
            mandatos = Mandato.objects.filter(data_inicial__lte=self.data_inicial, data_final__gte=self.data_inicial)

            if self.pk:
                mandatos = mandatos.exclude(pk=self.pk)  # Excluir o próprio objeto atual ao verificar colisões

            if mandatos.exists():
                raise ValidationError('A data inicial informada é de vigência de outro mandato cadastrado.')

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    def eh_mandato_vigente(self):
        from ..services import ServicoMandatoVigente
        servico_mandato_vigente = ServicoMandatoVigente()
        mandato_vigente = servico_mandato_vigente.get_mandato_vigente()

        return self == mandato_vigente

    def eh_mandato_futuro(self):
        from ..services import ServicoMandatoVigente
        servico_mandato_vigente = ServicoMandatoVigente()
        mandato_vigente = servico_mandato_vigente.get_mandato_vigente()

        if mandato_vigente:
            return self.data_inicial > mandato_vigente.data_final
        else:
            data_atual = date.today()
            return self.data_inicial > data_atual

    def possui_composicoes(self):
        return self.composicoes_do_mandato.exists()

    def possui_composicoes_com_data_final_maior_que_a_informada(self, data):
        if self.possui_composicoes():
            composicoes_encontradas = self.composicoes_do_mandato.filter(data_final__gt=data)

            return composicoes_encontradas.exists()

        return False

    def att_data_inicio_composicoes_e_cargos_composicoes(self, data_inicial, nova_data):
        for composicao in self.composicoes_do_mandato.filter(data_inicial=data_inicial):
            composicao.data_inicial = nova_data
            composicao.save()

            for cargo_composicao in composicao.cargos_da_composicao_da_composicao.all():
                if cargo_composicao.data_inicio_posterior_a_data_informada(nova_data):
                    continue

                cargo_composicao.data_inicio_no_cargo = nova_data
                cargo_composicao.save()

    def att_data_fim_composicoes_e_cargos_composicoes(self, data_final, nova_data):
        for composicao in self.composicoes_do_mandato.filter(data_final=data_final):
            composicao.data_final = nova_data
            composicao.save()

            for cargo_composicao in composicao.cargos_da_composicao_da_composicao.all():
                cargo_composicao.data_fim_no_cargo = nova_data
                cargo_composicao.save()


auditlog.register(Mandato)

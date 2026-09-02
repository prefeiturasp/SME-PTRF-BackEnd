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

    def att_data_inicio_composicao_vacancia(self, data_inicial_antiga: date, nova_data: date) -> None:
        """ Histórico de Membros V2 - equivalente a `att_data_inicio_composicoes_e_cargos_composicoes`
            mas não reflete em dados do Histórico de Membros(flag) antigo.
            Ao contrário da estrutura antiga, esta nova versão guarda vigentes e encerrados na mesma composição,
            por isso o filtro é por igualdade exata à data antiga, nunca "empurra tudo que for anterior à
            nova data".

            Só deve ser chamado após `possui_cargo_vacancia_incompativel_com_nova_data_inicial`
            confirmar que não há conflito com `att_data_fim_composicao_vacancia`

            Args:
                `data_inicial_antiga`: valor de `data_inicial` do mandato antes da edição
                `nova_data`: novo valor de `data_inicial` do mandato
        """
        from .cargo_composicao_vacancia import CargoComposicaoVacancia

        # Atualiza data inicio no cargo do CargoComposicao
        CargoComposicaoVacancia.objects.filter(
            composicao__mandato=self,
            data_inicio_no_cargo=data_inicial_antiga,
        ).update(data_inicio_no_cargo=nova_data)

    def att_data_fim_composicao_vacancia(self, data_final_antiga: date, nova_data: date) -> None:
        """ Histórico de Membros V2 - equivalente a `att_data_fim_composicoes_e_cargos_composicoes`

            Atualiza `data_final`/`data_fim_no_cargo` só de quem hoje acompanha o "vigente"
            (data_fim_no_cargo == data_final antiga do mandato) ocupados e vagos.
            Registros encerrados no meio do mandato mantem sua data histórica intacta.

            Só deve ser chamado após `possui_cargo_vacancia_incompativel_com_nova_data_final`
            confirmar que não há conflito.

            Args:
                `data_final_antiga`: valor de `data_final` do mandato antes da edição
                `nova_data`: novo valor de `data_final` do mandato
        """
        # Atualiza data fim no cargo do CargoComposicao
        from .cargo_composicao_vacancia import CargoComposicaoVacancia
        CargoComposicaoVacancia.objects.filter(
            composicao__mandato=self,
            data_fim_no_cargo=data_final_antiga,
        ).update(data_fim_no_cargo=nova_data)

    def possui_cargo_vacancia_incompativel_com_nova_data_inicial(self, nova_data_inicial: date) -> bool:
        """ True se adiar início do mandato pra `nova_data_inicial` deixaria algum
        cargo ocupado ou vago com data incompatível:
        - um registro que começaria antes da nova data inicial
        - um registro encerrado cuja saída já aconteceu antes da nova data inicial (deixaria inicio > fim)
        Args:
            `nova_data_inicial`: novo valor de `data_inicial` proposta para o mandato

        Returns:
            True se a edição deixaria algum regitro da v2 com intervalo inválido.
        """
        from .cargo_composicao_vacancia import CargoComposicaoVacancia

        comeca_antes_do_novo_inicio = CargoComposicaoVacancia.objects.filter(
            composicao__mandato=self,
            data_inicio_no_cargo__lt=nova_data_inicial,
        ).exclude(data_inicio_no_cargo=self.data_inicial)

        termina_antes_do_novo_inicio = CargoComposicaoVacancia.objects.filter(
            composicao__mandato=self,
            data_fim_no_cargo__lt=nova_data_inicial,
        )

        return comeca_antes_do_novo_inicio.exists() or termina_antes_do_novo_inicio.exists()

    def possui_cargo_vacancia_incompativel_com_nova_data_final(self, nova_data_final: date) -> bool:
        """ True se encolher o mandato pra `nova_data_final` deixaria algum
        cargo com data incompatível:
        - um registro encerrado cuja saída aconteceria depois da nova data final.
        - qualquer registro (mesmo vigente) cuja entrada já aconteceu depois da nova data final.

        Args:
            nova_data_final: data final proposta para o mandato.

        Returns:
            True se a edição deixaria algum registro com intervalo inválido.
        """
        from .cargo_composicao_vacancia import CargoComposicaoVacancia

        termina_depois_do_novo_fim = CargoComposicaoVacancia.objects.filter(
            composicao__mandato=self,
            data_fim_no_cargo__gt=nova_data_final,
        ).exclude(data_fim_no_cargo=self.data_final)

        comeca_depois_do_novo_fim = CargoComposicaoVacancia.objects.filter(
            composicao__mandato=self,
            data_inicio_no_cargo__gt=nova_data_final,
        )

        return termina_depois_do_novo_fim.exists() or comeca_depois_do_novo_fim.exists()


auditlog.register(Mandato)

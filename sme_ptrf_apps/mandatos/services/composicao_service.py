from ..models import Composicao, CargoComposicao
from datetime import date, timedelta, datetime
from django.db.models import Q
from django.core.exceptions import MultipleObjectsReturned


class ServicoComposicaoVigente:

    def __init__(self, associacao, mandato):
        self.__associacao = associacao
        self.__mandato = mandato

    @property
    def associacao(self):
        return self.__associacao

    @property
    def mandato(self):
        return self.__mandato

    def get_composicao_vigente(self):
        data_atual = date.today()

        # Filtrar as composições com data_inicial anterior ou igual à data atual
        qs = Composicao.objects.filter(data_inicial__lte=data_atual)

        # Filtrar as composições com data_final posterior ou igual à data atual OU sem data_final definida
        qs = qs.filter(Q(data_final__gte=data_atual) | Q(data_final__isnull=True))

        # Filtrar as composições da associacao
        qs = qs.filter(associacao=self.associacao)

        # Filtrar as composições do mandato
        qs = qs.filter(mandato=self.mandato)

        # Verificar se há mais de uma composicao vigente, e caso haja, retornar o último (o mais recente)
        composicao_vigente = qs.last()

        return composicao_vigente

    # def get_composicao_anterior(self):
    #     composicao_vigente = self.get_composicao_vigente()
    #
    #     composicao_anterior = Composicao.objects.filter(
    #         associacao=self.associacao,
    #         mandato=self.mandato,
    #         data_final=composicao_vigente.data_inicial - timedelta(days=1)
    #     ).exclude(id=composicao_vigente.id).order_by('-id')
    #
    #     return composicao_anterior.first() if composicao_anterior else None

    def get_composicao_anterior(self, data_inicial=None):
        if data_inicial:
            composicao_anterior = Composicao.objects.filter(
                associacao=self.associacao,
                mandato=self.mandato,
                data_final=data_inicial - timedelta(days=1)
            )
        else:
            composicao_vigente = self.get_composicao_vigente()
            if composicao_vigente:
                composicao_anterior = Composicao.objects.filter(
                    associacao=self.associacao,
                    mandato=self.mandato,
                    data_final=composicao_vigente.data_inicial - timedelta(days=1)
                ).exclude(id=composicao_vigente.id).order_by('-id')
            else:
                composicao_anterior = None

        return composicao_anterior.first() if composicao_anterior else None

    def get_info_composicao_anterior(self):
        composicao_anterior = self.get_composicao_anterior()

        result = {}

        if composicao_anterior:
            result = {
                'id': composicao_anterior.id,
                'uuid': composicao_anterior.uuid,
                'data_inicial': composicao_anterior.data_inicial,
                'data_final': composicao_anterior.data_final,
            }

        return result


class ServicoCriaComposicaoVigenteDoMandato(ServicoComposicaoVigente):

    def __init__(self, associacao, mandato):
        super().__init__(associacao, mandato)

    def cria_composicao_vigente(self):
        composicao = Composicao.objects.create(
            associacao=self.associacao,
            mandato=self.mandato,
            data_inicial=self.mandato.data_inicial,
            data_final=self.mandato.data_final
        )

        return composicao

    def cria_nova_composicao_atraves_de_alteracao_membro(
        self,
        data_fim_no_cargo,
        cargo_composicao_sendo_editado
    ):

        if data_fim_no_cargo != self.mandato.data_final:
            data_fim_no_cargo = datetime.strptime(data_fim_no_cargo, '%Y-%m-%d').date()

            minha_composicao_atual = cargo_composicao_sendo_editado.composicao

            # cargos encerrados na mesma data não devem gerar composições diferentes.
            composicao, created = Composicao.objects.get_or_create(
                associacao=self.associacao,
                mandato=self.mandato,
                data_inicial=data_fim_no_cargo + timedelta(days=1),
                data_final=self.mandato.data_final
            )

            if created:
                minha_composicao_atual.data_final = data_fim_no_cargo
                minha_composicao_atual.save()

            cargos_da_nova_composicao = minha_composicao_atual.cargos_da_composicao_da_composicao.exclude(
                ocupante_do_cargo=cargo_composicao_sendo_editado.ocupante_do_cargo
            )

            cargo_composicao_sendo_editado.set_encerrar_e_substituir(data_fim_no_cargo)

            if created:
                for cargo in cargos_da_nova_composicao:
                    CargoComposicao.objects.create(
                        composicao=composicao,
                        ocupante_do_cargo=cargo.ocupante_do_cargo,
                        cargo_associacao=cargo.cargo_associacao,
                        substituto=cargo.substituto,
                        substituido=cargo.substituido,
                        data_inicio_no_cargo=cargo.data_inicio_no_cargo,
                        data_fim_no_cargo=cargo.data_fim_no_cargo
                    )
                    # a data fim do cargo inicia com a data fim do mandato, porém deve acompanhar a data fim da composição.
                    cargo.data_fim_no_cargo = minha_composicao_atual.data_final
                    cargo.save()
            else:
                # caso a composição exista, então mais de um cargo foi finalizado com a mesma data.
                # sendo assim, o cargo é apenas deletado e o cargo da composição anterior atribuído como substituido.
                composicao.cargos_da_composicao_da_composicao.filter(
                    ocupante_do_cargo=cargo_composicao_sendo_editado.ocupante_do_cargo).delete()

                try:
                    composicao_anterior = Composicao.objects.get(
                        associacao=self.associacao,
                        mandato=self.mandato,
                        data_final=composicao.data_inicial - timedelta(days=1)
                    )
                except Composicao.DoesNotExist:
                    composicao_anterior = None
                except MultipleObjectsReturned:
                    composicao_anterior = Composicao.objects.filter(
                        associacao=self.associacao,
                        mandato=self.mandato,
                        data_final=composicao.data_inicial - timedelta(days=1)
                    ).order_by('-id').first()

                if composicao_anterior:
                    composicao_anterior.cargos_da_composicao_da_composicao.filter(
                        cargo_associacao=cargo_composicao_sendo_editado.cargo_associacao
                    ).update(substituido=True)


class ServicoRecuperaComposicaoPorData:
    @staticmethod
    def get_composicao_por_data_e_associacao(data, associacao_id):
        try:
            composicao = Composicao.objects.get(
                associacao_id=associacao_id,
                data_inicial__lte=data,
                data_final__gte=data
            )
            return composicao
        except Composicao.DoesNotExist:
            return None
        except MultipleObjectsReturned:
            composicao = Composicao.objects.filter(
                associacao_id=associacao_id,
                data_inicial__lte=data,
                data_final__gte=data
            ).order_by('-id').first()
            return composicao

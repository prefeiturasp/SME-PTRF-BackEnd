from . import ServicoComposicaoVigente, ServicoMandatoVigente
from ..models import CargoComposicao, Composicao, OcupanteCargo
import re


class ServicoCargosDaComposicao:
    def __init__(self, composicao=None):
        if composicao:
            self.__composicao = composicao
            self.__choices = CargoComposicao.CARGO_ASSOCIACAO_CHOICES
            self.__cargos_da_composicao = CargoComposicao.objects.filter(composicao=self.composicao)
            self.__cargos_list = {
                "diretoria_executiva": [],
                "conselho_fiscal": []
            }
            self.get_cargos_diretoria_executiva_da_composicao()
            self.get_cargos_conselho_fiscal_da_composicao()

    @property
    def composicao(self):
        return self.__composicao

    @property
    def choices(self):
        return self.__choices

    @property
    def cargos_da_composicao(self):
        return self.__cargos_da_composicao

    @property
    def cargos_list(self):
        return self.__cargos_list

    def retorna_se_composicao_vigente(self):
        mandato = self.composicao.mandato
        associacao = self.composicao.associacao

        if mandato and associacao:
            servico_composicao_vigente = ServicoComposicaoVigente(associacao=associacao, mandato=mandato)
            composicao_vigente = servico_composicao_vigente.get_composicao_vigente()
            if composicao_vigente:
                return composicao_vigente == self.composicao
            else:
                return False
        else:
            return False

    def get_cargos_por_ocupante_e_mandato(self, cargo):
        mandato = self.composicao.mandato
        cargos = CargoComposicao.objects.filter(
            composicao__mandato=mandato,
            ocupante_do_cargo=cargo.ocupante_do_cargo,
        ).order_by('composicao__data_final')
        return cargos

    def get_data_fim_no_cargo_composicao_mais_recente(self, cargo):
        ''' Caso seja uma composição passada, retorna informação de
            data final da composição mais recente do ocupante.'''

        if cargo and not self.retorna_se_composicao_vigente():
            cargos_composicao = self.get_cargos_por_ocupante_e_mandato(cargo)
            if cargos_composicao.exists():
                return cargos_composicao.last().composicao.data_final.strftime("%Y-%m-%d")
        return None

    def monta_cargos(self, cargo, indice, valor):

        obj = {
            "id": cargo.id if cargo else None,
            "uuid": cargo.uuid if cargo else None,
            "ocupante_do_cargo": {
                "id": cargo.ocupante_do_cargo.id if cargo and cargo.ocupante_do_cargo else None,
                "uuid": cargo.ocupante_do_cargo.uuid if cargo and cargo.ocupante_do_cargo else None,
                "nome": cargo.ocupante_do_cargo.nome if cargo and cargo.ocupante_do_cargo else None,
                "codigo_identificacao": cargo.ocupante_do_cargo.codigo_identificacao if cargo and cargo.ocupante_do_cargo else None,
                "cargo_educacao": cargo.ocupante_do_cargo.cargo_educacao if cargo and cargo.ocupante_do_cargo else None,
                "representacao": cargo.ocupante_do_cargo.representacao if cargo and cargo.ocupante_do_cargo else '',
                "representacao_label": cargo.ocupante_do_cargo.get_representacao_display() if cargo and cargo.ocupante_do_cargo else '',
                "email": cargo.ocupante_do_cargo.email if cargo and cargo.ocupante_do_cargo else None,
                "cpf_responsavel": cargo.ocupante_do_cargo.cpf_responsavel if cargo and cargo.ocupante_do_cargo else None,
                "telefone": cargo.ocupante_do_cargo.telefone if cargo and cargo.ocupante_do_cargo else None,
                "cep": cargo.ocupante_do_cargo.cep if cargo and cargo.ocupante_do_cargo else None,
                "bairro": cargo.ocupante_do_cargo.bairro if cargo and cargo.ocupante_do_cargo else None,
                "endereco": cargo.ocupante_do_cargo.endereco if cargo and cargo.ocupante_do_cargo else None
            },
            "cargo_associacao": cargo.cargo_associacao if cargo else indice,
            "cargo_associacao_label": valor.split(" ")[0],
            "data_inicio_no_cargo": cargo.data_inicio_no_cargo if cargo else None,
            "data_fim_no_cargo": cargo.data_fim_no_cargo if cargo else None,
            "data_fim_no_cargo_composicao_mais_recente": self.get_data_fim_no_cargo_composicao_mais_recente(cargo),
            "eh_composicao_vigente": self.retorna_se_composicao_vigente(),
            "substituto": cargo.substituto if cargo else None,
            "tag_substituto": f'Novo membro em {cargo.data_inicio_no_cargo.strftime("%d/%m/%Y")}' if cargo and cargo.substituto else None,
            "substituido": cargo.substituido if cargo else None,
            "tag_substituido": f'Substituído em {self.composicao.data_final.strftime("%d/%m/%Y")}' if cargo and cargo.substituido else None,
            "ocupante_editavel": True if not cargo else False,
            "data_final_editavel": True if cargo else False,
        }

        return obj

    def get_cargos_diretoria_executiva_da_composicao(self):

        for indice, valor in self.choices[:9]:

            cargo = self.cargos_da_composicao.filter(cargo_associacao=indice).first()

            obj = self.monta_cargos(cargo=cargo, indice=indice, valor=valor)

            self.cargos_list['diretoria_executiva'].append(obj)

    def get_cargos_conselho_fiscal_da_composicao(self):

        for indice, valor in self.choices[9:]:

            cargo = self.cargos_da_composicao.filter(cargo_associacao=indice).first()

            obj = self.monta_cargos(cargo=cargo, indice=indice, valor=valor)

            self.cargos_list['conselho_fiscal'].append(obj)

    def get_cargos_da_composicao_ordenado_por_cargo_associacao(self):
        return self.cargos_list

    def membro_substituido(self, cargo_associacao):

        composicao_anterior = Composicao.objects.filter(
            associacao=self.composicao.associacao,
            mandato=self.composicao.mandato
        ).exclude(id=self.composicao.id).order_by('-id')

        membro_substituido = CargoComposicao.objects.filter(
            composicao=composicao_anterior.first(),
            cargo_associacao=cargo_associacao,
            substituido=True
        )

        return membro_substituido.exists()

    def get_presidente_diretoria_executiva_composicao_vigente(self, associacao):
        servico_mandato_vigente = ServicoMandatoVigente()
        mandato_vigente = servico_mandato_vigente.get_mandato_vigente()

        servico_composicao_vigente = ServicoComposicaoVigente(associacao=associacao, mandato=mandato_vigente)
        composicao_vigente = servico_composicao_vigente.get_composicao_vigente()

        if mandato_vigente and composicao_vigente:
            if associacao.cargo_substituto_presidente_ausente:
                cargo_da_composicao_presidente_diretoria_executiva = CargoComposicao.objects.filter(
                    composicao=composicao_vigente,
                    cargo_associacao=associacao.cargo_substituto_presidente_ausente
                ).first()
            else:
                cargo_da_composicao_presidente_diretoria_executiva = CargoComposicao.objects.filter(
                    composicao=composicao_vigente,
                    cargo_associacao='PRESIDENTE_DIRETORIA_EXECUTIVA'
                ).first()

            presidente_diretoria_executiva = cargo_da_composicao_presidente_diretoria_executiva.ocupante_do_cargo.nome if cargo_da_composicao_presidente_diretoria_executiva and cargo_da_composicao_presidente_diretoria_executiva.ocupante_do_cargo and cargo_da_composicao_presidente_diretoria_executiva.ocupante_do_cargo.nome else '-------'

        else:
            print("Não existe nenhum Mandato/Composição vigente criada")
            presidente_diretoria_executiva = "-"

        return presidente_diretoria_executiva


class ServicoCargosDaDiretoriaExecutiva:
    def __init__(self):
        self.__choices = CargoComposicao.CARGO_ASSOCIACAO_CHOICES

    @property
    def choices(self):
        return self.__choices

    def get_cargos_diretoria_executiva(self):
        return [{'id': choice[0], 'nome': choice[1]} for choice in self.choices[:9]]


class ServicoPendenciaCargosDaComposicaoVigenteDaAssociacao:
    def __init__(self, associacao):
        self.__choices = CargoComposicao.CARGO_ASSOCIACAO_CHOICES
        self.__associacao = associacao

    @property
    def choices(self):
        return self.__choices

    @property
    def associacao(self):
        return self.__associacao

    def retorna_se_tem_pendencia(self):
        servico_mandato_vigente = ServicoMandatoVigente()
        mandato_vigente = servico_mandato_vigente.get_mandato_vigente()

        servico_composicao_vigente = ServicoComposicaoVigente(associacao=self.associacao, mandato=mandato_vigente)
        composicao_vigente = servico_composicao_vigente.get_composicao_vigente()

        if mandato_vigente and composicao_vigente:
            cargos_da_composicao = CargoComposicao.objects.filter(composicao=composicao_vigente)
            for indice, valor in self.choices:
                cargo = cargos_da_composicao.filter(cargo_associacao=indice)
                if not cargo.exists():
                    return True

            return False
        else:
            return True


class ServicoCargosOcupantesComposicao:
    def get_ocupantes_ordenados_por_cargo(self, composicao):
        ocupantes = OcupanteCargo.objects.filter(
            cargos_da_composicao_do_ocupante__composicao=composicao
        )

        if not ocupantes:
            # Nao existem ocupantes na composicao
            return []

        temp_diretoria_executiva = {}
        temp_conselho_fiscal = {}

        for ocupante in ocupantes:
            cargo_composicao = CargoComposicao.objects.get(
                composicao=composicao,
                ocupante_do_cargo=ocupante
            )
            cargo_associacao = cargo_composicao.cargo_associacao
            cargo_nome = CargoComposicao.CARGO_ASSOCIACAO_NOMES[cargo_associacao]

            if cargo_associacao in [choice[0] for choice in CargoComposicao.CARGO_ASSOCIACAO_CHOICES[:9]]:
                if cargo_associacao in temp_diretoria_executiva:
                    temp_diretoria_executiva[cargo_associacao].append({
                        'id': ocupante.id,
                        'cargo': cargo_nome,
                        'identificacao': ocupante.codigo_identificacao if ocupante.codigo_identificacao else ocupante.cpf_responsavel,
                        'nome': ocupante.nome,
                    })
                else:
                    temp_diretoria_executiva[cargo_associacao] = [{
                        'id': ocupante.id,
                        'cargo': cargo_nome,
                        'identificacao': ocupante.codigo_identificacao if ocupante.codigo_identificacao else ocupante.cpf_responsavel,
                        'nome': ocupante.nome,
                    }]
            else:
                if cargo_associacao in temp_conselho_fiscal:
                    temp_conselho_fiscal[cargo_associacao].append({
                        'id': ocupante.id,
                        'cargo': cargo_nome,
                        'identificacao': ocupante.codigo_identificacao if ocupante.codigo_identificacao else ocupante.cpf_responsavel,
                        'nome': ocupante.nome,
                    })
                else:
                    temp_conselho_fiscal[cargo_associacao] = [{
                        'id': ocupante.id,
                        'cargo': cargo_nome,
                        'identificacao': ocupante.codigo_identificacao if ocupante.codigo_identificacao else ocupante.cpf_responsavel,
                        'nome': ocupante.nome,
                    }]

        diretoria_executiva = []
        conselho_fiscal = []

        for choice in CargoComposicao.CARGO_ASSOCIACAO_CHOICES[:9]:
            cargo_associacao = choice[0]
            if cargo_associacao in temp_diretoria_executiva:
                diretoria_executiva.extend(temp_diretoria_executiva[cargo_associacao])

        for choice in CargoComposicao.CARGO_ASSOCIACAO_CHOICES[9:]:
            cargo_associacao = choice[0]
            if cargo_associacao in temp_conselho_fiscal:
                conselho_fiscal.extend(temp_conselho_fiscal[cargo_associacao])

        objeto = {
            'diretoria_executiva': diretoria_executiva,
            'conselho_fiscal': conselho_fiscal
        }

        return objeto

from ..models import CargoComposicao

class ServicoCargosDaComposicao:
    def __init__(self, composicao):
        self.__composicao = composicao
        self.__choices = CargoComposicao.CARGO_ASSOCIACAO_CHOICES
        self.__cargos_da_composicao = CargoComposicao.objects.filter(composicao=self.composicao)
        self.__cargos_list = {
            "diretoria_executiva": [],
            "conselho_fiscal": []
        }
        self.get_cargos_diretoria_executiva()
        self.get_cargos_conselho_fiscal()

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

    def get_cargos_diretoria_executiva(self):

        for indice, valor in self.choices[:9]:

            cargo = self.cargos_da_composicao.filter(cargo_associacao=indice).first()

            obj = {
                "id": cargo.id if cargo else None,
                "uuid": cargo.uuid if cargo else None,
                "ocupante_do_cargo": {
                    "id": cargo.ocupante_do_cargo.id if cargo else None,
                    "uuid": cargo.ocupante_do_cargo.uuid if cargo else None,
                    "nome": cargo.ocupante_do_cargo.nome if cargo else None,
                    "codigo_identificacao": cargo.ocupante_do_cargo.codigo_identificacao if cargo else None,
                    "cargo_educacao": cargo.ocupante_do_cargo.cargo_educacao if cargo else None,
                    "representacao": cargo.ocupante_do_cargo.representacao if cargo else '',
                    "representacao_label": cargo.ocupante_do_cargo.get_representacao_display() if cargo else '',
                    "email": cargo.ocupante_do_cargo.email if cargo else None,
                    "cpf_responsavel": cargo.ocupante_do_cargo.cpf_responsavel if cargo else None,
                    "telefone": cargo.ocupante_do_cargo.telefone if cargo else None,
                    "cep": cargo.ocupante_do_cargo.cep if cargo else None,
                    "bairro": cargo.ocupante_do_cargo.bairro if cargo else None,
                    "endereco": cargo.ocupante_do_cargo.endereco if cargo else None
                },
                "cargo_associacao": cargo.cargo_associacao if cargo else indice,
                "cargo_associacao_label": valor.split(" ")[0],
                "substituto": cargo.substituto if cargo else None,
                "substituido": cargo.substituido if cargo else None
            }

            self.cargos_list['diretoria_executiva'].append(obj)

    def get_cargos_conselho_fiscal(self):

        for indice, valor in self.choices[9:]:

            cargo = self.cargos_da_composicao.filter(cargo_associacao=indice).first()

            obj = {
                "id": cargo.id if cargo else None,
                "uuid": cargo.uuid if cargo else None,
                "ocupante_do_cargo": {
                    "id": cargo.ocupante_do_cargo.id if cargo else None,
                    "uuid": cargo.ocupante_do_cargo.uuid if cargo else None,
                    "nome": cargo.ocupante_do_cargo.nome if cargo else None,
                    "codigo_identificacao": cargo.ocupante_do_cargo.codigo_identificacao if cargo else None,
                    "cargo_educacao": cargo.ocupante_do_cargo.cargo_educacao if cargo else None,
                    "representacao": cargo.ocupante_do_cargo.representacao if cargo else '',
                    "representacao_label": cargo.ocupante_do_cargo.get_representacao_display() if cargo else '',
                    "email": cargo.ocupante_do_cargo.email if cargo else None,
                    "cpf_responsavel": cargo.ocupante_do_cargo.cpf_responsavel if cargo else None,
                    "telefone": cargo.ocupante_do_cargo.telefone if cargo else None,
                    "cep": cargo.ocupante_do_cargo.cep if cargo else None,
                    "bairro": cargo.ocupante_do_cargo.bairro if cargo else None,
                    "endereco": cargo.ocupante_do_cargo.endereco if cargo else None
                },
                "cargo_associacao": cargo.cargo_associacao if cargo else indice,
                "cargo_associacao_label": valor.split(" ")[0],
                "substituto": cargo.substituto if cargo else None,
                "substituido": cargo.substituido if cargo else None
            }

            self.cargos_list['conselho_fiscal'].append(obj)


    def get_cargos_da_composicao_ordenado_por_cargo_associacao(self):
        return self.cargos_list



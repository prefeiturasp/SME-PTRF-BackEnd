from sme_ptrf_apps.core.models import MembroAssociacao, Unidade
from brazilnum.cpf import format_cpf
from django.contrib.auth import get_user_model
from sme_ptrf_apps.users.services import (
    SmeIntegracaoService,
)

User = get_user_model()


class GestaoUsuarioService:

    def __init__(self, usuario):
        self.usuario = usuario

    def unidades_do_usuario(self, unidade_base, visao_base):
        if self.usuario.e_servidor:
            result = self.retorna_lista_unidades_servidor(unidade_base=unidade_base, visao_base=visao_base)
        else:
            result = self.retorna_lista_unidades_nao_servidor(unidade_base=unidade_base, visao_base=visao_base)

        return result

    def usuario_possui_acesso_a_unidade(self, unidade):
        usuario = User.objects.get(username=self.usuario.username)
        return usuario.unidades.filter(codigo_eol=unidade.codigo_eol).exists()

    def servidor_membro_associacao_na_unidade(self, unidade):
        return MembroAssociacao.objects.filter(
            codigo_identificacao=self.usuario.username, associacao__unidade=unidade).exists()

    def get_info_unidade(self):
        info = SmeIntegracaoService.get_info_lotacao_e_exercicio_do_servidor(self.usuario.username)
        unidade_encontrada = None

        if "unidadeExercicio" in info and info['unidadeExercicio'] is not None:
            unidade_encontrada = info['unidadeExercicio']

        elif "unidadeLotacao" in info and info['unidadeLotacao'] is not None:
            unidade_encontrada = info['unidadeLotacao']

        return unidade_encontrada

    def retorna_lista_unidades_nao_servidor(self, unidade_base, visao_base):
        lista = []
        membro_associacoes = MembroAssociacao.objects.filter(cpf=format_cpf(self.usuario.username)).all()
        unidades = []

        if visao_base == 'SME':
            unidades = Unidade.objects.values_list("codigo_eol", flat=True)
        elif visao_base == 'DRE':
            unidades = unidade_base.unidades_da_dre.values_list("codigo_eol", flat=True)

        for membro in membro_associacoes.filter(associacao__unidade__codigo_eol__in=unidades).all():
            lista.append({
                'uuid_unidade': f'{membro.associacao.unidade.uuid}',
                'nome_com_tipo': f'{membro.associacao.unidade.tipo_unidade} {membro.associacao.unidade.nome}',
                'membro': True,
                'tem_acesso': self.usuario_possui_acesso_a_unidade(membro.associacao.unidade),
                'username': self.usuario.username
            })

        lista_ordenada = sorted(lista, key=lambda row: (row['tem_acesso'] is False, row['nome_com_tipo']))
        return lista_ordenada

    def retorna_lista_unidades_servidor(self, unidade_base, visao_base):
        lista = []
        unidade_encontrada_na_api = self.get_info_unidade()

        unidade_encontrada_na_base = None

        if unidade_encontrada_na_api:
            unidade_encontrada_na_base = Unidade.objects.filter(codigo_eol=unidade_encontrada_na_api['codigo']).first()

        unidades = []
        if visao_base == 'SME':
            unidades = Unidade.objects.values_list("codigo_eol", flat=True)
        elif visao_base == 'DRE':
            unidades = unidade_base.unidades_da_dre.values_list("codigo_eol", flat=True)

        if unidade_encontrada_na_base and unidade_encontrada_na_base.codigo_eol in unidades:
            lista.append({
                'uuid_unidade': f'{unidade_encontrada_na_base.uuid}',
                'nome_com_tipo': f'{unidade_encontrada_na_base.tipo_unidade} {unidade_encontrada_na_base.nome}',
                'membro': self.servidor_membro_associacao_na_unidade(unidade_encontrada_na_base),
                'tem_acesso': self.usuario_possui_acesso_a_unidade(unidade_encontrada_na_base),
                'username': self.usuario.username,
                'unidade_em_exercicio': True
            })

        membro_associacoes = MembroAssociacao.objects.filter(codigo_identificacao=self.usuario.username).all()
        for membro in membro_associacoes.filter(associacao__unidade__codigo_eol__in=unidades).all():

            if unidade_encontrada_na_base == membro.associacao.unidade:
                # Esta unidade ja foi adicionada a lista no bloco acima
                continue

            lista.append({
                'uuid_unidade': f'{membro.associacao.unidade.uuid}',
                'nome_com_tipo': f'{membro.associacao.unidade.tipo_unidade} {membro.associacao.unidade.nome}',
                'membro': True,
                'tem_acesso': self.usuario_possui_acesso_a_unidade(membro.associacao.unidade),
                'username': self.usuario.username,
                'unidade_em_exercicio': False
            })

        lista_ordenada = sorted(lista, key=lambda row: (row['tem_acesso'] is False, row['nome_com_tipo']))
        return lista_ordenada

    def habilitar_acesso(self, unidade):
        self.usuario.add_unidade_se_nao_existir(codigo_eol=unidade.codigo_eol)

        visao_da_unidade = 'DRE' if unidade.tipo_unidade == 'DRE' else 'UE'
        self.usuario.add_visao_se_nao_existir(visao=visao_da_unidade)

        response = {
            "mensagem": "Acesso ativado para unidade selecionada"
        }

        return response

    def desabilitar_acesso(self, unidade):
        self.usuario.remove_unidade_se_existir(codigo_eol=unidade.codigo_eol)

        visao_da_unidade = 'DRE' if unidade.tipo_unidade == 'DRE' else 'UE'
        if not self.usuario.possui_unidades_da_visao(visao_da_unidade):
            self.usuario.remove_visao_se_existir(visao_da_unidade)

        response = {
            "mensagem": "Acesso desativado para unidade selecionada",
        }

        return response

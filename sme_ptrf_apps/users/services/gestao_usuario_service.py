from sme_ptrf_apps.core.models import MembroAssociacao, Unidade
from sme_ptrf_apps.users.models import AcessoConcedidoSme, UnidadeEmSuporte
from sme_ptrf_apps.sme.models import ParametrosSme
from brazilnum.cpf import format_cpf
from django.contrib.auth import get_user_model
from sme_ptrf_apps.users.services import (
    SmeIntegracaoService,
    SmeIntegracaoException
)
from django.db.models import Q

User = get_user_model()


class GestaoUsuarioService:

    def __init__(self, usuario):
        self.usuario = usuario

    def unidades_do_usuario(self, unidade_base="SME", visao_base="SME", inclui_unidades_suporte=False):
        if self.usuario.e_servidor:
            result = self.retorna_lista_unidades_servidor(
                unidade_base=unidade_base,
                visao_base=visao_base,
                inclui_unidades_suporte=inclui_unidades_suporte
            )
        else:
            result = self.retorna_lista_unidades_nao_servidor(
                unidade_base=unidade_base,
                visao_base=visao_base,
                inclui_unidades_suporte=inclui_unidades_suporte
            )

        return result

    def usuario_possui_acesso_a_unidade(self, unidade):
        usuario = User.objects.get(username=self.usuario.username)
        return usuario.unidades.filter(codigo_eol=unidade.codigo_eol).exists()

    def usuario_possui_visao(self, visao):
        usuario = User.objects.get(username=self.usuario.username)
        return usuario.visoes.filter(nome=visao).exists()

    def servidor_membro_associacao_na_unidade(self, unidade):
        return MembroAssociacao.objects.filter(
            codigo_identificacao=self.usuario.username, associacao__unidade=unidade).exists()

    def usuario_membro_associacao_na_unidade(self, unidade):
        if not self.usuario.e_servidor:
            return MembroAssociacao.objects.filter(
                cpf=format_cpf(self.usuario.username), associacao__unidade=unidade).exists()
        else:
            return MembroAssociacao.objects.filter(
                codigo_identificacao=self.usuario.username, associacao__unidade=unidade).exists()

    def get_info_unidade(self):
        try:
            info = SmeIntegracaoService.get_info_lotacao_e_exercicio_do_servidor(self.usuario.username)
        except SmeIntegracaoException:
            info = None

        unidade_encontrada = None

        if info:
            if "unidadeExercicio" in info and info['unidadeExercicio'] is not None:
                unidade_encontrada = info['unidadeExercicio']

            elif "unidadeLotacao" in info and info['unidadeLotacao'] is not None:
                unidade_encontrada = info['unidadeLotacao']

        return unidade_encontrada

    @staticmethod
    def permite_tipo_unidade_administrativa(codigo_eol):
        resultado = SmeIntegracaoService.get_dados_unidade_eol(codigo_eol, retorna_json=True)

        if resultado and "tipoUnidadeAdm" in resultado:
            if str(resultado["tipoUnidadeAdm"]) in ParametrosSme.get().tipos_unidade_adm_da_sme:
                return True

        return False

    def retorna_lista_unidades_nao_servidor(self, unidade_base, visao_base, inclui_unidades_suporte=False):
        lista = []
        membro_associacoes = MembroAssociacao.objects.filter(cpf=format_cpf(self.usuario.username)).all()
        acessos_concedidos_pela_sme = AcessoConcedidoSme.objects.filter(user=self.usuario).all()
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
                'username': self.usuario.username,
                'acesso_concedido_sme': False,
                'tipo_unidade': membro.associacao.unidade.tipo_unidade
            })

        for acesso in acessos_concedidos_pela_sme.filter(unidade__codigo_eol__in=unidades).all():
            lista.append({
                'uuid_unidade': f'{acesso.unidade.uuid}',
                'nome_com_tipo': f'{acesso.unidade.tipo_unidade} {acesso.unidade.nome}',
                'membro': self.usuario_membro_associacao_na_unidade(acesso.unidade),
                'tem_acesso': self.usuario_possui_acesso_a_unidade(acesso.unidade),
                'username': self.usuario.username,
                'acesso_concedido_sme': True,
                'tipo_unidade': acesso.unidade.tipo_unidade
            })

        if inclui_unidades_suporte:
            unidades_em_suporte = UnidadeEmSuporte.objects.filter(user=self.usuario).all()

            for unidade_suporte in unidades_em_suporte:
                lista.append({
                    'uuid_unidade': f'{unidade_suporte.unidade.uuid}',
                    'nome_com_tipo': f'{unidade_suporte.unidade.tipo_unidade} {unidade_suporte.unidade.nome}',
                    'membro': self.usuario_membro_associacao_na_unidade(unidade_suporte.unidade),
                    'tem_acesso': True,
                    'username': self.usuario.username,
                    'acesso_concedido_sme': False
                })

        lista_ordenada = sorted(lista, key=lambda row: (row['tem_acesso'] is False, row['nome_com_tipo']))

        if self.usuario.pode_acessar_sme and visao_base == 'SME':
            dados = {
                'uuid_unidade': f'SME',
                'nome_com_tipo': f'SME Secretaria Municipal de Educação',
                'membro': False,
                'tem_acesso': self.usuario_possui_visao("SME"),
                'username': self.usuario.username,
                'unidade_em_exercicio': False,
                'acesso_concedido_sme': False,
                'tipo_unidade': 'SME'
            }

            lista_ordenada.insert(0, dados)

        return lista_ordenada

    def retorna_lista_unidades_servidor(self, unidade_base, visao_base, inclui_unidades_suporte=False):
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
                'membro': self.usuario_membro_associacao_na_unidade(unidade_encontrada_na_base),
                'tem_acesso': self.usuario_possui_acesso_a_unidade(unidade_encontrada_na_base),
                'username': self.usuario.username,
                'unidade_em_exercicio': True,
                'acesso_concedido_sme': False,
                'tipo_unidade': unidade_encontrada_na_base.tipo_unidade
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
                'unidade_em_exercicio': False,
                'acesso_concedido_sme': False,
                'tipo_unidade': membro.associacao.unidade.tipo_unidade
            })

        acessos_concedidos_pela_sme = AcessoConcedidoSme.objects.filter(user=self.usuario).all()
        for acesso in acessos_concedidos_pela_sme.filter(unidade__codigo_eol__in=unidades).all():
            lista.append({
                'uuid_unidade': f'{acesso.unidade.uuid}',
                'nome_com_tipo': f'{acesso.unidade.tipo_unidade} {acesso.unidade.nome}',
                'membro': self.usuario_membro_associacao_na_unidade(acesso.unidade),
                'tem_acesso': self.usuario_possui_acesso_a_unidade(acesso.unidade),
                'username': self.usuario.username,
                'unidade_em_exercicio': False,
                'acesso_concedido_sme': True,
                'tipo_unidade': acesso.unidade.tipo_unidade
            })

        if inclui_unidades_suporte:
            unidades_em_suporte = UnidadeEmSuporte.objects.filter(user=self.usuario).all()

            for unidade_suporte in unidades_em_suporte:
                lista.append({
                    'uuid_unidade': f'{unidade_suporte.unidade.uuid}',
                    'nome_com_tipo': f'{unidade_suporte.unidade.tipo_unidade} {unidade_suporte.unidade.nome}',
                    'membro': self.usuario_membro_associacao_na_unidade(unidade_suporte.unidade),
                    'tem_acesso': True,
                    'username': self.usuario.username,
                    'acesso_concedido_sme': False
                })

        lista_ordenada = sorted(lista, key=lambda row: (row['tem_acesso'] is False, row['nome_com_tipo']))

        if unidade_encontrada_na_api and visao_base == 'SME':

            permite_administrativa = self.permite_tipo_unidade_administrativa(unidade_encontrada_na_api['codigo'])

            if permite_administrativa or self.usuario.pode_acessar_sme:
                dados = {
                    'uuid_unidade': f'SME',
                    'nome_com_tipo': f'SME Secretaria Municipal de Educação',
                    'membro': False,
                    'tem_acesso': self.usuario_possui_visao("SME"),
                    'username': self.usuario.username,
                    'unidade_em_exercicio': False,
                    'acesso_concedido_sme': False,
                    'tipo_unidade': 'SME'
                }

                lista_ordenada.insert(0, dados)

        return lista_ordenada

    def habilitar_acesso(self, unidade):

        if unidade == 'SME':
            self.usuario.add_visao_se_nao_existir(visao=unidade)
        else:
            self.usuario.add_unidade_se_nao_existir(codigo_eol=unidade.codigo_eol)

            visao_da_unidade = 'DRE' if unidade.tipo_unidade == 'DRE' else 'UE'
            self.usuario.add_visao_se_nao_existir(visao=visao_da_unidade)

        response = {
            "mensagem": "Acesso ativado para unidade selecionada"
        }

        return response

    def desabilitar_acesso(self, unidade, acesso_concedido_sme=False):
        if unidade == 'SME':
            self.usuario.remove_visao_se_existir(visao=unidade)
        else:
            self.usuario.remove_unidade_se_existir(codigo_eol=unidade.codigo_eol)

            visao_da_unidade = 'DRE' if unidade.tipo_unidade == 'DRE' else 'UE'
            if not self.usuario.possui_unidades_da_visao(visao_da_unidade):
                self.usuario.remove_visao_se_existir(visao_da_unidade)

            if acesso_concedido_sme:
                AcessoConcedidoSme.remover_acesso_se_existir(unidade=unidade, user=self.usuario)

        response = {
            "mensagem": "Acesso desativado para unidade selecionada",
        }

        return response

    def remover_grupos_acesso_apos_remocao_acesso_unidade(self, unidade, visao_base):
        lista_tipos_unidades_usuario_tem_acesso = list(self.tipos_unidades_usuario_tem_acesso(unidade_base=unidade, visao_base=visao_base))

        if unidade == "SME":
            self.usuario.desabilita_todos_grupos_acesso("SME")
        elif unidade.tipo_unidade == "DRE" and "DRE" not in lista_tipos_unidades_usuario_tem_acesso:
            self.usuario.desabilita_todos_grupos_acesso("DRE")
        elif not lista_tipos_unidades_usuario_tem_acesso or set(lista_tipos_unidades_usuario_tem_acesso) in [{"DRE"}, {"SME"}, {"SME", "DRE"}, {"DRE", "SME"}]:
            self.usuario.desabilita_todos_grupos_acesso("UE")

        return

    def unidades_disponiveis_para_inclusao(self, search):
        unidades_do_usuario = self.unidades_do_usuario('SME', 'SME')
        uuids_unidades_do_usuarios = [u['uuid_unidade'] for u in unidades_do_usuario if u["uuid_unidade"] != 'SME']
        query = Unidade.objects.exclude(uuid__in=uuids_unidades_do_usuarios)

        if search is not None:
            query = query.filter(Q(codigo_eol=search) | Q(nome__unaccent__icontains=search))

        return query.order_by("tipo_unidade", "nome")

    def incluir_unidade(self, unidade):
        self.usuario.add_unidade_se_nao_existir(codigo_eol=unidade.codigo_eol)
        visao_da_unidade = 'DRE' if unidade.tipo_unidade == 'DRE' else 'UE'
        self.usuario.add_visao_se_nao_existir(visao=visao_da_unidade)

        novo_acesso = AcessoConcedidoSme.criar_acesso_se_nao_existir(unidade=unidade, user=self.usuario)
        mensagem = "Unidade adicionada salva com sucesso." if novo_acesso else None

        return mensagem

    def tipos_unidades_usuario_tem_acesso(self, unidade_base="SME", visao_base="SME"):
        from sme_ptrf_apps.core.choices.tipos_unidade import TIPOS_CHOICE

        unidades_usuario = self.unidades_do_usuario(unidade_base, visao_base)
        tipos_unidades_usuario_tem_acesso = set()

        for unidade in unidades_usuario:
            if unidade['tipo_unidade'] == "DRE" and unidade['tem_acesso']:
                tipos_unidades_usuario_tem_acesso.add("DRE")
            elif unidade['tipo_unidade'] == "SME" and unidade['tem_acesso']:
                tipos_unidades_usuario_tem_acesso.add("SME")
            else:
                for tipo in TIPOS_CHOICE:
                    if unidade['tipo_unidade'] == tipo[0] and unidade['tem_acesso']:
                        tipos_unidades_usuario_tem_acesso.add("UE")
                        break

        return tipos_unidades_usuario_tem_acesso

from sme_ptrf_apps.core.models import Associacao, Notificacao, Unidade
from sme_ptrf_apps.users.models import UnidadeEmSuporte
from sme_ptrf_apps.dre.models import TecnicoDre
from sme_ptrf_apps.sme.models import ParametrosSme
import logging

from waffle import get_waffle_flag_model

logger = logging.getLogger(__name__)


class LoginUsuarioService:

    def __init__(self, usuario, gestao_usuario, suporte=False):
        self.usuario = usuario
        self.gestao_usuario = gestao_usuario

        self.unidades_que_usuario_pode_ter_acesso = gestao_usuario.unidades_do_usuario(inclui_unidades_suporte=True)
        self.unidades_que_usuario_tem_acesso = self.get_unidades_que_usuario_tem_acesso(suporte=suporte)
        self.unidades_que_perdeu_acesso = gestao_usuario.valida_unidades_do_usuario()
        self.mensagem_perca_acesso = self.get_mensagem_perca_acesso()

    def get_unidades_que_usuario_tem_acesso(self, suporte):
        flags = get_waffle_flag_model()

        novo_suporte_unidade = flags.objects.filter(name='novo-suporte-unidades', everyone=True).exists()

        unidades_que_tem_acesso = []
        for u in self.unidades_que_usuario_pode_ter_acesso:
            if u["tem_acesso"]:
                unidades_que_tem_acesso.append(u)

        tem_acesso_sme = False
        UUID_SME = "8919f454-bee5-419c-ad54-b2df27bf8007"
        info_sme = {
            'uuid': UUID_SME,
            'nome': 'Secretaria Municipal de Educação',
            'tipo_unidade': 'SME',
            'associacao': {
                'uuid': '',
                'nome': ''
            },
            'notificar_devolucao_referencia': None,
            'notificar_devolucao_pc_uuid': None,
            'notificacao_uuid': None,
            'acesso_de_suporte': False
        }

        info_unidades = []
        for unidade_com_acesso in unidades_que_tem_acesso:
            if unidade_com_acesso["uuid_unidade"] == "SME":
                tem_acesso_sme = True
            else:
                unidade = Unidade.by_uuid(unidade_com_acesso["uuid_unidade"])

                associacao = Associacao.objects.filter(unidade__uuid=unidade.uuid).first()

                acesso_de_suporte = UnidadeEmSuporte.objects.filter(unidade=unidade, user=self.usuario).exists()

                notificao_devolucao_pc = Notificacao.objects.filter(
                    usuario=self.usuario,
                    categoria=Notificacao.CATEGORIA_NOTIFICACAO_DEVOLUCAO_PC,
                    unidade=unidade,
                    lido=False
                ).first()

                if notificao_devolucao_pc and notificao_devolucao_pc.prestacao_conta:
                    notificar_devolucao_referencia = notificao_devolucao_pc.prestacao_conta.periodo.referencia
                    notificar_devolucao_pc_uuid = notificao_devolucao_pc.prestacao_conta.uuid
                    notificacao_uuid = notificao_devolucao_pc.uuid
                else:
                    notificar_devolucao_referencia = None
                    notificacao_uuid = None
                    notificar_devolucao_pc_uuid = None

                if novo_suporte_unidade:
                    if suporte and acesso_de_suporte or not suporte and not acesso_de_suporte:
                        info_unidades.append({
                            'uuid': unidade.uuid,
                            'nome': unidade.nome,
                            'tipo_unidade': unidade.tipo_unidade,
                            'associacao': {
                                'uuid': associacao.uuid if associacao else '',
                                'nome': associacao.nome if associacao else ''
                            },
                            'notificar_devolucao_referencia': notificar_devolucao_referencia,
                            'notificar_devolucao_pc_uuid': notificar_devolucao_pc_uuid,
                            'notificacao_uuid': notificacao_uuid,
                            'acesso_de_suporte': acesso_de_suporte
                        })
                else:
                    info_unidades.append({
                        'uuid': unidade.uuid,
                        'nome': unidade.nome,
                        'tipo_unidade': unidade.tipo_unidade,
                        'associacao': {
                            'uuid': associacao.uuid if associacao else '',
                            'nome': associacao.nome if associacao else ''
                        },
                        'notificar_devolucao_referencia': notificar_devolucao_referencia,
                        'notificar_devolucao_pc_uuid': notificar_devolucao_pc_uuid,
                        'notificacao_uuid': notificacao_uuid,
                        'acesso_de_suporte': acesso_de_suporte
                    })

        if novo_suporte_unidade:
            if tem_acesso_sme and not suporte:
                info_unidades.append(info_sme)
        else:
            if tem_acesso_sme:
                info_unidades.append(info_sme)

        return info_unidades


    def get_mensagem_perca_acesso(self):
        if self.unidades_que_perdeu_acesso:
            mensagem = "Favor entrar em contato com a DRE."

            if self.usuario.e_servidor:
                tecnico_dre = TecnicoDre.objects.filter(rf=self.usuario.username)

                if tecnico_dre.exists():
                    mensagem = "Favor entrar em contato com a SME."

            return mensagem

        return None

    def get_exibe_modal(self):
        if self.unidades_que_perdeu_acesso and self.mensagem_perca_acesso:
            return True

        return False

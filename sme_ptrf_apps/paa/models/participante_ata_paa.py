"""
Módulo de modelos do PAA (Plano Anual de Ação).

Este módulo define a entidade responsável por representar os
participantes da ata do PAA e seus atributos de negócio.
"""
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class ParticipanteAtaPaa(ModeloBase):
    """
    Representa um participante da ata do PAA (Plano Anual de Ação).

    Essa model armazena informações sobre os participantes presentes na ata do PAA,
    incluindo identificação, nome, cargo, status de membro, participação no conselho
    fiscal e presença na reunião.
    """
    history = AuditlogHistoryField()

    ata_paa = models.ForeignKey('AtaPaa', on_delete=models.CASCADE, related_name='presentes_na_ata_paa')
    identificacao = models.CharField('Identificacão do presente (RF,CPF ou EOL)', max_length=20, blank=True, default='')
    nome = models.CharField('Nome', max_length=200, blank=True, default='')
    cargo = models.CharField('Cargo', max_length=200, blank=True, default='')
    membro = models.BooleanField('Membro ?', default=False)
    conselho_fiscal = models.BooleanField('Pertence ao conselho fiscal ?', default=False)
    presente = models.BooleanField('Presente ?', default=True)
    professor_gremio = models.BooleanField('Professor do grêmio ?', default=False)

    def eh_conselho_fiscal(self) -> None:
        """Verifica se o participante pertence ao conselho fiscal com base
        no cargo e atualiza o campo `conselho_fiscal` da instância."""

        cargo = (self.cargo or "").lower()

        if "presidente do conselho fiscal" in cargo or "conselheiro" in cargo:
            self.conselho_fiscal = True
            self.save()

    @property
    def editavel(self) -> bool:
        return False

    @classmethod
    def get_informacao_servidor(cls, identificador) -> dict:
        """Retorna informações do servidor com base no identificador fornecido."""
        from sme_ptrf_apps.core.services import TerceirizadasException, TerceirizadasService, SmeIntegracaoApiException
        from requests import ConnectTimeout, ReadTimeout

        try:
            if identificador:
                if len(identificador) == 7:
                    servidor = TerceirizadasService.get_informacao_servidor(identificador)
                    if servidor:
                        result = {
                            "mensagem": "buscando-servidor-nao-membro",
                            "nome": servidor[0]["nm_pessoa"],
                            "cargo": servidor[0]["cargo"]
                        }

                        return result
        except SmeIntegracaoApiException as e:
            print({'detail': str(e)})
        except TerceirizadasException as e:
            print({'detail': str(e)})
        except ReadTimeout:
            print({'detail': 'EOL Timeout'})
        except ConnectTimeout:
            print({'detail': 'EOL Timeout'})

        result = {
            "mensagem": "servidor-nao-encontrado",
            "nome": "",
            "cargo": ""
        }

        return result

    @staticmethod
    def ordenar_por_cargo(participante) -> int:
        """Retorna um valor inteiro para ordenar os participantes pelo cargo."""
        cargos = {
            'Presidente da diretoria executiva': 1,
            'Presidente da Diretoria Executiva': 1,
            'Vice-Presidente da diretoria executiva': 2,            
            'Vice-Presidente da Diretoria Executiva': 2,
            'Secretário': 3,
            'Tesoureiro': 4,
            'Vogal': 5,
            'Presidente do conselho fiscal': 6,
            'Presidente do Conselho Fiscal': 6,
            'Conselheiro': 7,
        }
        return cargos.get(participante['cargo'], 8)  # 8 para cargos não listados

    @classmethod
    def participantes_ordenados_por_cargo(cls, ata_paa, membro) -> list:
        """Retorna os participantes da ata do PAA ordenados pelo cargo."""
        presentes_ata_membros = cls.objects.filter(ata_paa=ata_paa, membro=membro).values()

        presentes_ata_membros_ordenados = sorted(presentes_ata_membros, key=cls.ordenar_por_cargo)
        return presentes_ata_membros_ordenados

    class Meta:
        verbose_name = "Participantes ata PAA"
        verbose_name_plural = "Participantes ata PAA"


auditlog.register(ParticipanteAtaPaa)

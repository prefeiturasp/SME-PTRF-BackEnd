from sme_ptrf_apps.core.models_abstracts import ModeloBase
from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

class ParticipanteAtaPaa(ModeloBase):
    history = AuditlogHistoryField()

    ata_paa = models.ForeignKey('AtaPaa', on_delete=models.CASCADE, related_name='presentes_na_ata_paa')
    identificacao = models.CharField('Identificacão do presente (RF,CPF ou EOL)', max_length=20, blank=True, default='')
    nome = models.CharField('Nome', max_length=200, blank=True, default='')
    cargo = models.CharField('Cargo', max_length=200, blank=True, default='')
    membro = models.BooleanField('Membro ?', default=False)
    conselho_fiscal = models.BooleanField('Pertence ao conselho fiscal ?', default=False)
    presente = models.BooleanField('Presente ?', default=True)
    professor_gremio = models.BooleanField('Professor do grêmio ?', default=False)
    
    def eh_conselho_fiscal(self):
        if "Presidente do conselho fiscal" in self.cargo or "Conselheiro" in self.cargo:
            self.conselho_fiscal = True
            self.save()

    @property
    def editavel(self):
        return False

    @classmethod
    def get_informacao_servidor(cls, identificador):
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
    def ordenar_por_cargo(participante):
        cargos = {
            'Presidente da diretoria executiva': 1,
            'Vice-Presidente da diretoria executiva': 2,
            'Secretário': 3,
            'Tesoureiro': 4,
            'Vogal': 5,
            'Presidente do conselho fiscal': 6,
            'Conselheiro': 7,
        }
        return cargos.get(participante['cargo'], 8)  # 8 para cargos não listados
    
    @classmethod
    def participantes_ordenados_por_cargo(cls, ata_paa, membro):
        presentes_ata_membros = cls.objects.filter(ata_paa=ata_paa, membro=membro).values()
        
        presentes_ata_membros_ordenados = sorted(presentes_ata_membros, key=cls.ordenar_por_cargo)
        return presentes_ata_membros_ordenados

    class Meta:
        verbose_name = "Participantes ata PAA"
        verbose_name_plural = "Participantes ata PAA"


auditlog.register(ParticipanteAtaPaa)
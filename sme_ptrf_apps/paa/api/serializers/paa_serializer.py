from datetime import date
from django.db import transaction
from django.db import IntegrityError
from rest_framework import serializers
from sme_ptrf_apps.paa.models import Paa, PeriodoPaa, ObjetivoPaa, AtividadeEstatutaria, AtividadeEstatutariaPaa
from sme_ptrf_apps.core.api.serializers.unidade_serializer import UnidadeSimplesSerializer
from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.paa.api.serializers.objetivo_paa_serializer import ObjetivoPaaSerializer, ObjetivoPaaUpdateSerializer
from sme_ptrf_apps.paa.api.serializers.atividade_estatutaria_paa_serializer import (
    AtividadeEstatutariaPaaSerializer,
    AtividadeEstaturariaPaaUpdateSerializer
)
from sme_ptrf_apps.paa.api.serializers.ata_paa_serializer import AtaPaaSerializer
from sme_ptrf_apps.paa.api.serializers import PeriodoPaaSerializer, PeriodoPaaSimplesSerializer
from sme_ptrf_apps.paa.services.ciclo_retificacao_service import CicloRetificacaoService


class PaaSerializer(serializers.ModelSerializer):
    """
    Serializer responsável por validar, criar e serializar
    os dados de um PAA.

    Além dos campos do modelo, expõe campos calculados para apresentação.
    """
    associacao = serializers.SlugRelatedField(queryset=Associacao.objects.all(), slug_field='uuid')
    periodo_paa_objeto = PeriodoPaaSerializer(read_only=True, many=False)
    objetivos = ObjetivoPaaSerializer(many=True, read_only=True)
    total_recursos_proprios = serializers.SerializerMethodField()
    tem_documento_final_concluido = serializers.SerializerMethodField()
    tem_ata_concluida = serializers.SerializerMethodField()
    status_andamento = serializers.SerializerMethodField()

    def get_status_andamento(self, obj: Paa) -> str:
        """
        Retorna o status de andamento do PAA.

        Args:
            obj (Paa): Instância do Plano de Ação e Acompanhamento.

        Returns:
            str: Status de andamento do PAA.
        """
        return obj.get_status_andamento()

    def get_tem_documento_final_concluido(self, obj: Paa) -> bool:
        """
        Informa se o documento final do PAA foi concluído.

        Quando o PAA está em retificação, a informação é obtida por meio do
        ciclo de retificação. Caso contrário, utiliza o método da própria
        instância do PAA.

        Args:
            obj (Paa): Instância do Plano de Ação e Acompanhamento.

        Returns:
            bool: ``True`` se o documento final estiver concluído; caso
            contrário, ``False``.
        """
        if not obj.status_em_retificacao:
            return obj.get_tem_documento_final_concluido()
        return CicloRetificacaoService(obj).tem_documento_final_concluido

    def get_tem_ata_concluida(self, obj: Paa) -> bool:
        """
        Informa se a ata do PAA foi concluída.

        Quando o PAA está em retificação, a informação é obtida por meio do
        ciclo de retificação. Caso contrário, utiliza o método da própria
        instância do PAA.

        Args:
            obj (Paa): Instância do Plano de Ação e Acompanhamento.

        Returns:
            bool: ``True`` se a ata estiver concluída; caso contrário,
            ``False``.
        """
        if not obj.status_em_retificacao:
            return obj.get_tem_ata_concluida()
        return CicloRetificacaoService(obj).tem_ata_concluida

    class Meta:
        model = Paa
        fields = ('uuid', 'periodo_paa', 'associacao', 'periodo_paa_objeto', 'saldo_congelado_em',
                  'texto_introducao', 'texto_conclusao', 'status', 'objetivos', 'total_recursos_proprios',
                  'status_andamento', 'tem_documento_final_concluido', 'tem_ata_concluida')
        read_only_fields = ('periodo_paa_objeto', 'periodo_paa', 'status', 'objetivos', 'total_recursos_proprios',
                            'status_andamento', 'tem_documento_final_concluido', 'tem_ata_concluida')

    def get_total_recursos_proprios(self, obj: Paa) -> float:
        """
        Retorna o valor total dos recursos próprios do PAA.

        Args:
            obj (Paa): Instância do Plano de Ação e Acompanhamento.

        Returns:
            Float: Valor total dos recursos próprios do PAA.
        """
        return obj.get_total_recursos_proprios()

    def validate(self, attrs: dict) -> dict:
        """
        Valida os dados para criação de um PAA.

        Verifica se é permitido elaborar um novo PAA e se existe um período
        vigente. Caso as validações sejam satisfeitas, adiciona o período
        vigente aos atributos validados.

        Args:
            attrs (dict): Dados informados para criação do PAA.

        Returns:
            dict: Dados validados acrescidos do período vigente.

        Raises:
            serializers.ValidationError: Caso não seja permitido elaborar um
                novo PAA ou não exista um período vigente.
        """
        from sme_ptrf_apps.paa.services.paa_service import PaaService

        try:
            PaaService.pode_elaborar_novo_paa()
        except Exception as exc:
            raise serializers.ValidationError({'non_field_errors': exc})

        periodo_paa = PeriodoPaa.periodo_vigente()
        if not periodo_paa:
            raise serializers.ValidationError({
                'non_field_errors': ['Nenhum Período vigente foi encontrado.']
            })
        attrs["periodo_paa"] = periodo_paa

        return super().validate(attrs)

    def create(self, validated_data: dict) -> Paa:
        """
        Cria uma nova instância de PAA.

        Antes da criação, verifica se já existe um PAA para a associação e o
        período informados.

        Args:
            validated_data (dict): Dados validados para criação do PAA.

        Returns:
            Paa: Instância do PAA criada.

        Raises:
            serializers.ValidationError: Caso já exista um PAA cadastrado para
                a associação no período informado.
        """
        periodo_paa = validated_data.get('periodo_paa')  # obtido pelo Service, o Período vigente em validate()
        associacao = validated_data.get('associacao')  # obtido pelo payload

        existe_paa = Paa.objects.filter(periodo_paa=periodo_paa, associacao=associacao).exists()
        if existe_paa:
            raise serializers.ValidationError({
                'non_field_errors': ['Já existe um PAA para a Associação informada.']
            })

        instance = super().create(validated_data)

        return instance


class PaaRetificacaoComparativoSerializer(PaaSerializer):
    """
    Serializer responsável por serializar os dados do PAA para o
    comparativo de retificação.

    Estende o ``PaaSerializer``, adicionando as informações de alterações
    identificadas durante o processo de retificação e os dados das atas de
    elaboração e de retificação do PAA.
    """
    alteracoes = serializers.SerializerMethodField()
    ata_elaboracao = AtaPaaSerializer(source='get_ata_elaboracao', many=False, read_only=True)
    ata_retificacao = AtaPaaSerializer(source='get_ata_retificacao', many=False, read_only=True)

    def get_alteracoes(self, obj: Paa) -> dict:
        """
        Retorna as alterações disponíveis no contexto do serializer.

        As alterações são utilizadas para compor o comparativo do processo de
        retificação do PAA.

        Args:
            obj: Instância do PAA.

        Returns:
            dict: Dicionário contendo as alterações ou um dicionário vazio
            caso nenhuma alteração esteja disponível.
        """
        return self.context.get('alteracoes', {})

    class Meta(PaaSerializer.Meta):
        fields = PaaSerializer.Meta.fields + ('alteracoes', 'ata_elaboracao', 'ata_retificacao')
        read_only_fields = PaaSerializer.Meta.read_only_fields + ('alteracoes', 'ata_elaboracao',
                                                                  'ata_retificacao')


class PaaUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer responsável por atualizar e serializar
    os dados de um PAA.

    Além dos campos do modelo, expõe campos calculados para apresentação,
    como os rótulos de status, tipo, ano, mês e a ação de alteração
    associada ao registro.
    """
    objetivos = ObjetivoPaaUpdateSerializer(many=True)
    atividades_estatutarias = AtividadeEstaturariaPaaUpdateSerializer(
        many=True,
        write_only=True
    )
    atividades_estatutarias_paa = AtividadeEstatutariaPaaSerializer(
        source='atividadeestatutariapaa_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = Paa
        fields = [
            "texto_introducao",
            "texto_conclusao",
            "objetivos",
            "atividades_estatutarias",
            "atividades_estatutarias_paa"
        ]

    def update(self, instance: Paa, validated_data: dict) -> dict:
        """
        Atualiza uma nova instância de PAA.

        Args:
            instance: (Paa): Instâcia do PAA
            validated_data (dict): Dados validados para criação do PAA.

        Returns:
            Paa: Instância do PAA atualizada.
        """
        objetivos_data = validated_data.pop("objetivos", None)
        atividades_estatutarias_data = validated_data.pop("atividades_estatutarias", None)

        instance = super().update(instance, validated_data)

        if objetivos_data is not None:
            self._generenciar_objetivos(instance, objetivos_data)

        if atividades_estatutarias_data is not None:
            self._gerenciar_atividades_estatutarias(instance, atividades_estatutarias_data)

        return instance

    def _generenciar_objetivos(self, paa: Paa, objetivos_data: dict) -> None:
        """
        Gerencia os objetivos associadas ao PAA durante a atualização.

        Cada item recebido pode representar um objetivo existente, um nome
        de um objetivo ou a exclusão de um objetivo já vinculada. O método valida
        os dados informados, cria, atualiza ou deleta as instâncias correspondentes.
        """
        with transaction.atomic():
            current_objetivos_ids = []

            for objetivo_input in objetivos_data:
                if "objetivo" in objetivo_input:
                    objetivo = objetivo_input.get("objetivo")

                    if objetivo_input.get('_destroy'):
                        objetivo.delete()
                        continue

                    if paa == objetivo.paa:
                        objetivo.nome = objetivo_input["nome"]
                        objetivo.save(update_fields=['nome'])

                    paa.objetivos.add(objetivo)
                    current_objetivos_ids.append(objetivo.id)

                elif "nome" in objetivo_input:
                    exists = ObjetivoPaa.objects.filter(
                        nome__iexact=objetivo_input["nome"], paa=paa
                    ).exists()

                    if exists:
                        raise serializers.ValidationError({
                            'mensagem': ['Já existe um objetivo cadastrado com este nome.']
                        })
                    objetivo = ObjetivoPaa.objects.create(
                        nome=objetivo_input["nome"],
                        paa=paa
                    )
                    paa.objetivos.add(objetivo)
                    current_objetivos_ids.append(objetivo.id)

            paa.objetivos.set(current_objetivos_ids)

    def _gerenciar_atividades_estatutarias(self, paa: Paa, atividades_data: dict) -> None:
        """
        Gerencia as atividades estatutárias associadas ao PAA durante a atualização.

        Cada item recebido pode representar uma atividade existente, uma nova
        atividade ou a exclusão de uma atividade já vinculada. O método valida
        os dados informados, cria ou atualiza as instâncias correspondentes,
        mantém a relação com o PAA e impede duplicidades ou entradas inválidas.
        """
        with transaction.atomic():

            for item in atividades_data:
                atividade = item.get("atividade_estatutaria")
                nome = item.get("nome")
                tipo = item.get("tipo")
                data = item.get("data")
                destroy = item.get("_destroy", False)

                mes = data.month if data else None

                if atividade:

                    if atividade.paa == paa:

                        if destroy:
                            AtividadeEstatutariaPaa.objects.filter(atividade_estatutaria=atividade).delete()
                            atividade.delete()
                            continue

                        if nome or tipo:
                            if nome:
                                atividade.nome = nome
                            if tipo:
                                atividade.tipo = tipo
                            if mes:
                                atividade.mes = mes

                            if self._atividade_duplicada(
                                paa=paa,
                                nome=atividade.nome,
                                tipo=atividade.tipo,
                                mes=mes,
                                data=data,
                                atividade_id=atividade.id
                            ):
                                raise serializers.ValidationError({
                                    "mensagem": (
                                        "Já existe uma atividade com mesmo nome, tipo, mês e data para este PAA.")
                                })

                            atividade.save()

                    else:
                        if destroy:
                            raise serializers.ValidationError(
                                {"mensagem": "Não é possível excluir atividade estatutária que não pertece ao PAA."})

                    atividade_paa, created = AtividadeEstatutariaPaa.objects.get_or_create(
                        atividade_estatutaria=atividade,
                        paa=paa,
                        defaults={"data": data}
                    )

                    if not created and data:
                        atividade_paa.data = data
                        atividade_paa.save()

                    continue

                if not nome or not tipo or not data:
                    raise serializers.ValidationError({"mensagem": "Nova atividade precisa de nome, tipo e data."})

                if self._atividade_duplicada(
                        paa=paa,
                        nome=nome,
                        tipo=tipo,
                        mes=mes,
                        data=data
                ):
                    raise serializers.ValidationError({
                        "mensagem": "Já existe uma atividade com mesmo nome, tipo, mês e data para este PAA."
                    })

                nova_atividade = AtividadeEstatutaria.objects.create(
                    nome=nome,
                    tipo=tipo,
                    mes=mes,
                    paa=paa
                )

                try:
                    AtividadeEstatutariaPaa.objects.create(
                        atividade_estatutaria=nova_atividade,
                        paa=paa,
                        data=data
                    )
                except IntegrityError:
                    raise serializers.ValidationError(
                        {"mensagem": "Já existe uma atividade paa com esse paa e data."})

    def _atividade_duplicada(self, paa: Paa, nome: str, tipo: str,
                             mes: int, data: date, atividade_id: str | None = None) -> bool:
        """
        Verifica se já existe uma atividade estatutária com os mesmos dados.

        A verificação considera o PAA, o nome, o tipo, o mês e a data da
        atividade. Quando informado, o identificador da atividade é
        desconsiderado da pesquisa, permitindo a validação durante a edição
        do registro.

        Args:
            paa (Paa): Instância do Plano de Ação e Acompanhamento.
            nome (str): Nome da atividade estatutária.
            tipo (str): Tipo da atividade estatutária.
            mes (int): Mês da atividade.
            data (date): Data da atividade.
            atividade_id (str | None): Identificador da atividade a ser
                desconsiderada na verificação.

        Returns:
            bool: ``True`` se existir uma atividade com os mesmos dados;
            caso contrário, ``False``.
        """
        query = AtividadeEstatutariaPaa.objects.filter(
            paa=paa,
            data=data,
            atividade_estatutaria__nome=nome,
            atividade_estatutaria__tipo=tipo,
            atividade_estatutaria__mes=mes,
        )

        if atividade_id:
            query = query.exclude(
                atividade_estatutaria_id=atividade_id
            )

        return query.exists()


class PaaDreSerializer(serializers.ModelSerializer):
    """
    Serializer responsável por serializar os dados de um PAA na visão DRE.

    Além dos campos do modelo, expõe a informação se o PAA possui documento.
    """
    tem_documentos = serializers.SerializerMethodField()
    periodo_paa = PeriodoPaaSimplesSerializer(read_only=True)
    unidade = UnidadeSimplesSerializer(source='associacao.unidade', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    def get_tem_documentos(self, obj: Paa) -> bool:
        """Retorna se o PAA já possui documento na visão DRE"""
        return obj.tem_documentos

    class Meta:
        model = Paa
        fields = ('uuid', 'periodo_paa', 'unidade', 'saldo_congelado_em',
                  'status', 'status_display', 'tem_documentos')

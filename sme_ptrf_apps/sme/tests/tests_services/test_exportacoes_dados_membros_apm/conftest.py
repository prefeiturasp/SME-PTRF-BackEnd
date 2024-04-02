from datetime import date
import pytest
from model_bakery import baker


@pytest.fixture
def ambiente():
    return baker.make(
        'Ambiente',
        prefixo='dev-sig-escola',
        nome='Ambiente de desenvolvimento',
    )


@pytest.fixture
def membros_apm_fixture_mock(cargo_composicao_factory, ocupante_cargo_factory, periodo_factory, associacao_factory, mandato_factory, composicao_factory):
    
    periodo_inicial = periodo_factory.create(referencia="2022.1", data_inicio_realizacao_despesas=date(2022,1,1), data_fim_realizacao_despesas=date(2022,4,20))
    
    associacao = associacao_factory.create(periodo_inicial=periodo_inicial)
    
    mandato_2023_a_2025 = mandato_factory.create(
        referencia_mandato='2023 a 2025',
        data_inicial=date(2023, 7, 19),
        data_final=date(2023, 7, 20)
    )
    
    composicao_2023_a_2025 = composicao_factory.create(
        associacao=associacao,
        mandato=mandato_2023_a_2025,
        data_inicial=date(2023, 1, 1),
        data_final=date(2025, 12, 31),
    )
    
    ocupante_1 = ocupante_cargo_factory.create(
        nome="Matheus Diori",
        codigo_identificacao='1234567',
        cargo_educacao="Diretor de Escola",
        representacao='Servidor',
        email='mdiori@hotmail.com',
        cpf_responsavel='907.536.560-86',
        telefone='11976643126',
        cep='02847070',
        bairro='Jd. Shangrila',
        endereco='Rua longa, 222',
    )
    
    ocupante_2 = ocupante_cargo_factory.create(
        nome="Bert Macklin FBI",
        codigo_identificacao='1234567',
        cargo_educacao="Vogal 1",
        representacao='Servidor',
        email='mdiori@hotmail.com',
        cpf_responsavel='907.536.560-86',
        telefone='11976643126',
        cep='02847070',
        bairro='Jd. Space',
        endereco='Rua curta, 222',
    )
    
    cargo_composicao_1 = cargo_composicao_factory.create(
        composicao=composicao_2023_a_2025,
        ocupante_do_cargo=ocupante_1,
        cargo_associacao='Presidente da diretoria executiva',
        substituto=False,
        substituido=False,
        data_inicio_no_cargo=date(2023, 1, 10),
        data_fim_no_cargo=date(2023, 4, 10),
    )
    
    cargo_composicao_2 = cargo_composicao_factory.create(
        composicao=composicao_2023_a_2025,
        ocupante_do_cargo=ocupante_2,
        cargo_associacao='Vogal 1',
        substituto=False,
        substituido=False,
        data_inicio_no_cargo=date(2023, 3, 10),
        data_fim_no_cargo=date(2023, 5, 10),
    ) 
    
    return

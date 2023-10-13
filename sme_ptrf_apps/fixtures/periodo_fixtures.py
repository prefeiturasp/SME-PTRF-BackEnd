
from datetime import date
import pytest

def criar_periodo(periodo_factory, referencia, data_inicio, data_fim, periodo_anterior=None):
    return periodo_factory.create(
        referencia=referencia,
        data_inicio_realizacao_despesas=data_inicio,
        data_fim_realizacao_despesas=data_fim,
        periodo_anterior=periodo_anterior
    )

@pytest.fixture
def periodos_de_2019_ate_2023(periodo_factory):
    periodo_2019_1 = criar_periodo(periodo_factory, "2019.1", date(2019,1,1), date(2019,3,31))
    periodo_2019_2 = criar_periodo(periodo_factory, "2019.2", date(2019,4,1), date(2019,8,31), periodo_2019_1)
    periodo_2019_3 = criar_periodo(periodo_factory, "2019.3", date(2019,9,1), date(2019,11,30), periodo_2019_2)
    periodo_2020_1 = criar_periodo(periodo_factory, "2020.1", date(2019,12,1), date(2020,10,31), periodo_2019_3)
    periodo_2021_1 = criar_periodo(periodo_factory, "2021.1", date(2020,11,1), date(2021,6,30), periodo_2020_1)
    periodo_2021_2 = criar_periodo(periodo_factory, "2021.2", date(2021,7,1), date(2021,9,30), periodo_2021_1)
    periodo_2021_3 = criar_periodo(periodo_factory, "2021.3", date(2021,10,1), date(2021,12,31), periodo_2021_2)
    periodo_2022_1 = criar_periodo(periodo_factory, "2022.1", date(2022,1,1), date(2022,4,30), periodo_2021_3)
    periodo_2022_2 = criar_periodo(periodo_factory, "2022.2", date(2022,5,1), date(2022,8,31), periodo_2022_1)
    periodo_2022_3 = criar_periodo(periodo_factory, "2022.3", date(2022,9,1), date(2022,12,31), periodo_2022_2)
    periodo_2023_1 = criar_periodo(periodo_factory, "2023.1", date(2023,1,1), date(2023,4,30), periodo_2022_3)
    periodo_2023_2 = criar_periodo(periodo_factory, "2023.2", date(2023,5,1), date(2023,8,31), periodo_2023_1)
    periodo_2023_3 = criar_periodo(periodo_factory, "2023.3", date(2023,9,1), date(2023,12,31), periodo_2023_2)
    
    return periodo_2023_3
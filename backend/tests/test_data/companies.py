"""
Dados de teste para empresas fictícias.

CNPJs válidos gerados para testes.
"""
from datetime import datetime

TEST_COMPANIES = [
    {
        "cnpj": "14.337.098/0999-85",
        "razao_social": "HOSPITAL UNIMED LTDA",
        "nome_fantasia": "HOSPITAL UNIMED",
        "telefone": "(82) 99999-9999",
        "email": "contato@hospitalunimed.com.br",
        "endereco": {
            "cep": "57035-000",
            "logradouro": "AVENIDA FERNANDES LIMA",
            "numero": "1234",
            "complemento": "SALA 101",
            "bairro": "FAROL",
            "cidade": "MACEIÓ",
            "uf": "AL"
        }
    },
    {
        "cnpj": "11.679.181/7399-88",
        "razao_social": "HOSPITAL SÃO CAMILO E SÃO LUIS LTDA",
        "nome_fantasia": "HOSPITAL SÃO CAMILO E SÃO LUIS",
        "telefone": "(96) 99999-9999",
        "email": "contato@hospitalscaomilo.com.br",
        "endereco": {
            "cep": "68900-000",
            "logradouro": "AVENIDA FAB",
            "numero": "1000",
            "complemento": "",
            "bairro": "CENTRO",
            "cidade": "MACAPÁ",
            "uf": "AP"
        }
    },
    {
        "cnpj": "25.979.675/0001-20",
        "razao_social": "HOSPITAL CALIXTO MIDLEJ FILHO - SANTA CASA LTDA",
        "nome_fantasia": "HOSPITAL CALIXTO MIDLEJ FILHO - SANTA CASA",
        "telefone": "(73) 99999-9999",
        "email": "contato@santacasa.com.br",
        "endereco": {
            "cep": "45600-000",
            "logradouro": "RUA DO HOSPITAL",
            "numero": "500",
            "complemento": "",
            "bairro": "CENTRO",
            "cidade": "ITABUNA",
            "uf": "BA"
        }
    },
    {
        "cnpj": "81.352.932/5999-37",
        "razao_social": "HOSPITAL PORTUGUÊS LTDA",
        "nome_fantasia": "HOSPITAL PORTUGUÊS",
        "telefone": "(71) 99999-9999",
        "email": "contato@hospitalportugues.com.br",
        "endereco": {
            "cep": "40000-000",
            "logradouro": "RUA DOIS DE JULHO",
            "numero": "100",
            "complemento": "",
            "bairro": "CENTRO",
            "cidade": "SALVADOR",
            "uf": "BA"
        }
    },
    {
        "cnpj": "94.642.514/3999-19",
        "razao_social": "HOSPITAL SANTA ISABEL - SANTA CASA LTDA",
        "nome_fantasia": "HOSPITAL SANTA ISABEL - SANTA CASA",
        "telefone": "(71) 99999-9999",
        "email": "contato@santaisabel.com.br",
        "endereco": {
            "cep": "40000-000",
            "logradouro": "LARGO DO HOSPITAL",
            "numero": "200",
            "complemento": "",
            "bairro": "CENTRO",
            "cidade": "SALVADOR",
            "uf": "BA"
        }
    },
    {
        "cnpj": "11.236.195/6799-89",
        "razao_social": "HOSPITAL SANTO AMARO - FUNDAÇÃO JOSÉ SILVEIRA LTDA",
        "nome_fantasia": "HOSPITAL SANTO AMARO - FUNDAÇÃO JOSÉ SILVEIRA",
        "telefone": "(71) 99999-9999",
        "email": "contato@santoamaro.com.br",
        "endereco": {
            "cep": "40000-000",
            "logradouro": "RUA DO SANTO AMARO",
            "numero": "300",
            "complemento": "",
            "bairro": "CENTRO",
            "cidade": "SALVADOR",
            "uf": "BA"
        }
    },
    {
        "cnpj": "32.624.466/0000-30",
        "razao_social": "HOSPITAL CURA DARS LTDA",
        "nome_fantasia": "HOSPITAL CURA DARS",
        "telefone": "(85) 99999-9999",
        "email": "contato@curadars.com.br",
        "endereco": {
            "cep": "60000-000",
            "logradouro": "AVENIDA SENADOR VIRGILIO TAVORA",
            "numero": "400",
            "complemento": "",
            "bairro": "CENTRO",
            "cidade": "FORTALEZA",
            "uf": "CE"
        }
    },
    {
        "cnpj": "83.567.862/8999-34",
        "razao_social": "HOSPITAL REGIONAL UNIMED LTDA",
        "nome_fantasia": "HOSPITAL REGIONAL UNIMED",
        "telefone": "(85) 99999-9999",
        "email": "contato@unimedce.com.br",
        "endereco": {
            "cep": "60000-000",
            "logradouro": "RUA CORONEL JUCÁ",
            "numero": "500",
            "complemento": "",
            "bairro": "CENTRO",
            "cidade": "FORTALEZA",
            "uf": "CE"
        }
    },
    {
        "cnpj": "17.119.953/9000-24",
        "razao_social": "HOSPITAL ANCHIETA LTDA",
        "nome_fantasia": "HOSPITAL ANCHIETA",
        "telefone": "(61) 99999-9999",
        "email": "contato@hospitalanchieta.com.br",
        "endereco": {
            "cep": "70000-000",
            "logradouro": "SMPW QUADRA 1",
            "numero": "600",
            "complemento": "",
            "bairro": "ASA NORTE",
            "cidade": "BRASÍLIA",
            "uf": "DF"
        }
    },
    {
        "cnpj": "96.857.444/6999-16",
        "razao_social": "HOSPITAL SANTA LÚCIA GAMA LTDA",
        "nome_fantasia": "HOSPITAL SANTA LÚCIA GAMA",
        "telefone": "(61) 99999-9999",
        "email": "contato@santaluciagama.com.br",
        "endereco": {
            "cep": "70000-000",
            "logradouro": "AREA ESPECIAL 8",
            "numero": "700",
            "complemento": "",
            "bairro": "GAMA",
            "cidade": "BRASÍLIA",
            "uf": "DF"
        }
    },
    {
        "cnpj": "99.072.374/9999-13",
        "razao_social": "HOSPITAL SANTA LÚCIA SUL LTDA",
        "nome_fantasia": "HOSPITAL SANTA LÚCIA SUL",
        "telefone": "(61) 99999-9999",
        "email": "contato@santaluciasul.com.br",
        "endereco": {
            "cep": "70000-000",
            "logradouro": "AREA ESPECIAL 9",
            "numero": "800",
            "complemento": "",
            "bairro": "SUL",
            "cidade": "BRASÍLIA",
            "uf": "DF"
        }
    },
    {
        "cnpj": "10.128.730/5299-91",
        "razao_social": "HOSPITAL SANTA MARTA TAGUATINGA LTDA",
        "nome_fantasia": "HOSPITAL SANTA MARTA TAGUATINGA",
        "telefone": "(61) 99999-9999",
        "email": "contato@santamartataguatinga.com.br",
        "endereco": {
            "cep": "70000-000",
            "logradouro": "AREA ESPECIAL 10",
            "numero": "900",
            "complemento": "",
            "bairro": "TAGUATINGA",
            "cidade": "BRASÍLIA",
            "uf": "DF"
        }
    }
]

def get_test_company(cnpj=None):
    """Retorna uma empresa de teste por CNPJ ou a primeira da lista"""
    if cnpj:
        cnpj_clean = ''.join(c for c in cnpj if c.isdigit())  # Remove formatação
        for company in TEST_COMPANIES:
            if ''.join(c for c in company["cnpj"] if c.isdigit()) == cnpj_clean:
                return company
    return TEST_COMPANIES[0]
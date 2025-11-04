# backend/tests/mocks/cnpj_mock_data.py
"""
Dados mockados para consultas de CNPJ
Elimina dependência de APIs externas e rate limits
"""

# Dados completos dos 12 hospitais para testes
MOCK_CNPJ_DATA = {
    "14337098000185": {  # Hospital Unimed - AL
        "cnpj": "14337098000185",
        "razao_social": "HOSPITAL UNIMED LTDA",
        "nome_fantasia": "HOSPITAL UNIMED",
        "situacao_cadastral": "ATIVA",
        "data_abertura": "2010-01-15",
        "cnae_principal": "8610-1/00",
        "natureza_juridica": "206-2 - SOCIEDADE EMPRESARIA LIMITADA",
        "capital_social": "5000000.00",
        "endereco": {
            "logradouro": "AVENIDA FERNANDES LIMA",
            "numero": "1234",
            "complemento": "SALA 101",
            "bairro": "FAROL",
            "municipio": "MACEIÓ",
            "uf": "AL",
            "cep": "57035000"
        },
        "telefone": "(82) 99999-9999",
        "email": "contato@hospitalunimed.com.br"
    },
    
    "11679181739988": {  # Hospital São Camilo - AP
        "cnpj": "11679181739988",
        "razao_social": "HOSPITAL SAO CAMILO E SAO LUIS LTDA",
        "nome_fantasia": "HOSPITAL SAO CAMILO E SAO LUIS",
        "situacao_cadastral": "ATIVA",
        "data_abertura": "2008-03-20",
        "cnae_principal": "8610-1/00",
        "natureza_juridica": "206-2 - SOCIEDADE EMPRESARIA LIMITADA",
        "capital_social": "3000000.00",
        "endereco": {
            "logradouro": "RUA JOVINO DINOÁ",
            "numero": "1000",
            "bairro": "BURITIZAL",
            "municipio": "MACAPÁ",
            "uf": "AP",
            "cep": "68900073"
        },
        "telefone": "(96) 98888-7777",
        "email": "contato@hospitalsaocamilo.com.br"
    },
    
    "25979675000120": {  # Hospital Calixto - BA
        "cnpj": "25979675000120",
        "razao_social": "HOSPITAL CALIXTO MIDLEJ FILHO LTDA",
        "nome_fantasia": "HOSPITAL CALIXTO MIDLEJ FILHO",
        "situacao_cadastral": "ATIVA",
        "data_abertura": "2005-07-10",
        "cnae_principal": "8610-1/00",
        "natureza_juridica": "206-2 - SOCIEDADE EMPRESARIA LIMITADA",
        "capital_social": "8000000.00",
        "endereco": {
            "logradouro": "AVENIDA CINQUENTENÁRIO",
            "numero": "500",
            "bairro": "CENTRO",
            "municipio": "ITABUNA",
            "uf": "BA",
            "cep": "45600000"
        },
        "telefone": "(73) 97777-6666",
        "email": "contato@hospitalcalixto.com.br"
    },
    
    "81352932599937": {  # Hospital Português - BA
        "cnpj": "81352932599937",
        "razao_social": "HOSPITAL PORTUGUÊS LTDA",
        "nome_fantasia": "HOSPITAL PORTUGUÊS",
        "situacao_cadastral": "ATIVA",
        "data_abertura": "1995-12-05",
        "cnae_principal": "8610-1/00",
        "natureza_juridica": "206-2 - SOCIEDADE EMPRESARIA LIMITADA",
        "capital_social": "12000000.00",
        "endereco": {
            "logradouro": "AVENIDA PRINCESA ISABEL",
            "numero": "2",
            "bairro": "BARRA",
            "municipio": "SALVADOR",
            "uf": "BA",
            "cep": "40140020"
        },
        "telefone": "(71) 96666-5555",
        "email": "contato@hospitalportugues.com.br"
    },
    
    "94642514399919": {  # Hospital Santa Isabel - BA
        "cnpj": "94642514399919",
        "razao_social": "HOSPITAL SANTA ISABEL LTDA",
        "nome_fantasia": "HOSPITAL SANTA ISABEL",
        "situacao_cadastral": "ATIVA",
        "data_abertura": "2000-09-15",
        "cnae_principal": "8610-1/00",
        "natureza_juridica": "206-2 - SOCIEDADE EMPRESARIA LIMITADA",
        "capital_social": "6000000.00",
        "endereco": {
            "logradouro": "RUA SANTA ISABEL",
            "numero": "100",
            "bairro": "SANTA ISABEL",
            "municipio": "SALVADOR",
            "uf": "BA",
            "cep": "40301110"
        },
        "telefone": "(71) 95555-4444",
        "email": "contato@hospitalsantaisabel.com.br"
    },
    
    "11236195679989": {  # Hospital Santo Amaro - BA
        "cnpj": "11236195679989",
        "razao_social": "HOSPITAL SANTO AMARO LTDA",
        "nome_fantasia": "HOSPITAL SANTO AMARO",
        "situacao_cadastral": "ATIVA",
        "data_abertura": "1998-04-22",
        "cnae_principal": "8610-1/00",
        "natureza_juridica": "206-2 - SOCIEDADE EMPRESARIA LIMITADA",
        "capital_social": "4500000.00",
        "endereco": {
            "logradouro": "RUA SANTO AMARO",
            "numero": "200",
            "bairro": "SANTO AMARO",
            "municipio": "SALVADOR",
            "uf": "BA",
            "cep": "40421000"
        },
        "telefone": "(71) 94444-3333",
        "email": "contato@hospitalsantoamaro.com.br"
    },
    
    "32624466000030": {  # Hospital Cura Dars - CE
        "cnpj": "32624466000030",
        "razao_social": "HOSPITAL CURA DARS LTDA",
        "nome_fantasia": "HOSPITAL CURA DARS",
        "situacao_cadastral": "ATIVA",
        "data_abertura": "2012-11-08",
        "cnae_principal": "8610-1/00",
        "natureza_juridica": "206-2 - SOCIEDADE EMPRESARIA LIMITADA",
        "capital_social": "7000000.00",
        "endereco": {
            "logradouro": "AVENIDA SANTOS DUMONT",
            "numero": "3000",
            "bairro": "ALDEOTA",
            "municipio": "FORTALEZA",
            "uf": "CE",
            "cep": "60150160"
        },
        "telefone": "(85) 93333-2222",
        "email": "contato@hospitalcuradars.com.br"
    },
    
    "83567862899934": {  # Hospital Regional Unimed - CE
        "cnpj": "83567862899934",
        "razao_social": "HOSPITAL REGIONAL UNIMED LTDA",
        "nome_fantasia": "HOSPITAL REGIONAL UNIMED",
        "situacao_cadastral": "ATIVA",
        "data_abertura": "2015-06-30",
        "cnae_principal": "8610-1/00",
        "natureza_juridica": "206-2 - SOCIEDADE EMPRESARIA LIMITADA",
        "capital_social": "9000000.00",
        "endereco": {
            "logradouro": "RUA DESEMBARGADOR LEITE ALBUQUERQUE",
            "numero": "1000",
            "bairro": "ALDEOTA",
            "municipio": "FORTALEZA",
            "uf": "CE",
            "cep": "60150030"
        },
        "telefone": "(85) 92222-1111",
        "email": "contato@hospitalregionalunimed.com.br"
    },
    
    "17119953900024": {  # Hospital Anchieta - DF
        "cnpj": "17119953900024",
        "razao_social": "HOSPITAL ANCHIETA LTDA",
        "nome_fantasia": "HOSPITAL ANCHIETA",
        "situacao_cadastral": "ATIVA",
        "data_abertura": "2003-02-14",
        "cnae_principal": "8610-1/00",
        "natureza_juridica": "206-2 - SOCIEDADE EMPRESARIA LIMITADA",
        "capital_social": "15000000.00",
        "endereco": {
            "logradouro": "SETOR HOSPITALAR SUL",
            "numero": "10",
            "bairro": "ASA SUL",
            "municipio": "BRASÍLIA",
            "uf": "DF",
            "cep": "70390108"
        },
        "telefone": "(61) 91111-0000",
        "email": "contato@hospitalanchieta.com.br"
    },
    
    "96857444699916": {  # Hospital Santa Lúcia Gama - DF
        "cnpj": "96857444699916",
        "razao_social": "HOSPITAL SANTA LUCIA GAMA LTDA",
        "nome_fantasia": "HOSPITAL SANTA LUCIA GAMA",
        "situacao_cadastral": "ATIVA",
        "data_abertura": "2007-08-25",
        "cnae_principal": "8610-1/00",
        "natureza_juridica": "206-2 - SOCIEDADE EMPRESARIA LIMITADA",
        "capital_social": "6500000.00",
        "endereco": {
            "logradouro": "ÁREA ESPECIAL",
            "numero": "1",
            "bairro": "SETOR CENTRAL",
            "municipio": "GAMA",
            "uf": "DF",
            "cep": "72405610"
        },
        "telefone": "(61) 90000-9999",
        "email": "contato@hospitalsantaluciagama.com.br"
    },
    
    "99072374999913": {  # Hospital Santa Lúcia Sul - DF
        "cnpj": "99072374999913",
        "razao_social": "HOSPITAL SANTA LUCIA SUL LTDA",
        "nome_fantasia": "HOSPITAL SANTA LUCIA SUL",
        "situacao_cadastral": "ATIVA",
        "data_abertura": "2009-05-18",
        "cnae_principal": "8610-1/00",
        "natureza_juridica": "206-2 - SOCIEDADE EMPRESARIA LIMITADA",
        "capital_social": "8500000.00",
        "endereco": {
            "logradouro": "SETOR HOSPITALAR SUL",
            "numero": "20",
            "bairro": "ASA SUL",
            "municipio": "BRASÍLIA",
            "uf": "DF",
            "cep": "70390108"
        },
        "telefone": "(61) 98888-7777",
        "email": "contato@hospitalsantaluciasul.com.br"
    },
    
    "10128730529991": {  # Hospital Santa Marta Taguatinga - DF
        "cnpj": "10128730529991",
        "razao_social": "HOSPITAL SANTA MARTA TAGUATINGA LTDA",
        "nome_fantasia": "HOSPITAL SANTA MARTA TAGUATINGA",
        "situacao_cadastral": "ATIVA",
        "data_abertura": "2011-10-12",
        "cnae_principal": "8610-1/00",
        "natureza_juridica": "206-2 - SOCIEDADE EMPRESARIA LIMITADA",
        "capital_social": "7500000.00",
        "endereco": {
            "logradouro": "QNM 40",
            "numero": "610",
            "bairro": "CEILÂNDIA SUL",
            "municipio": "BRASÍLIA",
            "uf": "DF",
            "cep": "72220400"
        },
        "telefone": "(61) 97777-6666",
        "email": "contato@hospitalsantamartataguatinga.com.br"
    }
}

def get_mock_cnpj_data(cnpj: str):
    """Retorna dados mockados para um CNPJ específico"""
    # Remove formatação do CNPJ
    clean_cnpj = ''.join(filter(str.isdigit, cnpj))
    return MOCK_CNPJ_DATA.get(clean_cnpj, None)

def get_all_valid_cnpjs():
    """Retorna lista de todos os CNPJs válidos para testes"""
    return list(MOCK_CNPJ_DATA.keys())

def is_valid_test_cnpj(cnpj: str):
    """Verifica se um CNPJ está na lista de testes válidos"""
    clean_cnpj = ''.join(filter(str.isdigit, cnpj))
    return clean_cnpj in MOCK_CNPJ_DATA

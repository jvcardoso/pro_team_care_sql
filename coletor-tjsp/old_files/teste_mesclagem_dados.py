#!/usr/bin/env python3
"""
Teste da lógica de mesclagem de dados API + Scraping
"""
import sys
import os
from datetime import datetime

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(__file__))

from src.hybrid_collector import HybridCollector

def teste_mesclagem_dados():
    """Teste da lógica de mesclagem sem scraping real"""
    print("=" * 80)
    print("TESTE DE MESCLAGEM DE DADOS")
    print("=" * 80)

    # Dados simulados da API DataJud (baseado no resultado real)
    dados_api = {
        "numero": "10284846520198260576",
        "numero_formatado": "1028484-65.2019.8.26.0576",
        "classe": "Execução de Título Extrajudicial",
        "assuntos": [],
        "assunto_principal": None,
        "orgao_julgador": "01 CIVEL DE SAO JOSE DO RIO PRETO",
        "comarca": None,
        "data_ajuizamento": "2019-07-11T09:16:26.000Z",
        "data_ultima_atualizacao": "2025-02-06T00:09:15.277Z",
        "sistema": "SAJ",
        "grau": "G1",
        "tribunal": None,
        "status": None,
        "valor_causa": None,
        "quantidade_movimentacoes": 178,
        "fonte": "API DataJud (CNJ)",
        "data_consulta": "2025-10-30T15:46:31.749806"
    }

    # Dados simulados do web scraping (baseado no exemplo fornecido)
    dados_scraping = {
        'processo_numero': '1028484-65.2019.8.26.0576',
        'coleta_timestamp': datetime.now().isoformat(),
        'vara': '1ª Vara Cível de São José do Rio Preto',
        'classe_assunto': 'Execução de Título Extrajudicial - Despesas Condominiais',
        'valor_causa': 'R$ 40.633,29',
        'exequente': 'Parque Rio Nieva',
        'executado': 'Juliano Ventura Cardoso',
        'advogado_autor_nome': 'Adilson Lopes Teixeira',
        'advogado_autor_oab': '357725/SP',
        'advogado_reu_nome': 'Darcio Jose da Mota',
        'advogado_reu_oab': '67669/SP',
        'situacao': 'Em andamento',
        'movimentacoes': []
    }

    # Criar instância do coletor (sem contexto async para teste)
    coletor = HybridCollector()

    print("📊 DADOS DE ENTRADA:")
    print("-" * 50)
    print("🔍 API DataJud:")
    print(f"   Classe: {dados_api['classe']}")
    print(f"   Órgão: {dados_api['orgao_julgador']}")
    print(f"   Movimentações: {dados_api['quantidade_movimentacoes']}")
    print()

    print("🕷️  Web Scraping:")
    print(f"   Vara: {dados_scraping['vara']}")
    print(f"   Exequente: {dados_scraping['exequente']}")
    print(f"   Executado: {dados_scraping['executado']}")
    print(f"   Adv. Autor: {dados_scraping['advogado_autor_nome']} ({dados_scraping['advogado_autor_oab']})")
    print(f"   Adv. Réu: {dados_scraping['advogado_reu_nome']} ({dados_scraping['advogado_reu_oab']})")
    print()

    # Testar mesclagem
    print("🔀 MESCLANDO DADOS...")
    dados_mesclados = coletor._mesclar_dados_api_scraping(dados_api, dados_scraping)

    print("✅ Mesclagem concluída!")
    print()

    print("📋 RESULTADO FINAL:")
    print("-" * 50)
    print(f"🎯 Fonte: {dados_mesclados['fonte']}")
    print(f"📄 Número: {dados_mesclados['numero_formatado']}")
    print(f"🏛️  Classe: {dados_mesclados['classe']}")
    print(f"⚖️  Órgão: {dados_mesclados['orgao_julgador']}")
    print(f"🔄 Movimentações: {dados_mesclados['quantidade_movimentacoes']}")
    print()

    # Dados complementares
    complementares = dados_mesclados.get('dados_complementares', {})
    print("🔍 Dados Complementares:")
    print(f"   Vara detalhada: {complementares.get('vara_detalhada', 'N/A')}")
    print(f"   Situação: {complementares.get('situacao', 'N/A')}")
    print(f"   Valor causa: {complementares.get('valor_causa_formatado', 'N/A')}")
    print()

    # Partes
    partes = dados_mesclados.get('partes', {})
    print("👥 Partes do Processo:")
    if 'exequente' in partes:
        print(f"   Exequente: {partes['exequente']}")
    if 'executado' in partes:
        print(f"   Executado: {partes['executado']}")
    print()

    # Advogados
    advogados = dados_mesclados.get('advogados', {})
    print("⚖️  Advogados:")
    if 'autor' in advogados:
        adv_autor = advogados['autor']
        print(f"   Adv. Exequente: {adv_autor.get('nome', 'N/A')} - OAB: {adv_autor.get('oab', 'N/A')}")
    if 'reu' in advogados:
        adv_reu = advogados['reu']
        print(f"   Adv. Executado: {adv_reu.get('nome', 'N/A')} - OAB: {adv_reu.get('oab', 'N/A')}")
    print()

    # Validação
    print("🎯 VALIDAÇÃO:")
    print("-" * 30)

    validacoes = []

    # Verificar se dados essenciais foram preservados
    if dados_mesclados['classe'] == dados_api['classe']:
        validacoes.append(("✅ Classe API", "Preservada"))
    else:
        validacoes.append(("❌ Classe API", "Perdida"))

    if dados_mesclados['quantidade_movimentacoes'] == dados_api['quantidade_movimentacoes']:
        validacoes.append(("✅ Movimentações", "Preservadas"))
    else:
        validacoes.append(("❌ Movimentações", "Perdidas"))

    # Verificar se dados de scraping foram adicionados
    if 'partes' in dados_mesclados and dados_mesclados['partes']:
        validacoes.append(("✅ Partes", "Adicionadas"))
    else:
        validacoes.append(("❌ Partes", "Não adicionadas"))

    if 'advogados' in dados_mesclados and dados_mesclados['advogados']:
        validacoes.append(("✅ Advogados", "Adicionados"))
    else:
        validacoes.append(("❌ Advogados", "Não adicionados"))

    if 'dados_complementares' in dados_mesclados:
        validacoes.append(("✅ Dados complementares", "Adicionados"))
    else:
        validacoes.append(("❌ Dados complementares", "Não adicionados"))

    for validacao in validacoes:
        print(f"   {validacao[0]}: {validacao[1]}")

    print()
    print("💾 Salvando resultado de teste...")
    import json
    resultado_teste = {
        'teste': 'mesclagem_dados',
        'timestamp': datetime.now().isoformat(),
        'dados_mesclados': dados_mesclados,
        'validacoes': validacoes
    }

    with open('output/teste_mesclagem.json', 'w', encoding='utf-8') as f:
        json.dump(resultado_teste, f, indent=2, ensure_ascii=False, default=str)

    print("✅ Resultado salvo em: output/teste_mesclagem.json")

    print()
    print("=" * 80)
    print("TESTE DE MESCLAGEM CONCLUÍDO!")
    print("=" * 80)

    # Verificar sucesso
    sucesso = all("✅" in v[0] for v in validacoes)
    if sucesso:
        print("🎉 SUCESSO: Mesclagem funcionando perfeitamente!")
    else:
        print("⚠️  PARCIAL: Algumas validações falharam")

    return sucesso

if __name__ == "__main__":
    try:
        sucesso = teste_mesclagem_dados()
        exit(0 if sucesso else 1)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
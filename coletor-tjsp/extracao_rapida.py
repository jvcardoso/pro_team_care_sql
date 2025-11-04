#!/usr/bin/env python3
"""
Extração rápida focada em JSON e CSV apenas
Processa ~4 processos por minuto
"""
import asyncio
import csv
import json
from pathlib import Path
from datetime import datetime
from src.scraper import TJSPScraper

async def extracao_rapida():
    """Extração rápida focada em JSON/CSV"""
    print("🚀 EXTRAÇÃO RÁPIDA - JSON/CSV APENAS")
    print("=" * 50)

    # Carregar lista de processos
    lista_csv = Path("./resultado_parque_rio_nieva/lista_processos_parque_rio_nieva.csv")
    if not lista_csv.exists():
        print("❌ Lista de processos não encontrada!")
        return

    processos = []
    with open(lista_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            processos.append(row['processo_numero'])

    # Para demonstração, processar apenas os primeiros 3 processos
    processos = processos[:3]
    print(f"📋 Carregados {len(processos)} processos da lista (demonstração)")

    # Criar diretório de saída
    output_dir = Path("./dados_completos_parque_rio_nieva")
    output_dir.mkdir(exist_ok=True)

    # Arquivos de saída
    json_file = output_dir / "processos_completos.json"
    csv_file = output_dir / "processos_completos.csv"

    # Inicializar dados
    todos_processos = []
    csv_data = []

    async with TJSPScraper() as scraper:
        total = len(processos)
        print(f"🎯 Iniciando processamento de {total} processos...")

        for i, processo_numero in enumerate(processos, 1):
            print(f"\n[{i}/{total}] Processando: {processo_numero}")

            try:
                # Buscar dados do processo
                dados = await scraper.search_by_process_number(processo_numero)

                if dados:
                    print("  ✅ Dados extraídos com sucesso")
                    # Adicionar à lista JSON
                    todos_processos.append(dados)

                    # Preparar dados para CSV
                    csv_row = {
                        'processo_numero': dados.get('processo_numero', ''),
                        'vara': dados.get('vara', ''),
                        'classe_assunto': dados.get('classe_assunto', ''),
                        'valor_causa': dados.get('valor_causa', ''),
                        'exequente': dados.get('exequente', ''),
                        'executado': dados.get('executado', ''),
                        'situacao': dados.get('situacao', ''),
                        'total_movimentacoes': len(dados.get('movimentacoes', [])),
                        'coleta_timestamp': dados.get('coleta_timestamp', ''),
                        'etiqueta_opcional': 'Parte: Parque Rio Nieva'
                    }
                    csv_data.append(csv_row)

                else:
                    print("  ⚠️ Processo não encontrado ou em segredo")
                    # Adicionar entrada vazia para manter consistência
                    csv_row = {
                        'processo_numero': processo_numero,
                        'vara': '',
                        'classe_assunto': '',
                        'valor_causa': '',
                        'exequente': '',
                        'executado': '',
                        'situacao': 'SEGREDO_DE_JUSTICA',
                        'total_movimentacoes': 0,
                        'coleta_timestamp': datetime.now().isoformat(),
                        'etiqueta_opcional': 'Parte: Parque Rio Nieva'
                    }
                    csv_data.append(csv_row)

            except Exception as e:
                print(f"  ❌ Erro: {e}")
                csv_row = {
                    'processo_numero': processo_numero,
                    'vara': '',
                    'classe_assunto': '',
                    'valor_causa': '',
                    'exequente': '',
                    'executado': '',
                    'situacao': f'ERRO: {str(e)}',
                    'total_movimentacoes': 0,
                    'coleta_timestamp': datetime.now().isoformat(),
                    'etiqueta_opcional': 'Parte: Parque Rio Nieva'
                }
                csv_data.append(csv_row)

            # Delay entre processos (~4 por minuto = 15s médio)
            if i < total:
                delay = 15  # segundos
                print(f"  ⏱️ Aguardando {delay}s antes do próximo...")
                await asyncio.sleep(delay)

    # Salvar JSON
    print("\n💾 Salvando JSON...")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'fonte': 'TJSP Coletor',
                'parte_pesquisada': 'Parque Rio Nieva',
                'total_processos': len(todos_processos),
                'data_coleta': datetime.now().isoformat(),
                'processos_sigilosos': len([p for p in csv_data if p['situacao'] == 'SEGREDO_DE_JUSTICA'])
            },
            'processos': todos_processos
        }, f, ensure_ascii=False, indent=2)

    # Salvar CSV
    print("💾 Salvando CSV...")
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        if csv_data:
            writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
            writer.writeheader()
            writer.writerows(csv_data)

    # Estatísticas finais
    processos_publicos = len([p for p in csv_data if p['situacao'] != 'SEGREDO_DE_JUSTICA' and 'ERRO' not in p['situacao']])
    processos_sigilosos = len([p for p in csv_data if p['situacao'] == 'SEGREDO_DE_JUSTICA'])
    processos_erros = len([p for p in csv_data if 'ERRO' in p['situacao']])

    print("\n🎯 EXTRAÇÃO CONCLUÍDA!")
    print(f"   📄 JSON: {json_file}")
    print(f"   📊 CSV: {csv_file}")
    print(f"   📁 Local: {output_dir.absolute()}")
    print("\n📊 ESTATÍSTICAS:")
    print(f"   ✅ Processos públicos: {processos_publicos}")
    print(f"   🔒 Processos sigilosos: {processos_sigilosos}")
    print(f"   ❌ Processos com erro: {processos_erros}")
    print(f"   📈 Total processado: {len(csv_data)}")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(extracao_rapida())
#!/usr/bin/env python3
"""
Workflow completo para Rio Nieva:
1. Buscar processos por nome da parte "Rio Nieva"
2. Extrair dados completos e movimentações de cada processo
3. Salvar em output/rio_nieva_completo/
"""
import asyncio
import sys
import os
import json
import argparse
import shutil
from pathlib import Path
from datetime import datetime

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(__file__))

from src.scraper import TJSPScraper
from loguru import logger

# Configuração de paralelização (por enquanto mantida sequencial para estabilidade)
MAX_WORKERS_DEFAULT = 3

# Configurar logging
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")


async def workflow_rio_nieva(start_process=1, end_process=None, max_workers=3):
    """Executa workflow completo para Rio Nieva

    Args:
        start_process: Número do primeiro processo a processar (1-based)
        end_process: Número do último processo a processar (None = todos)
        max_workers: Número máximo de workers paralelos (1-5 recomendado)
    """

    print("=" * 80)
    print("🏛️  WORKFLOW COMPLETO - RIO NIEVA")
    if start_process > 1 or end_process:
        print(f"📊 LOTE: Processos {start_process} até {end_process or 'todos'}")
    if max_workers > 1:
        print(f"⚡ PARALELIZAÇÃO: {max_workers} workers simultâneos")
    print("=" * 80)

    # Diretório de saída
    output_dir = Path("output/rio_nieva_completo")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Limpar arquivos existentes para evitar dados incorretos
    for file_path in output_dir.glob('*'):
        if file_path.is_file():
            file_path.unlink()
        elif file_path.is_dir():
            shutil.rmtree(file_path)

    # Arquivo de log
    log_file = output_dir / f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logger.add(log_file, level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")

    logger.info("🚀 Iniciando workflow Rio Nieva")

    # PASSO 1: Buscar processos por nome da parte
    party_name = "Rio Nieva"
    logger.info(f"🔍 PASSO 1: Buscando processos para '{party_name}'")

    async with TJSPScraper() as scraper:
        # Buscar processos
        processos_encontrados = await scraper.search_by_party(party_name)

        if not processos_encontrados:
            logger.error("❌ Nenhum processo encontrado para a parte especificada")
            return False

        logger.info(f"📊 Encontrados {len(processos_encontrados)} processos")

        # Filtrar por range se especificado
        if end_process:
            processos_encontrados = processos_encontrados[start_process-1:end_process]
        else:
            processos_encontrados = processos_encontrados[start_process-1:]

        logger.info(f"🎯 Processando {len(processos_encontrados)} processos (do {start_process} ao {end_process or 'último'})")

    # PASSO 2: Processamento paralelo
    logger.info(f"⚡ PASSO 2: Processamento paralelo com {max_workers} workers")

    # Semaphore para controlar concorrência máxima (limitado para evitar conflitos)
    semaphore = asyncio.Semaphore(1)

    # Dividir processos em chunks
    chunk_size = len(processos_encontrados) // max_workers
    remainder = len(processos_encontrados) % max_workers
    chunks = []
    start = 0
    for i in range(max_workers):
        size = chunk_size + (1 if i < remainder else 0)
        chunks.append(processos_encontrados[start:start + size])
        start += size

    async def process_chunk(chunk, worker_id):
        """Processa um chunk de processos com scraper próprio"""
        async with semaphore:  # Controla concorrência
            processos_sucesso = []
            processos_erro = []
            start_index = start_process + sum(len(c) for c in chunks[:worker_id])

            async with TJSPScraper() as scraper:  # Cada worker tem seu próprio scraper
                for idx, processo_numero in enumerate(chunk):
                    index = start_index + idx
                    logger.info(f"[{index}/{len(processos_encontrados)}] Worker {worker_id+1}: Processando {processo_numero}")

                    try:
                        # Extrair dados do processo
                        dados_processo = await scraper.search_by_process_number(processo_numero)

                        if dados_processo:
                            # Salvar dados individuais
                            filename = f"processo_completo_{processo_numero.replace('.', '_').replace('-', '_')}.json"
                            filepath = output_dir / filename

                            with open(filepath, 'w', encoding='utf-8') as f:
                                json.dump(dados_processo, f, indent=2, ensure_ascii=False)

                            logger.info(f"   ✅ Salvo: {filename}")
                            processos_sucesso.append({
                                "processo": processo_numero,
                                "arquivo": filename,
                                "total_movimentacoes": len(dados_processo.get('movimentacoes', []))
                            })
                        else:
                            logger.error(f"   ❌ Falha ao extrair: {processo_numero}")
                            processos_erro.append(processo_numero)

                    except Exception as e:
                        logger.error(f"   ❌ Erro no processo {processo_numero}: {e}")
                        processos_erro.append(processo_numero)

                    # Delay entre processos no mesmo worker
                    await scraper.random_delay()

            return processos_sucesso, processos_erro

    # Criar tarefas para cada chunk
    tasks = []
    for idx, chunk in enumerate(chunks):
        task = asyncio.create_task(process_chunk(chunk, idx))
        tasks.append(task)

    # Aguardar conclusão de todas as tarefas
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Processar resultados
    processos_sucesso = []
    processos_erro = []

    for result in results:
        if isinstance(result, tuple):
            sucesso, erro = result
            processos_sucesso.extend(sucesso)
            processos_erro.extend(erro)
        elif isinstance(result, Exception):
            logger.error(f"   ❌ Exceção em worker: {result}")
            processos_erro.append("excecao_worker")

    # PASSO 3: Gerar relatório final
    logger.info("📋 PASSO 3: Gerando relatório final")

    relatorio = {
        "workflow": "Rio Nieva - Dados Completos",
        "data_execucao": datetime.now().isoformat(),
        "party_name": party_name,
        "estatisticas": {
            "processos_encontrados": len(processos_encontrados),
            "processos_sucesso": len(processos_sucesso),
            "processos_erro": len(processos_erro),
            "taxa_sucesso": f"{len(processos_sucesso)/len(processos_encontrados)*100:.1f}%" if processos_encontrados else "0%"
        },
        "processos_sucesso": processos_sucesso,
        "processos_erro": processos_erro,
        "diretorio_saida": str(output_dir)
    }

    relatorio_file = output_dir / "relatorio_workflow.json"
    with open(relatorio_file, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)

    # PASSO 4: Exibir resumo
    print("\n" + "=" * 80)
    print("📊 RESUMO DO WORKFLOW")
    print("=" * 80)
    print(f"🏛️  Parte pesquisada: {party_name}")
    print(f"📂 Diretório de saída: {output_dir}")
    print(f"🔍 Processos encontrados: {len(processos_encontrados)}")
    print(f"✅ Processos processados: {len(processos_sucesso)}")
    print(f"❌ Processos com erro: {len(processos_erro)}")
    print(f"📈 Taxa de sucesso: {relatorio['estatisticas']['taxa_sucesso']}")

    if processos_sucesso:
        print("\n📋 Processos extraídos:")
        for proc in processos_sucesso[:5]:  # Mostra primeiros 5
            print(
                f"   ✅ {proc['processo']} "
                f"({proc['total_movimentacoes']} movimentações)"
            )
        if len(processos_sucesso) > 5:
            print(f"   ... e mais {len(processos_sucesso) - 5} processos")

    if processos_erro:
        print("\n❌ Processos com erro:")
        for proc in processos_erro[:3]:  # Mostra primeiros 3
            print(f"   ❌ {proc}")
        if len(processos_erro) > 3:
            print(f"   ... e mais {len(processos_erro) - 3} processos")

    print(f"\n📄 Relatório completo: {relatorio_file}")
    print(f"📄 Log detalhado: {log_file}")
    print("=" * 80)

    logger.info("🎉 Workflow Rio Nieva concluído com sucesso!")
    return True


async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Workflow Rio Nieva - Extração de dados processuais')
    parser.add_argument(
        '--start',
        type=int,
        default=1,
        help='Número do primeiro processo a processar (1-based)'
    )
    parser.add_argument(
        '--end',
        type=int,
        default=None,
        help='Número do último processo a processar (None = todos)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=3,
        help='Número de workers paralelos (1-5 recomendado, padrão: 3)'
    )

    args = parser.parse_args()

    sucesso = await workflow_rio_nieva(start_process=args.start, end_process=args.end, max_workers=args.workers)
    sys.exit(0 if sucesso else 1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nWorkflow interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)

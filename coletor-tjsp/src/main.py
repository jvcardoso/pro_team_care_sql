#!/usr/bin/env python3
"""
Script principal do coletor TJSP
"""
import asyncio
import argparse
import csv
import sys
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from loguru import logger

from .config import Config
from .scraper import TJSPScraper
from .exporter import DataExporter


def setup_logging():
    """Configura sistema de logs"""
    config = Config()
    
    # Remove handler padrão
    logger.remove()
    
    # Console handler
    logger.add(
        sys.stderr,
        level=config.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
    )
    
    # File handler
    if config.ROTATE_LOGS:
        logger.add(
            config.get_log_path("coletor_{time}.log"),
            rotation=f"{config.MAX_LOG_SIZE} MB",
            retention=config.LOG_RETENTION,
            level=config.LOG_LEVEL
        )
    else:
        logger.add(
            config.get_log_path("coletor.log"),
            level=config.LOG_LEVEL
        )


def load_process_list(input_file: Path) -> List[Dict]:
    """
    Carrega lista de processos do arquivo CSV
    
    Args:
        input_file: Caminho do arquivo CSV
        
    Returns:
        Lista de processos
    """
    processos = []
    
    try:
        with open(input_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                processos.append({
                    'processo_numero': row.get('processo_numero', '').strip(),
                    'etiqueta_opcional': row.get('etiqueta_opcional', '').strip()
                })
        
        logger.info(f"Carregados {len(processos)} processos do arquivo {input_file}")
        
    except Exception as e:
        logger.error(f"Erro ao carregar arquivo de entrada: {e}")
        sys.exit(1)
    
    return processos


async def collect_single_process(scraper: TJSPScraper, processo_info: Dict) -> Dict:
    """
    Coleta dados de um único processo
    
    Args:
        scraper: Instância do scraper
        processo_info: Informações do processo
        
    Returns:
        Dados coletados
    """
    processo_numero = processo_info['processo_numero']
    
    try:
        logger.info(f"Coletando processo: {processo_numero}")
        
        # Buscar processo
        data = await scraper.search_by_process_number(processo_numero)
        
        if data:
            # Adicionar etiqueta opcional
            data['etiqueta_opcional'] = processo_info.get('etiqueta_opcional', '')
            logger.success(f"✓ Processo {processo_numero} coletado com sucesso")
        else:
            logger.warning(f"✗ Processo {processo_numero} não encontrado ou em segredo")
            data = {
                'processo_numero': processo_numero,
                'etiqueta_opcional': processo_info.get('etiqueta_opcional', ''),
                'erro': 'Processo não encontrado ou em segredo de justiça',
                'coleta_timestamp': datetime.now().isoformat()
            }
        
        return data
        
    except Exception as e:
        logger.error(f"Erro ao coletar processo {processo_numero}: {e}")
        return {
            'processo_numero': processo_numero,
            'etiqueta_opcional': processo_info.get('etiqueta_opcional', ''),
            'erro': str(e),
            'coleta_timestamp': datetime.now().isoformat()
        }


async def collect_by_lawyer(scraper: TJSPScraper, lawyer_name: str) -> List[str]:
    """
    Busca processos por advogado
    
    Args:
        scraper: Instância do scraper
        lawyer_name: Nome do advogado
        
    Returns:
        Lista de números de processos
    """
    logger.info(f"Buscando processos do advogado: {lawyer_name}")
    
    try:
        processos = await scraper.search_by_lawyer(lawyer_name)
        logger.success(f"Encontrados {len(processos)} processos do advogado {lawyer_name}")
        return processos
    except Exception as e:
        logger.error(f"Erro ao buscar por advogado: {e}")
        return []


async def collect_by_party(scraper: TJSPScraper, party_name: str) -> List[str]:
    """
    Busca processos por parte
    
    Args:
        scraper: Instância do scraper
        party_name: Nome da parte
        
    Returns:
        Lista de números de processos
    """
    logger.info(f"Buscando processos da parte: {party_name}")
    
    try:
        processos = await scraper.search_by_party(party_name)
        logger.success(f"Encontrados {len(processos)} processos da parte {party_name}")
        return processos
    except Exception as e:
        logger.error(f"Erro ao buscar por parte: {e}")
        return []


async def main():
    """Função principal"""
    # Parser de argumentos
    parser = argparse.ArgumentParser(
        description='Coletor de processos públicos TJSP 1º Grau'
    )
    
    # Argumentos de entrada
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        '--input', '-i',
        type=Path,
        help='Arquivo CSV com lista de processos'
    )
    input_group.add_argument(
        '--search-lawyer',
        type=str,
        help='Buscar processos por nome do advogado'
    )
    input_group.add_argument(
        '--search-party',
        type=str,
        help='Buscar processos por nome da parte'
    )
    
    # Argumentos de saída
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=Path('./output'),
        help='Diretório de saída (padrão: ./output)'
    )
    
    # Opções adicionais
    parser.add_argument(
        '--max-mov',
        type=int,
        default=0,
        help='Máximo de movimentações por processo (0 = sem limite)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Modo debug (salva HTML bruto)'
    )
    parser.add_argument(
        '--monitor',
        action='store_true',
        help='Modo monitoramento contínuo'
    )
    parser.add_argument(
        '--interval',
        type=str,
        default='6h',
        help='Intervalo de monitoramento (ex: 6h, 30m)'
    )
    
    args = parser.parse_args()
    
    # Validar argumentos
    if not any([args.input, args.search_lawyer, args.search_party]):
        parser.error('É necessário especificar --input, --search-lawyer ou --search-party')
    
    # Setup
    setup_logging()
    config = Config()
    
    # Aplicar configurações dos argumentos
    if args.max_mov:
        config.MAX_MOVIMENTACOES = args.max_mov
    if args.debug:
        config.DEBUG_MODE = True
    
    logger.info("=" * 60)
    logger.info("COLETOR DE PROCESSOS TJSP - 1º GRAU")
    logger.info("=" * 60)
    
    # Criar scraper
    async with TJSPScraper() as scraper:
        processos_para_coletar = []
        
        # Determinar lista de processos
        if args.input:
            # Carregar de arquivo
            processos_info = load_process_list(args.input)
            processos_para_coletar = processos_info
            
        elif args.search_lawyer:
            # Buscar por advogado
            numeros = await collect_by_lawyer(scraper, args.search_lawyer)
            processos_para_coletar = [
                {'processo_numero': num, 'etiqueta_opcional': f'Adv: {args.search_lawyer}'}
                for num in numeros
            ]
            
        elif args.search_party:
            # Buscar por parte
            numeros = await collect_by_party(scraper, args.search_party)
            processos_para_coletar = [
                {'processo_numero': num, 'etiqueta_opcional': f'Parte: {args.search_party}'}
                for num in numeros
            ]
        
        if not processos_para_coletar:
            logger.warning("Nenhum processo para coletar")
            return
        
        logger.info(f"Total de processos para coletar: {len(processos_para_coletar)}")
        
        # Coletar dados
        resultados = []
        total = len(processos_para_coletar)
        
        for idx, processo_info in enumerate(processos_para_coletar, 1):
            logger.info(f"[{idx}/{total}] Processando...")
            
            resultado = await collect_single_process(scraper, processo_info)
            resultados.append(resultado)
            
            # Delay entre processos
            if idx < total:
                await scraper.random_delay()
        
        # Exportar resultados
        logger.info("Exportando resultados...")
        exporter = DataExporter()
        
        # Filtrar processos com sucesso
        processos_sucesso = [r for r in resultados if 'erro' not in r]
        processos_erro = [r for r in resultados if 'erro' in r]
        
        if processos_sucesso:
            # Exportar CSVs
            exporter.export_to_csv(processos_sucesso, args.output)
            
            # Exportar JSON
            exporter.export_to_json(processos_sucesso, args.output)
            
            # Gerar dashboard HTML
            exporter.export_html_dashboard(processos_sucesso, args.output)
        
        # Relatório de erros
        if processos_erro:
            logger.warning(f"Processos com erro: {len(processos_erro)}")
            for erro in processos_erro:
                logger.error(f"  - {erro['processo_numero']}: {erro['erro']}")
        
        # Resumo final
        logger.info("=" * 60)
        logger.info("COLETA FINALIZADA")
        logger.info(f"✓ Sucesso: {len(processos_sucesso)} processos")
        logger.info(f"✗ Erro: {len(processos_erro)} processos")
        logger.info(f"📁 Resultados salvos em: {args.output}")
        logger.info("=" * 60)
        
        # Modo monitoramento
        if args.monitor:
            logger.info(f"Modo monitoramento ativado - Intervalo: {args.interval}")
            logger.info("Pressione Ctrl+C para parar")
            
            # Parse intervalo
            interval_seconds = 3600 * 6  # Padrão 6h
            if args.interval.endswith('h'):
                interval_seconds = int(args.interval[:-1]) * 3600
            elif args.interval.endswith('m'):
                interval_seconds = int(args.interval[:-1]) * 60
            
            while True:
                try:
                    logger.info(f"Aguardando {args.interval} para próxima coleta...")
                    await asyncio.sleep(interval_seconds)
                    
                    # Re-executar coleta
                    logger.info("Iniciando nova coleta...")
                    # ... código de re-coleta aqui ...
                    
                except KeyboardInterrupt:
                    logger.info("Monitoramento interrompido pelo usuário")
                    break


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Execução interrompida pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)

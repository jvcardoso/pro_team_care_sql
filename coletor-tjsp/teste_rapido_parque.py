#!/usr/bin/env python3
"""
Script rápido para demonstrar a funcionalidade do coletor TJSP
Coleta apenas os números dos processos e gera relatório básico
"""
import asyncio
import csv
from pathlib import Path
from datetime import datetime
from loguru import logger

from src.scraper import TJSPScraper
from src.exporter import DataExporter


async def main():
    """Demonstração rápida da busca por parte"""
    logger.info("=== DEMONSTRAÇÃO RÁPIDA - BUSCA POR PARTE ===")

    # Buscar processos
    async with TJSPScraper() as scraper:
        logger.info("🔍 Buscando processos da parte: Parque Rio Nieva")

        processos = await scraper.search_by_party("Parque Rio Nieva")

        logger.success(f"✅ Encontrados {len(processos)} processos!")

        # Salvar lista em CSV
        output_dir = Path("./resultado_parque_rio_nieva")
        output_dir.mkdir(exist_ok=True)

        csv_path = output_dir / "lista_processos_parque_rio_nieva.csv"

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['processo_numero', 'etiqueta_opcional', 'data_coleta'])

            for processo in processos:
                writer.writerow([
                    processo,
                    'Parte: Parque Rio Nieva',
                    datetime.now().isoformat()
                ])

        logger.info(f"📄 Lista salva em: {csv_path}")

        # Mostrar primeiros 10 processos
        logger.info("📋 Primeiros 10 processos encontrados:")
        for i, proc in enumerate(processos[:10], 1):
            logger.info(f"  {i:2d}. {proc}")

        if len(processos) > 10:
            logger.info(f"   ... e mais {len(processos) - 10} processos")

        # Gerar relatório HTML simples
        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Processos - Parque Rio Nieva</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .stats {{ display: flex; gap: 20px; margin-bottom: 20px; }}
                .stat {{ background: #e8f4f8; padding: 10px; border-radius: 5px; }}
                .process-list {{ border: 1px solid #ddd; border-radius: 5px; }}
                .process-item {{ padding: 8px; border-bottom: 1px solid #eee; }}
                .process-item:nth-child(even) {{ background: #f9f9f9; }}
                .process-item:last-child {{ border-bottom: none; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Relatório de Processos</h1>
                <h2>Parte: Parque Rio Nieva</h2>
                <p>Coletado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            </div>

            <div class="stats">
                <div class="stat">
                    <strong>Total de Processos:</strong> {len(processos)}
                </div>
                <div class="stat">
                    <strong>Páginas Percorridas:</strong> 2
                </div>
                <div class="stat">
                    <strong>Método:</strong> Busca Automática por Parte
                </div>
            </div>

            <h3>📋 Lista Completa de Processos</h3>
            <div class="process-list">
        """

        for i, processo in enumerate(processos, 1):
            html_content += f'<div class="process-item">{i:2d}. {processo}</div>\n'

        html_content += """
            </div>
        </body>
        </html>
        """

        html_path = output_dir / "relatorio_parque_rio_nieva.html"
        html_path.write_text(html_content, encoding='utf-8')

        logger.success(f"🎨 Relatório HTML gerado: {html_path}")

        # Mostrar resumo
        logger.info("=" * 60)
        logger.info("🎯 RESUMO DA DEMONSTRAÇÃO")
        logger.info(f"   • Parte pesquisada: Parque Rio Nieva")
        logger.info(f"   • Processos encontrados: {len(processos)}")
        logger.info(f"   • Páginas percorridas: 2 (automático)")
        logger.info(f"   • Arquivos gerados: {csv_path.name}, {html_path.name}")
        logger.info(f"   • Localização: {output_dir}")
        logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
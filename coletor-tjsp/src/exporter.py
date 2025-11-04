"""
Exportador de dados para CSV, JSON e HTML
"""
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from jinja2 import Template
from loguru import logger

from .config import Config
from .keywords import Keywords


class DataExporter:
    """Exporta dados coletados em diversos formatos"""
    
    def __init__(self):
        self.config = Config()
    
    def export_to_csv(self, processos: List[Dict], output_dir: Optional[Path] = None):
        """
        Exporta dados para arquivos CSV
        
        Args:
            processos: Lista de processos com dados
            output_dir: Diretório de saída (opcional)
        """
        if not output_dir:
            output_dir = self.config.OUTPUT_DIR
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Preparar dados de processos
        processos_data = []
        movimentacoes_data = []
        
        for processo in processos:
            # Dados do processo
            proc_row = {
                'processo_numero': processo.get('processo_numero', ''),
                'vara': processo.get('vara', ''),
                'classe_assunto': processo.get('classe_assunto', ''),
                'valor_causa': processo.get('valor_causa', ''),
                'exequente': processo.get('exequente', ''),
                'executado': processo.get('executado', ''),
                'advogado_autor_nome': processo.get('advogado_autor_nome', ''),
                'advogado_autor_oab': processo.get('advogado_autor_oab', ''),
                'advogado_reu_nome': processo.get('advogado_reu_nome', ''),
                'advogado_reu_oab': processo.get('advogado_reu_oab', ''),
                'situacao': processo.get('situacao', ''),
                'etiqueta_opcional': processo.get('etiqueta_opcional', ''),
                'coleta_timestamp': processo.get('coleta_timestamp', '')
            }
            processos_data.append(proc_row)
            
            # Movimentações
            for mov in processo.get('movimentacoes', []):
                mov_row = {
                    'processo_numero': processo.get('processo_numero', ''),
                    'mov_ordem': mov.get('mov_ordem', ''),
                    'mov_data': mov.get('mov_data', ''),
                    'mov_texto': mov.get('mov_texto', ''),
                    'palavras_chave_detectadas': '|'.join(mov.get('palavras_chave_detectadas', [])),
                    'decisao_resultado': mov.get('decisao_resultado', ''),
                    'valor_bloqueado': mov.get('valor_bloqueado', ''),
                    'coleta_timestamp': mov.get('coleta_timestamp', '')
                }
                movimentacoes_data.append(mov_row)
        
        # Salvar CSVs
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Processos
        if processos_data:
            df_processos = pd.DataFrame(processos_data)
            processos_file = output_dir / f'processos_{timestamp}.csv'
            df_processos.to_csv(processos_file, index=False, encoding='utf-8-sig')
            logger.info(f"Processos exportados para: {processos_file}")
        
        # Movimentações
        if movimentacoes_data:
            df_movimentacoes = pd.DataFrame(movimentacoes_data)
            movimentacoes_file = output_dir / f'movimentacoes_{timestamp}.csv'
            df_movimentacoes.to_csv(movimentacoes_file, index=False, encoding='utf-8-sig')
            logger.info(f"Movimentações exportadas para: {movimentacoes_file}")
    
    def export_to_json(self, processos: List[Dict], output_dir: Optional[Path] = None):
        """
        Exporta dados para arquivo JSON
        
        Args:
            processos: Lista de processos com dados
            output_dir: Diretório de saída (opcional)
        """
        if not output_dir:
            output_dir = self.config.OUTPUT_DIR
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_file = output_dir / f'processos_{timestamp}.json'
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(processos, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"Dados exportados para JSON: {json_file}")
    
    def generate_analysis_report(self, processos: List[Dict]) -> Dict:
        """
        Gera relatório de análise estratégica
        
        Args:
            processos: Lista de processos com dados
            
        Returns:
            Dicionário com análise
        """
        analysis = {
            'total_processos': len(processos),
            'total_movimentacoes': 0,
            'medidas_constritivas': {
                'SISBAJUD': 0,
                'RENAJUD': 0,
                'INFOJUD': 0,
                'SERASAJUD': 0,
                'PENHORA': 0,
                'PROTESTO': 0
            },
            'decisoes': {
                'DEFERIDO': 0,
                'INDEFERIDO': 0,
                'PARCIAL': 0,
                'NAO_IDENTIFICADO': 0
            },
            'valores_bloqueados': [],
            'processos_com_acordo': 0,
            'processos_com_embargos': 0,
            'processos_com_excecao': 0,
            'advogados': {
                'autores': {},
                'reus': {}
            },
            'varas': {},
            'timeline': []
        }
        
        for processo in processos:
            # Contabilizar advogados
            adv_autor = processo.get('advogado_autor_nome', '')
            if adv_autor:
                analysis['advogados']['autores'][adv_autor] = \
                    analysis['advogados']['autores'].get(adv_autor, 0) + 1
            
            adv_reu = processo.get('advogado_reu_nome', '')
            if adv_reu:
                analysis['advogados']['reus'][adv_reu] = \
                    analysis['advogados']['reus'].get(adv_reu, 0) + 1
            
            # Contabilizar varas
            vara = processo.get('vara', '')
            if vara:
                analysis['varas'][vara] = analysis['varas'].get(vara, 0) + 1
            
            # Analisar movimentações
            tem_acordo = False
            tem_embargos = False
            tem_excecao = False
            
            for mov in processo.get('movimentacoes', []):
                analysis['total_movimentacoes'] += 1
                
                # Contabilizar palavras-chave
                for keyword in mov.get('palavras_chave_detectadas', []):
                    if keyword in analysis['medidas_constritivas']:
                        analysis['medidas_constritivas'][keyword] += 1
                    
                    if keyword == 'ACORDO':
                        tem_acordo = True
                    elif keyword == 'EMBARGOS':
                        tem_embargos = True
                    elif keyword == 'EXCECAO_PRE':
                        tem_excecao = True
                
                # Contabilizar decisões
                decisao = mov.get('decisao_resultado', 'NAO_IDENTIFICADO')
                analysis['decisoes'][decisao] += 1
                
                # Coletar valores bloqueados
                valor = mov.get('valor_bloqueado', '')
                if valor:
                    analysis['valores_bloqueados'].append({
                        'processo': processo.get('processo_numero', ''),
                        'valor': valor,
                        'data': mov.get('mov_data', '')
                    })
                
                # Timeline de eventos importantes
                if mov.get('palavras_chave_detectadas'):
                    analysis['timeline'].append({
                        'processo': processo.get('processo_numero', ''),
                        'data': mov.get('mov_data', ''),
                        'evento': '|'.join(mov.get('palavras_chave_detectadas', [])),
                        'decisao': decisao
                    })
            
            if tem_acordo:
                analysis['processos_com_acordo'] += 1
            if tem_embargos:
                analysis['processos_com_embargos'] += 1
            if tem_excecao:
                analysis['processos_com_excecao'] += 1
        
        # Calcular estatísticas
        if analysis['total_movimentacoes'] > 0:
            total_decisoes = sum(analysis['decisoes'].values()) - analysis['decisoes']['NAO_IDENTIFICADO']
            if total_decisoes > 0:
                analysis['taxa_deferimento'] = \
                    f"{(analysis['decisoes']['DEFERIDO'] / total_decisoes * 100):.1f}%"
        
        # Ordenar timeline por data
        analysis['timeline'].sort(key=lambda x: x['data'])
        
        return analysis
    
    def export_html_dashboard(self, processos: List[Dict], output_dir: Optional[Path] = None):
        """
        Gera dashboard HTML com análise visual
        
        Args:
            processos: Lista de processos com dados
            output_dir: Diretório de saída (opcional)
        """
        if not output_dir:
            output_dir = self.config.OUTPUT_DIR
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        analysis = self.generate_analysis_report(processos)
        
        # Template HTML
        html_template = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Análise de Processos TJSP</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { color: #333; margin-bottom: 30px; text-align: center; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card h2 { color: #555; font-size: 18px; margin-bottom: 15px; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .stat { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; }
        .stat:last-child { border-bottom: none; }
        .stat-label { color: #666; }
        .stat-value { font-weight: bold; color: #333; }
        .success { color: #28a745; }
        .danger { color: #dc3545; }
        .warning { color: #ffc107; }
        .info { color: #17a2b8; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: 600; color: #555; }
        tr:hover { background: #f8f9fa; }
        .timeline { max-height: 400px; overflow-y: auto; }
        .timeline-item { padding: 10px; border-left: 3px solid #007bff; margin-bottom: 10px; background: #f8f9fa; }
        .timeline-date { font-size: 12px; color: #666; }
        .timeline-event { margin-top: 5px; font-weight: 500; }
        .badge { display: inline-block; padding: 3px 8px; border-radius: 12px; font-size: 12px; margin: 2px; }
        .badge-success { background: #d4edda; color: #155724; }
        .badge-danger { background: #f8d7da; color: #721c24; }
        .badge-warning { background: #fff3cd; color: #856404; }
        .badge-info { background: #d1ecf1; color: #0c5460; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Dashboard - Análise de Processos TJSP</h1>
        <p style="text-align: center; color: #666; margin-bottom: 30px;">
            Gerado em: {{ timestamp }}
        </p>
        
        <div class="grid">
            <!-- Resumo Geral -->
            <div class="card">
                <h2>📈 Resumo Geral</h2>
                <div class="stat">
                    <span class="stat-label">Total de Processos:</span>
                    <span class="stat-value">{{ analysis.total_processos }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Total de Movimentações:</span>
                    <span class="stat-value">{{ analysis.total_movimentacoes }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Processos com Acordo:</span>
                    <span class="stat-value success">{{ analysis.processos_com_acordo }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Processos com Embargos:</span>
                    <span class="stat-value warning">{{ analysis.processos_com_embargos }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Processos com Exceção:</span>
                    <span class="stat-value warning">{{ analysis.processos_com_excecao }}</span>
                </div>
            </div>
            
            <!-- Medidas Constritivas -->
            <div class="card">
                <h2>🔒 Medidas Constritivas</h2>
                {% for medida, count in analysis.medidas_constritivas.items() %}
                {% if count > 0 %}
                <div class="stat">
                    <span class="stat-label">{{ medida }}:</span>
                    <span class="stat-value {% if count > 10 %}danger{% elif count > 5 %}warning{% else %}info{% endif %}">
                        {{ count }}
                    </span>
                </div>
                {% endif %}
                {% endfor %}
            </div>
            
            <!-- Decisões -->
            <div class="card">
                <h2>⚖️ Análise de Decisões</h2>
                <div class="stat">
                    <span class="stat-label">Deferidas:</span>
                    <span class="stat-value success">{{ analysis.decisoes.DEFERIDO }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Indeferidas:</span>
                    <span class="stat-value danger">{{ analysis.decisoes.INDEFERIDO }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Parciais:</span>
                    <span class="stat-value warning">{{ analysis.decisoes.PARCIAL }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Não Identificadas:</span>
                    <span class="stat-value">{{ analysis.decisoes.NAO_IDENTIFICADO }}</span>
                </div>
                {% if analysis.taxa_deferimento %}
                <div class="stat" style="margin-top: 10px; padding-top: 10px; border-top: 2px solid #007bff;">
                    <span class="stat-label"><strong>Taxa de Deferimento:</strong></span>
                    <span class="stat-value success"><strong>{{ analysis.taxa_deferimento }}</strong></span>
                </div>
                {% endif %}
            </div>
        </div>
        
        <!-- Valores Bloqueados -->
        {% if analysis.valores_bloqueados %}
        <div class="card">
            <h2>💰 Valores Bloqueados</h2>
            <table>
                <thead>
                    <tr>
                        <th>Processo</th>
                        <th>Data</th>
                        <th>Valor</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in analysis.valores_bloqueados[:10] %}
                    <tr>
                        <td>{{ item.processo }}</td>
                        <td>{{ item.data }}</td>
                        <td class="success"><strong>{{ item.valor }}</strong></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
        
        <!-- Timeline de Eventos -->
        {% if analysis.timeline %}
        <div class="card">
            <h2>📅 Timeline de Eventos Importantes</h2>
            <div class="timeline">
                {% for evento in analysis.timeline[:50] %}
                <div class="timeline-item">
                    <div class="timeline-date">{{ evento.data }} - {{ evento.processo }}</div>
                    <div class="timeline-event">
                        {% for keyword in evento.evento.split('|') %}
                        <span class="badge badge-info">{{ keyword }}</span>
                        {% endfor %}
                        {% if evento.decisao != 'NAO_IDENTIFICADO' %}
                        <span class="badge {% if evento.decisao == 'DEFERIDO' %}badge-success{% elif evento.decisao == 'INDEFERIDO' %}badge-danger{% else %}badge-warning{% endif %}">
                            {{ evento.decisao }}
                        </span>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        
        <div class="grid">
            <!-- Top Advogados Autores -->
            {% if analysis.advogados.autores %}
            <div class="card">
                <h2>👨‍⚖️ Top Advogados (Autores)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Advogado</th>
                            <th>Processos</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for adv, count in analysis.advogados.autores.items()[:10] %}
                        <tr>
                            <td>{{ adv }}</td>
                            <td>{{ count }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% endif %}
            
            <!-- Top Varas -->
            {% if analysis.varas %}
            <div class="card">
                <h2>🏛️ Distribuição por Vara</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Vara</th>
                            <th>Processos</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for vara, count in analysis.varas.items()[:10] %}
                        <tr>
                            <td>{{ vara }}</td>
                            <td>{{ count }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
        """
        
        # Renderizar template
        template = Template(html_template)
        html_content = template.render(
            analysis=analysis,
            timestamp=datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        )
        
        # Salvar arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_file = output_dir / f'dashboard_{timestamp}.html'
        html_file.write_text(html_content, encoding='utf-8')
        
        logger.info(f"Dashboard HTML gerado: {html_file}")
        
        # Também salvar análise em JSON
        json_file = output_dir / f'analise_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"Análise JSON salva: {json_file}")

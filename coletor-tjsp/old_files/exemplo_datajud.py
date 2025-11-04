#!/usr/bin/env python3
"""
Exemplo prático de uso da API DataJud (CNJ)
Consulta processos jurídicos públicos sem necessidade de ser advogado
"""
import requests
import json
from datetime import datetime
from typing import Optional, Dict, List

class DataJudAPI:
    """Cliente para API Pública do DataJud (CNJ)"""
    
    # Chave pública oficial do CNJ (disponível em: https://datajud-wiki.cnj.jus.br/api-publica/acesso/)
    API_KEY = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
    BASE_URL = "https://api-publica.datajud.cnj.jus.br"
    
    def __init__(self, tribunal: str = 'tjsp'):
        """
        Inicializa cliente da API
        
        Args:
            tribunal: Sigla do tribunal (tjsp, tjrj, trf3, etc.)
        """
        self.tribunal = tribunal
        self.endpoint = f"{self.BASE_URL}/api_publica_{tribunal}/_search"
        self.headers = {
            'Authorization': f'APIKey {self.API_KEY}',
            'Content-Type': 'application/json'
        }
    
    def _limpar_numero_processo(self, numero: str) -> str:
        """Remove formatação do número do processo"""
        return numero.replace('-', '').replace('.', '').replace(' ', '')
    
    def consultar_por_numero(self, numero_processo: str) -> Optional[Dict]:
        """
        Consulta processo por número CNJ
        
        Args:
            numero_processo: Número do processo (ex: '1000032-02.2024.8.26.0100')
        
        Returns:
            Dados do processo ou None se não encontrado
        """
        numero_limpo = self._limpar_numero_processo(numero_processo)
        
        query = {
            "query": {
                "match": {
                    "numeroProcesso": numero_limpo
                }
            }
        }
        
        try:
            print(f"Consultando processo {numero_processo}...")
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=query,
                timeout=30
            )
            
            if response.status_code == 200:
                dados = response.json()
                hits = dados.get('hits', {}).get('hits', [])
                
                if hits:
                    return self._processar_resultado(hits[0]['_source'])
                else:
                    print(f"⚠️ Processo {numero_processo} não encontrado")
                    return None
            else:
                print(f"❌ Erro HTTP {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na requisição: {e}")
            return None
    
    def consultar_por_parte(self, nome_parte: str, max_resultados: int = 10) -> List[Dict]:
        """
        Busca processos por nome da parte
        
        Args:
            nome_parte: Nome da parte (pessoa física ou jurídica)
            max_resultados: Número máximo de resultados
        
        Returns:
            Lista de processos encontrados
        """
        query = {
            "query": {
                "match": {
                    "nome": nome_parte
                }
            },
            "size": max_resultados
        }
        
        try:
            print(f"Buscando processos de '{nome_parte}'...")
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=query,
                timeout=30
            )
            
            if response.status_code == 200:
                dados = response.json()
                hits = dados.get('hits', {}).get('hits', [])
                
                if hits:
                    processos = [self._processar_resultado(hit['_source']) for hit in hits]
                    print(f"✅ {len(processos)} processos encontrados")
                    return processos
                else:
                    print(f"⚠️ Nenhum processo encontrado para '{nome_parte}'")
                    return []
            else:
                print(f"❌ Erro HTTP {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na requisição: {e}")
            return []
    
    def _processar_resultado(self, processo: Dict) -> Dict:
        """Processa e estrutura dados do processo"""
        return {
            'numero': processo.get('numeroProcesso'),
            'classe': processo.get('classe', {}).get('nome'),
            'assunto': processo.get('assunto', [{}])[0].get('nome') if processo.get('assunto') else None,
            'orgao_julgador': processo.get('orgaoJulgador', {}).get('nome'),
            'data_ajuizamento': processo.get('dataAjuizamento'),
            'data_ultima_atualizacao': processo.get('dataHoraUltimaAtualizacao'),
            'sistema': processo.get('sistema', {}).get('nome'),
            'grau': processo.get('grau'),
            'tribunal': processo.get('siglaTribunal'),
            'movimentacoes': len(processo.get('movimentos', [])),
            'dados_completos': processo
        }
    
    def salvar_json(self, dados: Dict, nome_arquivo: Optional[str] = None):
        """Salva dados em arquivo JSON"""
        if not nome_arquivo:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_arquivo = f'processo_datajud_{timestamp}.json'
        
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Dados salvos em: {nome_arquivo}")


def exemplo_consulta_numero():
    """Exemplo: Consultar processo por número"""
    print("=" * 70)
    print("EXEMPLO 1: CONSULTA POR NÚMERO DE PROCESSO")
    print("=" * 70)
    
    api = DataJudAPI('tjsp')
    
    # Exemplo com número de processo real (substitua por um número válido)
    numero = '1000032-02.2024.8.26.0100'
    resultado = api.consultar_por_numero(numero)
    
    if resultado:
        print("\n✅ PROCESSO ENCONTRADO:")
        print(f"   Número: {resultado['numero']}")
        print(f"   Classe: {resultado['classe']}")
        print(f"   Assunto: {resultado['assunto']}")
        print(f"   Órgão: {resultado['orgao_julgador']}")
        print(f"   Data Ajuizamento: {resultado['data_ajuizamento']}")
        print(f"   Movimentações: {resultado['movimentacoes']}")
        print(f"   Sistema: {resultado['sistema']}")
        
        # Salvar dados completos
        api.salvar_json(resultado, 'processo_exemplo.json')
    
    print("\n" + "=" * 70)


def exemplo_consulta_parte():
    """Exemplo: Buscar processos por nome da parte"""
    print("\n" + "=" * 70)
    print("EXEMPLO 2: BUSCA POR NOME DA PARTE")
    print("=" * 70)
    
    api = DataJudAPI('tjsp')
    
    # Buscar processos de um condomínio (exemplo)
    nome = 'Condominio Edificio'
    processos = api.consultar_por_parte(nome, max_resultados=5)
    
    if processos:
        print(f"\n✅ {len(processos)} PROCESSOS ENCONTRADOS:\n")
        
        for i, proc in enumerate(processos, 1):
            print(f"{i}. Processo: {proc['numero']}")
            print(f"   Classe: {proc['classe']}")
            print(f"   Órgão: {proc['orgao_julgador']}")
            print(f"   Data: {proc['data_ajuizamento']}")
            print()
        
        # Salvar todos os processos
        api.salvar_json({'total': len(processos), 'processos': processos}, 'processos_parte.json')
    
    print("=" * 70)


def exemplo_comparacao_tribunais():
    """Exemplo: Consultar mesmo processo em tribunais diferentes"""
    print("\n" + "=" * 70)
    print("EXEMPLO 3: COMPARAÇÃO ENTRE TRIBUNAIS")
    print("=" * 70)
    
    tribunais = ['tjsp', 'tjrj', 'trf3']
    
    for tribunal in tribunais:
        print(f"\n🔍 Testando {tribunal.upper()}...")
        api = DataJudAPI(tribunal)
        
        # Fazer uma busca genérica
        query = {
            "query": {
                "match_all": {}
            },
            "size": 1
        }
        
        try:
            response = requests.post(
                api.endpoint,
                headers=api.headers,
                json=query,
                timeout=10
            )
            
            if response.status_code == 200:
                dados = response.json()
                total = dados.get('hits', {}).get('total', {}).get('value', 0)
                print(f"   ✅ {tribunal.upper()}: {total:,} processos disponíveis")
            else:
                print(f"   ⚠️ {tribunal.upper()}: Erro {response.status_code}")
        
        except Exception as e:
            print(f"   ❌ {tribunal.upper()}: {e}")
    
    print("\n" + "=" * 70)


def main():
    """Função principal"""
    print("\n🔍 EXEMPLOS DE USO DA API DATAJUD (CNJ)")
    print("Consulta de processos jurídicos públicos - SEM necessidade de ser advogado\n")
    
    # Exemplo 1: Consulta por número
    exemplo_consulta_numero()

    # Exemplo 2: Busca por parte
    exemplo_consulta_parte()  # Agora testando

    # Exemplo 3: Comparação de tribunais
    exemplo_comparacao_tribunais()  # Agora testando
    
    print("\n✅ Exemplos concluídos!")
    print("\n📚 Documentação completa:")
    print("   https://datajud-wiki.cnj.jus.br/api-publica/")
    print("\n⚖️ Legalidade:")
    print("   ✅ 100% Legal - API pública do CNJ")
    print("   ✅ Não requer ser advogado")
    print("   ✅ Acesso gratuito e sem cadastro")
    print("   ✅ Dados públicos conforme Lei de Acesso à Informação")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExecução interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()

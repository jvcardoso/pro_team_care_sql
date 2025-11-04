"""
Definições de palavras-chave e regras de classificação
"""
from typing import List, Dict, Set
import re

class Keywords:
    """Gerenciador de palavras-chave e classificações"""
    
    # --- PALAVRAS-CHAVE PARA DETECÇÃO ---
    KEYWORDS_MAP = {
        "SISBAJUD": [
            "sisbajud", "bacenjud", "bacen jud", "sistema bacen",
            "bloqueio judicial", "bloqueio de valores", "bloqueio online"
        ],
        "RENAJUD": [
            "renajud", "restrição de veículos", "bloqueio de veículos",
            "restrição veicular", "detran"
        ],
        "INFOJUD": [
            "infojud", "info jud", "receita federal", "declaração de renda",
            "informações fiscais", "dados fiscais"
        ],
        "SERASAJUD": [
            "serasajud", "serasa jud", "serasa", "inclusão serasa",
            "negativação", "restrição de crédito"
        ],
        "PROTESTO": [
            "protesto", "cartório de protesto", "protesto de título",
            "protesto judicial", "certidão de protesto"
        ],
        "PENHORA": [
            "penhora", "constrição", "indisponibilidade", "bloqueio de bens",
            "arresto", "sequestro de bens", "apreensão judicial"
        ],
        "ARRESTO": [
            "arresto", "arresto de bens", "arresto online",
            "medida cautelar de arresto"
        ],
        "BLOQUEIO": [
            "bloqueio", "constrição online", "bloqueio de ativos",
            "bloqueio de conta", "indisponibilidade de bens"
        ],
        "DESBLOQUEIO": [
            "desbloqueio", "liberação", "levantamento de constrição",
            "liberação de valores", "desbloqueio de conta"
        ],
        "EMBARGOS": [
            "embargos", "embargos à execução", "embargos do devedor",
            "embargos de terceiro", "impugnação ao cumprimento"
        ],
        "EXCECAO_PRE": [
            "exceção de pré-executividade", "exceção de pré executividade",
            "excecao de pre-executividade", "exceção pré-executividade",
            "objeção de pré-executividade"
        ],
        "ACORDO": [
            "acordo", "composição", "transação", "parcelamento",
            "negociação", "conciliação", "mediação", "autocomposição"
        ],
        "CITACAO": [
            "citação", "citado", "citar", "mandado de citação",
            "carta de citação", "citação por edital", "AR citação"
        ],
        "INTIMACAO": [
            "intimação", "intimado", "intimar", "mandado de intimação",
            "carta de intimação", "intimação pessoal"
        ]
    }
    
    # --- REGRAS PARA CLASSIFICAÇÃO DE DECISÃO ---
    DECISION_RULES = {
        "DEFERIDO": [
            r"\bdefir[oi]\b", r"\bdeferid[oa]s?\b",
            r"\bdetermin[eo]-?se\b", r"\bexpeç[ao]-?se\b",
            r"\brealize-?se\b", r"\bproceda-?se\b",
            r"\bacolh[eo]\b(?!.*\bnão\b)", r"\bautorizo\b",
            r"\bconcedo\b", r"\bdefiro\s+o\s+pedido\b"
        ],
        "INDEFERIDO": [
            r"\bindefir[oi]\b", r"\bindeferid[oa]s?\b",
            r"\bnão\s+acolh[eo]\b", r"\binacolh[eo]\b",
            r"\binviável\b", r"\bimprocedente\b",
            r"\brejeit[oa]\b", r"\bnego\b(?!ciação)",
            r"\bindeferimento\b", r"\bimpossibilidade\b"
        ],
        "PARCIAL": [
            r"\bparcialmente\b", r"\bem\s+parte\b",
            r"\bparcial\b", r"\bdefiro\s+em\s+parte\b",
            r"\bacolho\s+parcialmente\b"
        ]
    }
    
    # --- REGEX PARA EXTRAÇÃO DE VALORES ---
    VALUE_REGEX = re.compile(
        r'R\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
        re.IGNORECASE
    )
    
    # --- REGEX PARA DATAS ---
    DATE_REGEX = re.compile(
        r'\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})\b'
    )
    
    @classmethod
    def detect_keywords(cls, text: str) -> List[str]:
        """
        Detecta palavras-chave no texto
        
        Args:
            text: Texto para análise
            
        Returns:
            Lista de palavras-chave detectadas
        """
        if not text:
            return []
        
        text_lower = text.lower()
        detected = []
        
        for keyword, variations in cls.KEYWORDS_MAP.items():
            for variation in variations:
                if variation in text_lower:
                    detected.append(keyword)
                    break  # Uma variação encontrada é suficiente
        
        return list(set(detected))  # Remove duplicatas
    
    @classmethod
    def classify_decision(cls, text: str) -> str:
        """
        Classifica o resultado de uma decisão
        
        Args:
            text: Texto da decisão
            
        Returns:
            DEFERIDO, INDEFERIDO, PARCIAL ou NAO_IDENTIFICADO
        """
        if not text:
            return "NAO_IDENTIFICADO"
        
        text_lower = text.lower()
        
        # Verifica primeiro PARCIAL (mais específico)
        for pattern in cls.DECISION_RULES["PARCIAL"]:
            if re.search(pattern, text_lower):
                return "PARCIAL"
        
        # Depois INDEFERIDO
        for pattern in cls.DECISION_RULES["INDEFERIDO"]:
            if re.search(pattern, text_lower):
                return "INDEFERIDO"
        
        # Por fim DEFERIDO
        for pattern in cls.DECISION_RULES["DEFERIDO"]:
            if re.search(pattern, text_lower):
                return "DEFERIDO"
        
        return "NAO_IDENTIFICADO"
    
    @classmethod
    def extract_values(cls, text: str) -> List[str]:
        """
        Extrai valores monetários do texto
        
        Args:
            text: Texto para extração
            
        Returns:
            Lista de valores encontrados
        """
        if not text:
            return []
        
        matches = cls.VALUE_REGEX.findall(text)
        return [f"R$ {match}" for match in matches]
    
    @classmethod
    def extract_dates(cls, text: str) -> List[str]:
        """
        Extrai datas do texto
        
        Args:
            text: Texto para extração
            
        Returns:
            Lista de datas encontradas
        """
        if not text:
            return []
        
        matches = cls.DATE_REGEX.findall(text)
        dates = []
        
        for day, month, year in matches:
            # Padroniza ano para 4 dígitos
            if len(year) == 2:
                year = f"20{year}" if int(year) < 50 else f"19{year}"
            dates.append(f"{day.zfill(2)}/{month.zfill(2)}/{year}")
        
        return dates
    
    @classmethod
    def is_sensitive_movement(cls, text: str) -> bool:
        """
        Verifica se a movimentação contém informações sensíveis
        
        Args:
            text: Texto da movimentação
            
        Returns:
            True se contém informações sensíveis
        """
        sensitive_keywords = [
            "SISBAJUD", "RENAJUD", "INFOJUD", "SERASAJUD",
            "PENHORA", "BLOQUEIO", "ARRESTO"
        ]
        
        detected = cls.detect_keywords(text)
        return any(kw in sensitive_keywords for kw in detected)
    
    @classmethod
    def get_movement_priority(cls, keywords: List[str]) -> int:
        """
        Define prioridade da movimentação baseada nas palavras-chave
        
        Args:
            keywords: Lista de palavras-chave detectadas
            
        Returns:
            Prioridade (1-5, sendo 5 a mais alta)
        """
        if not keywords:
            return 1
        
        # Alta prioridade
        high_priority = {"SISBAJUD", "RENAJUD", "INFOJUD", "PENHORA", "BLOQUEIO"}
        if any(kw in high_priority for kw in keywords):
            return 5
        
        # Média-alta prioridade
        medium_high = {"ACORDO", "EMBARGOS", "EXCECAO_PRE"}
        if any(kw in medium_high for kw in keywords):
            return 4
        
        # Média prioridade
        medium = {"CITACAO", "INTIMACAO", "PROTESTO"}
        if any(kw in medium for kw in keywords):
            return 3
        
        # Baixa prioridade
        return 2

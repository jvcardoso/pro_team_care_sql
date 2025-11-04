"""
Testes para o módulo de palavras-chave
"""
import pytest
from src.keywords import Keywords


class TestKeywordsDetection:
    """Testes de detecção de palavras-chave"""
    
    def test_detect_sisbajud(self):
        """Testa detecção de SISBAJUD e variações"""
        texts = [
            "Determinei o bloqueio via SISBAJUD",
            "Consulta ao sistema BacenJud realizada",
            "Bloqueio online de valores determinado",
            "Bloqueio judicial de contas bancárias"
        ]
        
        for text in texts:
            keywords = Keywords.detect_keywords(text)
            assert "SISBAJUD" in keywords
    
    def test_detect_renajud(self):
        """Testa detecção de RENAJUD"""
        text = "Procedi à restrição de veículos via RENAJUD"
        keywords = Keywords.detect_keywords(text)
        assert "RENAJUD" in keywords
    
    def test_detect_multiple_keywords(self):
        """Testa detecção de múltiplas palavras-chave"""
        text = """
        Defiro o pedido de penhora online via SISBAJUD.
        Caso infrutífera, proceda-se à consulta RENAJUD e INFOJUD.
        """
        keywords = Keywords.detect_keywords(text)
        
        assert "SISBAJUD" in keywords
        assert "RENAJUD" in keywords
        assert "INFOJUD" in keywords
        assert "PENHORA" in keywords
    
    def test_no_keywords(self):
        """Testa texto sem palavras-chave"""
        text = "Audiência de conciliação designada para 15/03/2024"
        keywords = Keywords.detect_keywords(text)
        assert len(keywords) == 0


class TestDecisionClassification:
    """Testes de classificação de decisões"""
    
    def test_deferido(self):
        """Testa classificação DEFERIDO"""
        texts = [
            "Defiro o pedido de bloqueio",
            "Pedido deferido nos termos requeridos",
            "Determine-se a expedição de mandado",
            "Expeça-se o necessário",
            "Acolho o pedido formulado"
        ]
        
        for text in texts:
            result = Keywords.classify_decision(text)
            assert result == "DEFERIDO", f"Falhou para: {text}"
    
    def test_indeferido(self):
        """Testa classificação INDEFERIDO"""
        texts = [
            "Indefiro o pedido por falta de provas",
            "Não acolho a pretensão",
            "Pedido indeferido",
            "Rejeito os embargos",
            "Nego provimento ao recurso"
        ]
        
        for text in texts:
            result = Keywords.classify_decision(text)
            assert result == "INDEFERIDO", f"Falhou para: {text}"
    
    def test_parcial(self):
        """Testa classificação PARCIAL"""
        texts = [
            "Defiro parcialmente o pedido",
            "Acolho em parte a pretensão",
            "Pedido parcialmente deferido"
        ]
        
        for text in texts:
            result = Keywords.classify_decision(text)
            assert result == "PARCIAL", f"Falhou para: {text}"
    
    def test_nao_identificado(self):
        """Testa classificação NAO_IDENTIFICADO"""
        texts = [
            "Aguarde-se manifestação das partes",
            "Vista ao Ministério Público",
            "Certifique a serventia"
        ]
        
        for text in texts:
            result = Keywords.classify_decision(text)
            assert result == "NAO_IDENTIFICADO"


class TestValueExtraction:
    """Testes de extração de valores"""
    
    def test_extract_single_value(self):
        """Testa extração de valor único"""
        text = "Bloqueio realizado no valor de R$ 1.234,56"
        values = Keywords.extract_values(text)
        
        assert len(values) == 1
        assert values[0] == "R$ 1.234,56"
    
    def test_extract_multiple_values(self):
        """Testa extração de múltiplos valores"""
        text = """
        Valor principal: R$ 10.000,00
        Multa: R$ 1.000,00
        Honorários: R$ 2.000,00
        """
        values = Keywords.extract_values(text)
        
        assert len(values) == 3
        assert "R$ 10.000,00" in values
        assert "R$ 1.000,00" in values
        assert "R$ 2.000,00" in values
    
    def test_extract_large_values(self):
        """Testa extração de valores grandes"""
        text = "Valor da causa: R$ 1.234.567,89"
        values = Keywords.extract_values(text)
        
        assert len(values) == 1
        assert values[0] == "R$ 1.234.567,89"
    
    def test_no_values(self):
        """Testa texto sem valores"""
        text = "Intimem-se as partes"
        values = Keywords.extract_values(text)
        assert len(values) == 0


class TestDateExtraction:
    """Testes de extração de datas"""
    
    def test_extract_dates(self):
        """Testa extração de datas"""
        text = "Audiência designada para 15/03/2024 às 14h"
        dates = Keywords.extract_dates(text)
        
        assert len(dates) == 1
        assert dates[0] == "15/03/2024"
    
    def test_extract_multiple_dates(self):
        """Testa extração de múltiplas datas"""
        text = """
        Prazo de 05/03/2024 a 20/03/2024
        Próxima audiência em 10/04/2024
        """
        dates = Keywords.extract_dates(text)
        
        assert len(dates) == 3
        assert "05/03/2024" in dates
        assert "20/03/2024" in dates
        assert "10/04/2024" in dates
    
    def test_date_formats(self):
        """Testa diferentes formatos de data"""
        texts = [
            ("Data: 01/01/2024", "01/01/2024"),
            ("Data: 1/1/2024", "01/01/2024"),
            ("Data: 01-01-2024", "01/01/2024"),
            ("Data: 01.01.2024", "01/01/2024")
        ]
        
        for text, expected in texts:
            dates = Keywords.extract_dates(text)
            assert len(dates) == 1
            assert dates[0] == expected


class TestMovementPriority:
    """Testes de prioridade de movimentações"""
    
    def test_high_priority(self):
        """Testa movimentações de alta prioridade"""
        keywords = ["SISBAJUD", "PENHORA"]
        priority = Keywords.get_movement_priority(keywords)
        assert priority == 5
    
    def test_medium_high_priority(self):
        """Testa movimentações de média-alta prioridade"""
        keywords = ["ACORDO", "EMBARGOS"]
        priority = Keywords.get_movement_priority(keywords)
        assert priority == 4
    
    def test_medium_priority(self):
        """Testa movimentações de média prioridade"""
        keywords = ["CITACAO", "INTIMACAO"]
        priority = Keywords.get_movement_priority(keywords)
        assert priority == 3
    
    def test_low_priority(self):
        """Testa movimentações de baixa prioridade"""
        keywords = ["DESBLOQUEIO"]
        priority = Keywords.get_movement_priority(keywords)
        assert priority == 2
    
    def test_no_keywords_priority(self):
        """Testa prioridade sem palavras-chave"""
        keywords = []
        priority = Keywords.get_movement_priority(keywords)
        assert priority == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

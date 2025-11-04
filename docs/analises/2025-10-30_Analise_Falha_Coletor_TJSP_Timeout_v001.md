# Análise de Falha - Coletor TJSP por Timeout

**Data:** 2025-10-30 21:00
**Versão:** v001
**Autor:** Gemini
**Revisão de:** N/A
**Motivo da revisão:** N/A

## Histórico de Versões
- v001 (2025-10-30): Versão inicial da análise sobre a falha de timeout na execução do workflow.

## 1. Objetivo
Analisar a causa raiz da interrupção do script `workflow_rio_nieva.py` durante a extração em lote de 29 processos, que foi interrompido no 13º processo. O objetivo é fornecer um diagnóstico claro e propor soluções para garantir que o script possa ser executado completamente sem atingir limites de tempo.

## 2. Metodologia
Para esta análise, foram aplicados os seguintes métodos:
- **Análise Forense de Logs:** Investigação dos logs de execução para reconstruir a sequência de eventos e os tempos de cada etapa.
- **Método dos 5 Porquês:** Utilizado para aprofundar na causa raiz do problema a partir do sintoma inicial (o timeout).
- **Análise Diferencial:** Comparação entre o resultado esperado (29 processos extraídos) e o resultado obtido (12 processos completos e falha no 13º).

## 3. Resultados da Análise (Diagnóstico)

A investigação, baseada nos logs e no resumo da execução, revelou o seguinte:

1.  **Por que a execução falhou?**
    - A execução foi interrompida por um **limite de tempo (timeout) de 10 minutos** imposto pela plataforma ou ambiente de execução.

2.  **Por que o timeout foi atingido?**
    - O tempo total para processar os 13 primeiros itens excedeu os 10 minutos.
    - **Cálculo de tempo:**
        - **Passo 1 (Busca inicial):** ~1.5 minutos.
        - **Passo 2 (Extração de 12 processos):** 12 processos * ~45 segundos/processo = 540 segundos = 9 minutos.
        - **Tempo Total Estimado até a falha:** 1.5 min + 9 min = **10.5 minutos**.
    - Este cálculo confirma que o tempo de execução é totalmente consistente com o acionamento de um timeout de 10 minutos.

3.  **Por que o processamento é tão lento?**
    - O script processa os 29 processos de forma **sequencial** (um de cada vez).
    - Cada extração individual contém pausas deliberadas e longas (`Aguardando X segundos...`) para evitar o bloqueio pelo site do TJSP.

4.  **Conclusão da Causa Raiz:**
    - A estratégia de execução **sequencial é inerentemente lenta demais** para completar o lote de 29 processos dentro do limite de 10 minutos. O problema não é um erro no código de extração (que funciona para cada item individual), mas sim uma **incompatibilidade entre a arquitetura de execução do script e as restrições da plataforma**.

## 4. Conclusões

- A lógica de extração de dados está **correta e funcional**, conforme validado pelos 12 processos salvos com sucesso.
- A falha é um **problema de performance e arquitetura**, não um bug de funcionalidade.
- Manter a abordagem sequencial tornará o script inutilizável para qualquer lote que demore mais de 10 minutos para ser processado.

## 5. Próximos Passos (Plano de Ação)

Para garantir que o coletor seja robusto e finalize seu trabalho, as seguintes soluções são propostas, em ordem de prioridade:

### Solução 1: Implementação de Paralelismo (Recomendado)

Esta é a solução definitiva, pois ataca a causa raiz do problema (a lentidão).

- **Ação:** Modificar o `workflow_rio_nieva.py` para processar a lista de processos em paralelo, utilizando um número controlado de "workers" (threads ou processos).
- **Limite Seguro:** Iniciar com **3 workers paralelos**.
- **Impacto Esperado:** Redução do tempo total de ~22 minutos para **~7-8 minutos**, o que resolve confortavelmente o problema do timeout de 10 minutos.
- **Vantagem:** Torna o script escalável e robusto para lotes de tamanhos variados.

### Solução 2: Execução em Lotes (Contorno)

Esta é uma solução de contorno, que não resolve a lentidão, mas evita o timeout.

- **Ação:** Manter o script como está, mas orquestrar sua execução em lotes menores que caibam no limite de tempo.
- **Exemplo de Execução:**
  ```bash
  # Lote 1
  python workflow_rio_nieva.py --start 1 --end 12
  # Lote 2
  python workflow_rio_nieva.py --start 13 --end 24
  # Lote 3
  python workflow_rio_nieva.py --start 25 --end 29
  ```
- **Vantagem:** Não exige alteração no código principal.
- **Desvantagem:** É uma solução manual, menos elegante e que não resolve o problema fundamental de performance.

**Recomendação final para o desenvolvedor:** Priorizar a **Solução 1 (Paralelismo)** para garantir a eficiência e a confiabilidade do coletor a longo prazo.

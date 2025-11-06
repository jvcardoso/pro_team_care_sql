# Análise de Sistema - Painel de BI do Kanban

**Data:** 2025-11-05 14:30
**Versão:** v001
**Autor:** Gemini
**Revisão de:** N/A
**Motivo da revisão:** N/A

## Histórico de Versões
- v001 (2025-11-05): Criação do documento inicial para a arquitetura do painel de BI do Kanban.

## 1. Objetivo
Definir a arquitetura de banco de dados para a criação de um painel de Business Intelligence (BI) focado na análise de dados do quadro Kanban. O objetivo é centralizar toda a lógica de cálculo de métricas e KPIs no SQL Server 2025, seguindo o padrão "Database-First Presentation". A solução deve fornecer dados pré-processados para a aplicação, garantindo alta performance, consistência e flexibilidade para filtros de data.

## 2. Metodologia
A análise foi conduzida utilizando os seguintes métodos, com foco na criação de uma solução robusta e performática:
- **Systematic Investigation:** Análise da estrutura de dados existente (`Cards`, `CardColumns`, `CardMovements`) para definir a melhor forma de consolidar as informações.
- **Differential Analysis:** Comparação entre processar os dados na aplicação vs. no banco de dados, validando a superioridade da abordagem Database-First para este caso.
- **Forensic Analysis:** Estudo de como os movimentos dos cards (`CardMovements`) podem ser usados para reconstruir o histórico e calcular tempos de permanência em cada estágio.
- **5 Whys Method:** Utilizado para chegar à necessidade central: não apenas visualizar dados, mas obter *insights* sobre eficiência, gargalos e performance do fluxo de trabalho.
- **Pesquisa de Mercado:** Investigação de novos recursos do SQL Server 2025 para otimizar a solução.

## 3. Resultados da Análise e Arquitetura Proposta
A arquitetura será implementada em três fases (camadas) dentro do banco de dados, culminando em uma única Stored Procedure que alimentará o painel.

### Fase 1: A Fundação - A Visão Analítica Central
Criaremos uma `VIEW` para servir como a fonte única da verdade. Esta view desnormalizará os dados e realizará o cálculo fundamental: o tempo gasto por um card em cada movimento.

**Objeto:** `[analytics].[vw_CardFullHistory]`
**Lógica:**
1.  Unir as tabelas `dbo.Cards`, `dbo.CardMovements`, `dbo.CardColumns` e `dbo.Users`.
2.  Utilizar a função de janela `LEAD()` sobre a tabela `CardMovements` (ordenada por data) para encontrar a data do próximo movimento.
3.  Calcular a diferença de tempo (`DATEDIFF`) entre um movimento e o próximo. Este será o `TimeSpentInStageInSeconds`.
4.  A view conterá colunas como `CardID`, `Title`, `CurrentColumnID`, `MovementColumnID`, `UserID`, `MovementDate`, `NextMovementDate`, `TimeSpentInStageInSeconds`, `DueDate`, `CreatedAt`.

### Fase 2: As Métricas - Os Indicadores de Performance (KPIs)
Com a view base, podemos construir funções ou usar expressões de tabela comuns (CTEs) dentro da procedure final para calcular os KPIs.

**KPIs Sugeridos:**
- **Métricas de Fluxo:**
  - `Lead Time`: Tempo total do `CreatedAt` até a data do movimento para a coluna final ("Concluído").
  - `Cycle Time`: Tempo total do primeiro movimento para uma coluna de "Em Andamento" até a coluna final.
  - `Throughput`: Contagem de cards movidos para a coluna final em um determinado período.
  - `WIP (Work In Progress)`: Contagem de cards que não estão nas colunas iniciais ("Backlog") nem finais ("Concluído").
- **Métricas de Qualidade e Esforço:**
  - `SLA Compliance`: Percentual de cards concluídos dentro do `DueDate`.
  - `TotalTimeSpent`: Soma de `TimeSpentInStageInSeconds` para todos os movimentos de um card.
- **Métricas de Eficiência do Processo:**
  - `AvgTimePerStage`: Média de `TimeSpentInStageInSeconds` para cada `CardColumnID`. Revela gargalos.
  - `MovementCount`: Contagem de movimentos por card. Pode indicar retrabalho.

### Fase 3: O Painel - A Stored Procedure Final
Criaremos uma única Stored Procedure que orquestrará a consulta aos dados e a geração do resultado consolidado, aproveitando os novos recursos do SQL Server 2025.

**Objeto:** `[reports].[sp_GetKanbanDashboard]`
**Assinatura Proposta:**
```sql
CREATE PROCEDURE [reports].[sp_GetKanbanDashboard]
    @StartDate DATE,
    @EndDate DATE,
    @BoardID INT,
    @UserID INT = NULL -- Opcional
AS
```
**Lógica e Uso de Recursos do SQL Server 2025:**
1.  A procedure receberá um intervalo de datas e IDs de filtro.
2.  **[SQL Server 2025] Optional Parameter Plan Optimization (OPPO):** O novo otimizador de planos garantirá que a consulta tenha performance estável, mesmo com o uso de parâmetros opcionais como `@UserID`.
3.  A procedure consultará a `[analytics].[vw_CardFullHistory]` e usará CTEs para calcular os KPIs definidos na Fase 2, sempre dentro do range de datas fornecido.
4.  **[SQL Server 2025] Suporte Nativo a JSON:** A procedure agregará todos os KPIs calculados em um único documento JSON. Isso cria um contrato de dados claro e eficiente para a aplicação, que receberá um único objeto com todos os dados do painel, como no exemplo abaixo.

**Exemplo de Saída JSON:**
```json
{
  "summary": {
    "leadTimeAvg": 86400,
    "cycleTimeAvg": 43200,
    "throughput": 15,
    "wip": 8,
    "slaCompliance": 0.93
  },
  "timePerStage": [
    { "columnName": "Backlog", "avgSeconds": 0 },
    { "columnName": "Em Andamento", "avgSeconds": 25920 },
    { "columnName": "Revisão", "avgSeconds": 12960 }
  ],
  "throughputHistory": [
    { "date": "2025-11-01", "count": 2 },
    { "date": "2025-11-02", "count": 5 }
  ]
}
```

## 4. Conclusões
Esta arquitetura centraliza a lógica de BI no banco de dados, resultando em:
- **Performance:** Os cálculos são feitos onde os dados residem, de forma otimizada.
- **Consistência:** Todos os clientes (aplicação, outros relatórios) consomem a mesma lógica.
- **Manutenibilidade:** A lógica de negócio está em um só lugar, facilitando futuras alterações.
- **Simplicidade na Aplicação:** O frontend e o backend apenas requisitam e exibem os dados, sem a necessidade de cálculos complexos.

## 5. Próximos Passos
A implementação será dividida nos seguintes scripts SQL, que serão fornecidos sequencialmente:
1.  **Script 1:** Criação dos schemas `[analytics]` e `[reports]`.
2.  **Script 2:** Criação da view `[analytics].[vw_CardFullHistory]`.
3.  **Script 3:** Criação da Stored Procedure `[reports].[sp_GetKanbanDashboard]` com a lógica de cálculo e a saída em JSON.
4.  **Script 4:** Scripts de teste para validar os cálculos dos KPIs.

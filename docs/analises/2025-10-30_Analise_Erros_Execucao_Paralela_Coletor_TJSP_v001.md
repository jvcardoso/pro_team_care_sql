# Análise de Erros na Execução Paralela do Coletor TJSP

**Data:** 2025-10-30 21:30
**Versão:** v001
**Autor:** Gemini

## 1. Objetivo

Analisar e diagnosticar dois erros distintos ocorridos durante a execução dos scripts do Coletor TJSP:
1.  `FileNotFoundError` ao executar `run.py`.
2.  `playwright._impl._errors.Error` (race condition) ao executar `workflow_rio_nieva.py` em modo paralelo.

O objetivo é fornecer a causa raiz e a solução para cada um dos problemas.

## 2. Análise do Erro 1: `run.py`

- **Comando Executado:** `python run.py --input teste.csv --output teste_saida --debug`
- **Sintoma:** O programa encerrou imediatamente com o erro `Erro ao carregar arquivo de entrada: [Errno 2] No such file or directory: 'teste.csv'`.
- **Causa Raiz:** O script foi instruído a ler o arquivo `teste.csv`, mas esse arquivo não existe no diretório em que o comando foi executado (`/home/juliano/Projetos/meu_projeto/coletor-tjsp`).
- **Solução:** Antes de executar o comando, garantir que o arquivo de entrada (`teste.csv`) esteja presente no diretório de execução ou fornecer o caminho absoluto para ele.

## 3. Análise do Erro 2: `workflow_rio_nieva.py` (Paralelo)

Este é o erro crítico que impede o sucesso da nova implementação paralela.

- **Comando Executado:** `python workflow_rio_nieva.py`
- **Sintoma:** A execução inicia com 3 workers, mas falha com o erro `playwright._impl._errors.Error: Unable to retrieve content because the page is navigating and changing the content.`.
- **Causa Raiz (Diagnóstico Técnico):** O erro é um sintoma clássico de **Race Condition**. A implementação atual está fazendo com que os **3 workers paralelos compartilhem UMA ÚNICA instância do navegador e da página** (`scraper.page`).

    Isso cria um cenário caótico e incorreto:
    1.  O Worker 1 navega para a URL do Processo A.
    2.  Imediatamente, o Worker 2 manda a **mesma página** navegar para a URL do Processo B.
    3.  O Worker 3 manda a **mesma página** navegar para a URL do Processo C.
    4.  Quando o Worker 1 tenta clicar no botão "Mais" ou extrair o conteúdo, a página já pode ter sido redirecionada pelo Worker 2 ou 3. O Playwright detecta que a página está em um estado instável ("is navigating") e lança a exceção, pois não é seguro ler seu conteúdo.

### Solução Arquitetural (Correção Obrigatória)

A arquitetura do paralelismo precisa ser alterada para garantir o **isolamento** entre os workers. Cada worker deve ter sua própria instância do navegador/página, completamente independente das outras.

- **Implementação da Correção:**
    1.  O objeto `TJSPScraper` **não deve** ser criado uma única vez no escopo principal do workflow.
    2.  Em vez disso, a inicialização do scraper (`async with TJSPScraper() as scraper:`) deve ser movida para **dentro** da função que cada worker executa (`process_single` ou uma função similar).
    3.  Dessa forma, cada tarefa paralela irá:
        a. Criar sua própria instância do `TJSPScraper` (e sua própria página).
        b. Realizar todo o trabalho de extração de forma isolada.
        c. Fechar sua instância ao final.

O semáforo (`asyncio.Semaphore`) deve ser mantido no escopo externo para continuar controlando quantas dessas instâncias independentes podem ser criadas e executadas ao mesmo tempo.

## 4. Resumo das Ações Recomendadas

1.  **Para `run.py`:** Verificar a existência do arquivo `teste.csv` no diretório de execução.
2.  **Para `workflow_rio_nieva.py`:** Refatorar o código para que **cada worker crie e gerencie sua própria instância do `TJSPScraper`**, garantindo total isolamento e eliminando a condição de corrida (race condition).

Após a aplicação da correção arquitetural no `workflow_rio_nieva.py`, o script funcionará de forma paralela, segura e eficiente, resolvendo o problema do timeout sem introduzir novos erros.

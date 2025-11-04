# Análise do Sistema - Dados Incompletos na Revelação de Endereços (LGPD)

**Data:** 2025-10-26 14:30
**Versão:** v001
**Autor:** Gemini
**Revisão de:** N/A
**Motivo da revisão:** N/A

## Histórico de Versões
- v001 (2025-10-26): Versão inicial da análise sobre dados de endereço incompletos na funcionalidade de "reveal".

## Objetivo
Investigar e identificar a causa raiz do problema onde os campos `Logradouro`, `Bairro` e `CEP` não são exibidos na interface do usuário após a função de "revelar" (LGPD) ser acionada, embora a operação não retorne mais erros de sistema.

## Metodologia
Para esta análise, foram aplicados os seguintes métodos:
- **Systematic Investigation:** Análise do fluxo de dados completo, desde a requisição do frontend, passando pela lógica da API no backend, até a consulta no banco de dados SQL Server.
- **Differential Analysis:** Comparação do comportamento dos campos que são exibidos corretamente (ex: `Cidade/Estado`, `Número`) com os que aparecem vazios (`Logradouro`, `Bairro`, `CEP`).
- **Forensic Analysis:** Inspeção detalhada do código-fonte do backend, especificamente o endpoint `reveal_fields_generic` no arquivo `backend/app/api/v1/lgpd.py`, que é responsável por buscar os dados no banco.
- **5 Whys Method:** Aplicação de perguntas sucessivas para aprofundar a investigação até a causa fundamental.
  1. *Por que o endereço aparece incompleto?* Porque os campos `logradouro`, `bairro` e `cep` estão vazios.
  2. *Por que eles estão vazios?* Porque o backend provavelmente não os incluiu na resposta da API.
  3. *Por que o backend não os incluiu?* Porque as queries SQL executadas para buscar esses campos podem ter retornado um valor nulo ou vazio.
  4. *Por que a query retornaria um valor nulo?* Porque o registro para aquele endereço específico na tabela `core.addresses` pode não ter esses campos preenchidos.
  5. *Por que o registro no banco estaria incompleto?* Potencialmente por uma falha no processo de inserção de dados original ou por se tratar de um dado de teste incompleto.

## Resultados
1.  **Erro Anterior Corrigido:** A análise anterior identificou e levou à correção de um `ValidationError` do Pydantic. A API não apresenta mais erro 500.
2.  **Comportamento Atual:** A API retorna status `200 OK`. O frontend recebe a resposta e tenta renderizar os dados.
3.  **Dados Exibidos vs. Não Exibidos:**
    - **Exibidos:** `Cidade/Estado` e `Número` (mostrado como "S/N").
    - **Não Exibidos:** `Logradouro`, `Bairro`, `CEP`.
4.  **Análise do Código:** O endpoint `reveal_fields_generic` em `lgpd.py` executa uma query SQL individual para cada parte do endereço. A lógica para cada campo é similar:
    ```python
    query = text("SELECT street FROM core.addresses WHERE id = :address_id ...")
    result = await db.execute(query, ...)
    row = result.first()
    if row:
        revealed_data[field_name] = row.street
    ```
    Se `row` for encontrado, mas `row.street` for `NULL` no banco, o valor atribuído será `None`. Se o frontend não tratar `null` adequadamente, o campo pode aparecer vazio. Se `row` não for encontrado, nada é adicionado ao dicionário `revealed_data`.

## Conclusões
A hipótese principal, com alta probabilidade de ser a correta, é que **os dados para `street`, `neighborhood`, e `zip_code` estão nulos ou armazenados como strings vazias na tabela `core.addresses`** para o registro de endereço específico que está sendo consultado.

O fato de `Cidade/Estado` e `Número` serem exibidos (mesmo que "S/N") indica que o mecanismo de "reveal" está funcionando, mas a qualidade dos dados no banco é o problema. A lógica do backend não falha; ela apenas retorna os dados que encontra.

## Próximos passos
1.  **Validação Definitiva:** Executar uma consulta `SELECT` diretamente no banco de dados para inspecionar a linha correspondente na tabela `core.addresses`.
    ```sql
    -- Substituir '?' pelo ID do endereço sendo testado.
    SELECT street, number, neighborhood, zip_code, city, state
    FROM core.addresses
    WHERE id = ?;
    ```
2.  **Ação Corretiva:**
    - **Se os dados estiverem ausentes/nulos:** Corrigir o registro diretamente no banco para validar o fluxo completo. Investigar a origem da inserção de dados incompletos.
    - **Se os dados existirem no banco:** A investigação deverá mudar o foco para a camada da API, analisando como os tipos de dados (ex: `None` do Python) são serializados para JSON e interpretados pelo frontend.

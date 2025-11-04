# Análise do Sistema - Revisão da Lógica de Acesso aos Logs de Auditoria LGPD

**Data:** 2025-10-26 22:00
**Versão:** v001
**Autor:** Gemini
**Revisão de:** N/A
**Motivo da revisão:** Análise inicial.

## Histórico de Versões
- v001 (2025-10-26): Criação do documento para analisar a implementação da lógica de acesso aos logs de auditoria LGPD e propor a migração para o banco de dados.

## Objetivo
Esta análise tem como objetivo diagnosticar a implementação atual da lógica de filtragem de logs de auditoria LGPD, identificar os desvios arquitetônicos em relação ao padrão "Database-First" do projeto e especificar a solução correta, centralizando a regra de negócio no banco de dados SQL Server.

## Metodologia
Para a elaboração deste documento, foram aplicados os seguintes métodos de análise:
- **Systematic Investigation:** Análise do fluxo de dados descrito, desde a requisição no frontend até a consulta no banco.
- **Differential Analysis:** Comparação da abordagem atual (lógica na aplicação) com a abordagem definida pela arquitetura do projeto (lógica no banco de dados).
- **Forensic Analysis:** Exame da estrutura da tabela `lgpd_audit_log` e dos parâmetros de consulta para entender a intenção original.
- **5 Whys Method:** Investigação da causa raiz que levou à implementação da lógica de segurança na camada de aplicação.

## Resultados

### 1. Diagnóstico do Fluxo Atual
O fluxo para visualização de logs de auditoria LGPD, conforme a implementação corrente, é o seguinte:
1.  **Requisição:** O frontend solicita os logs para uma empresa específica (`GET /api/v1/lgpd/companies/{company_id}/audit-log`).
2.  **Autenticação:** O backend valida o token JWT do usuário.
3.  **Lógica de Negócio (Aplicação):** O código Python no backend constrói dinamicamente uma consulta SQL.
    - Ele verifica se o usuário autenticado possui o atributo `is_system_admin`.
    - **Se `is_system_admin` for verdadeiro**, a consulta ao banco `pro_team_care_logs` na tabela `core.lgpd_audit_log` **não inclui** um filtro por `company_id` do usuário, permitindo acesso irrestrito aos logs da empresa solicitada.
    - **Se `is_system_admin` for falso**, a consulta **inclui** um filtro `WHERE company_id = {current_user.company_id}`, restringindo a visão apenas aos logs da própria empresa do usuário.
4.  **Consulta:** A query SQL, já com a lógica de permissão embutida, é executada no banco de dados.

### 2. Análise Crítica e Causa Raiz (5 Whys)

A implementação atual, embora resolva o requisito funcional, representa um grave desvio arquitetônico.

- **Por que a lógica de permissão está na aplicação?**
  - *Resposta:* Para corrigir um bug onde administradores do sistema não conseguiam ver logs de outras empresas.
- **Por que o bug existia?**
  - *Resposta:* Porque a consulta original aplicava um filtro de `company_id` de forma indiscriminada para todos os perfis de usuário.
- **Por que a consulta era indiscriminada?**
  - *Resposta:* Porque o mecanismo de acesso a dados não tinha conhecimento dos diferentes níveis de permissão (usuário de tenant vs. administrador do sistema).
- **Por que o mecanismo de acesso a dados não tinha esse conhecimento?**
  - *Resposta:* Porque a regra de negócio sobre "quem pode ver o quê" não foi modelada ou delegada ao banco de dados.
- **Por que a regra não foi delegada ao banco?**
  - *Resposta (Causa Raiz):* **A arquitetura de acesso a dados não possuía um componente (como uma Stored Procedure ou View parametrizada) capaz de encapsular e aplicar as regras de autorização complexas, forçando o desenvolvedor a implementá-las na camada de aplicação.**

Este desvio viola o princípio de que o banco de dados é a fonte soberana da verdade, introduzindo os seguintes riscos:
- **Inconsistência:** A mesma lógica pode ser reescrita de forma diferente em outros endpoints, criando múltiplas fontes da verdade.
- **Manutenção:** Alterações na política de acesso exigirão modificações no código da aplicação, em vez de uma alteração centralizada no banco.
- **Segurança:** É mais difícil auditar e garantir as políticas de segurança quando elas estão dispersas pelo código da aplicação.

## Conclusões
A implementação atual da lógica de acesso aos logs de auditoria LGPD na camada de aplicação é inadequada e viola os princípios arquitetônicos do projeto Pro Team Care. A correção, embora funcional, introduziu um débito técnico que deve ser sanado.

Toda a lógica de autorização para acesso aos logs deve ser migrada para o banco de dados para garantir centralização, consistência e segurança.

## Próximos passos
Recomenda-se ao DBA a criação de uma Stored Procedure para encapsular toda a lógica de consulta e autorização, que será o único ponto de acesso do backend para estes dados.

### 1. Especificação da Stored Procedure
- **Nome:** `pro_team_care_logs.core.sp_get_lgpd_audit_logs`
- **Parâmetros de Entrada:**
  - `@requesting_user_id INT`: ID do usuário que está fazendo a solicitação (obtido do token JWT).
  - `@target_company_id INT`: ID da empresa cujos logs estão sendo solicitados (o `{company_id}` da URL).
  - `@page_number INT = 1`: Número da página para paginação.
  - `@page_size INT = 100`: Quantidade de registros por página.

- **Lógica Interna:**
  1.  A procedure deve primeiro verificar o perfil do `@requesting_user_id` consultando a tabela `pro_team_care.core.users` (ou uma view de usuários apropriada) para determinar se o usuário é um administrador do sistema (`is_system_admin = 1`).
  2.  **SE** o usuário for um administrador do sistema:
      - A consulta principal deve ser executada na tabela `pro_team_care_logs.core.lgpd_audit_log` filtrando **apenas** por `entity_type = 'companies'` e `entity_id = @target_company_id`.
  3.  **SENÃO** (se for um usuário comum):
      - A consulta deve filtrar por `entity_type = 'companies'`, `entity_id = @target_company_id`, E TAMBÉM `company_id = (SELECT company_id FROM pro_team_care.core.users WHERE id = @requesting_user_id)`.
  4.  A consulta deve sempre ser ordenada por `created_at DESC`.
  5.  A paginação deve ser implementada usando `OFFSET (@page_number - 1) * @page_size ROWS FETCH NEXT @page_size ROWS ONLY`.

### 2. Orientação para a Camada de Aplicação
O endpoint do backend (`/api/v1/lgpd/companies/{company_id}/audit-log`) deverá ser refatorado para, em vez de construir uma query dinâmica, executar uma chamada a esta nova Stored Procedure, passando os parâmetros requeridos.

### 3. Exemplo de Validação para o DBA
O DBA pode validar a lógica da procedure com as seguintes execuções:

```sql
-- Simulação de um admin (ex: user_id = 1) vendo logs da empresa 164
EXEC pro_team_care_logs.core.sp_get_lgpd_audit_logs 
    @requesting_user_id = 1, 
    @target_company_id = 164, 
    @page_number = 1, 
    @page_size = 100;

-- Simulação de um usuário comum da empresa 25 vendo (sem sucesso) logs da empresa 164
-- (Esta chamada não deve retornar resultados se o usuário 25 não for da empresa 164)
EXEC pro_team_care_logs.core.sp_get_lgpd_audit_logs 
    @requesting_user_id = 25, 
    @target_company_id = 164, 
    @page_number = 1, 
    @page_size = 100;
```

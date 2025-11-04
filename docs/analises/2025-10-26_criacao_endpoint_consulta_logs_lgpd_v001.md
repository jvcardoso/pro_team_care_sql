# Análise de Demanda - Criação de Endpoint para Consulta de Logs LGPD

**Data:** 2025-10-26 15:00
**Versão:** v001
**Autor:** Gemini
**Revisão de:** N/A
**Motivo da revisão:** N/A

## Histórico de Versões
- v001 (2025-10-26): Documento inicial para guiar o desenvolvimento do endpoint de consulta de logs de auditoria.

## 1. Objetivo da Demanda

Desenvolver um novo endpoint `GET` no backend (FastAPI) que permita ao frontend consultar, filtrar e paginar os registros de auditoria da tabela `pro_team_care_logs.core.lgpd_audit_log`. Esta API é o recurso que falta para alimentar a aba "LGPD" na tela de detalhes da empresa.

## 2. Requisitos Técnicos e Guia de Implementação

**Arquivo a ser Modificado:** `backend/app/api/v1/lgpd.py`

**Rota a ser Criada:**
- **Verbo HTTP:** `GET`
- **Path:** `/audit-logs/`
- **Router:** Deve ser adicionado ao `router` existente com prefixo `/lgpd`.
- **Nome da Função Sugerido:** `get_audit_logs`

**Parâmetros de Entrada (Filtros e Paginação):**
- A função deve receber seus parâmetros através de injeção de dependência do schema `AuditLogFilters`, que já existe.
- Exemplo de assinatura da função:
  ```python
  from app.schemas.lgpd import AuditLogFilters, AuditLogResponse

  @router.get("/audit-logs/", response_model=AuditLogResponse)
  async def get_audit_logs(
      filters: AuditLogFilters = Depends(),
      db: AsyncSession = Depends(get_db),
      current_user: User = Depends(get_current_active_user)
  ):
      # ... lógica a ser implementada
  ```

**Lógica de Banco de Dados (SQLAlchemy):**
1.  **Consulta Principal (SELECT):**
    - Crie uma consulta base na tabela `pro_team_care_logs.core.lgpd_audit_log`.
    - Adicione cláusulas `.where()` dinamicamente à consulta com base nos filtros fornecidos em `filters`. Verifique se `filters.entity_type`, `filters.entity_id`, `filters.user_id`, etc., foram fornecidos.
    - Ordene os resultados pela data, do mais recente para o mais antigo (`.order_by(col('timestamp').desc())`).
2.  **Consulta de Contagem (COUNT):**
    - Crie uma segunda consulta para contar o número total de registros que correspondem aos mesmos filtros (`SELECT COUNT(*)`). Isso é essencial para a paginação.
3.  **Paginação:**
    - Calcule o `offset` a partir de `filters.page` e `filters.size` (ex: `offset = (filters.page - 1) * filters.size`).
    - Aplique `LIMIT` (`.limit(filters.size)`) e `OFFSET` (`.offset(offset)`) à consulta principal.

**Modelo e Construção da Resposta:**
- A rota deve ser decorada com `@router.get(..., response_model=AuditLogResponse)`. `AuditLogResponse` já está definido em `schemas/lgpd.py`.
- Após executar as consultas, mapeie os resultados da consulta principal para uma lista de objetos `AuditLogEntry`.
- Construa e retorne um objeto `AuditLogResponse`, preenchendo todos os seus campos obrigatórios: `items`, `total`, `page`, `size`, e `pages` (calculado a partir de `total` e `size`).

## 3. Critérios de Aceite (Resultados Esperados)

- Uma requisição `GET` para `/api/v1/lgpd/audit-logs/?entity_type=company&entity_id=164&page=1&size=10` deve retornar um JSON com o status `200 OK`.
- O corpo da resposta deve corresponder à estrutura do schema `AuditLogResponse`, contendo a lista de logs no campo `items` e os dados de paginação corretos.
- A API deve ser capaz de filtrar os resultados corretamente quando outros parâmetros (como `user_id` ou `action_type`) forem fornecidos.
- Se nenhum log for encontrado, a API deve retornar uma resposta `200 OK` com o campo `items` sendo uma lista vazia e `total` igual a 0.

## 4. Próximos Passos

1.  **Desenvolvimento:** Implementar a nova rota e sua lógica conforme especificado acima.
2.  **Testes:** Criar testes unitários e/ou de integração para o novo endpoint. Os testes devem validar a filtragem, a paginação e a estrutura da resposta.
3.  **Comunicação:** Após o merge, notificar a equipe de frontend sobre a disponibilidade e a especificação final da nova API para que possam integrá-la na interface.

# Criar Endpoint REST

## Contexto
Você está criando um novo endpoint REST para o Pro Team Care (SaaS multi-tenant).

## Requisitos
- **SEMPRE** use BaseRepository para operações CRUD
- **SEMPRE** adicione dependência `get_current_active_user`
- **SEMPRE** adicione paginação (skip/limit) para endpoints GET
- **SEMPRE** use HTTPException para tratamento de erros
- **SEMPRE** filtre por company_id (multi-tenant)
- **NUNCA** use SELECT * em queries
- **NUNCA** faça hard delete

## Estrutura do Endpoint
```python
@router.get("/", response_model=List[ResponseSchema])
async def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Lista itens com paginação"""
    repo = BaseRepository(ItemModel, db)
    return await repo.get_all(skip=skip, limit=limit)
```

## Testes Necessários
- Teste de sucesso (200)
- Teste de erro (404, 422, 500)
- Teste de autenticação
- Teste de paginação

## Documentação
- Docstring em português explicando o que faz
- Parâmetros e retornos documentados
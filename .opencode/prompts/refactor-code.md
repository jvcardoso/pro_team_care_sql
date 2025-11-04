# Refatorar Código

## Contexto
Você está refatorando código duplicado no Pro Team Care.

## Processo
1. **Identificar duplicação**: Encontre código similar em múltiplos lugares
2. **Criar abstração**: Função, componente ou hook reutilizável
3. **Substituir ocorrências**: Use a nova abstração em todos os lugares
4. **Limpar**: Remover código comentado e imports não utilizados
5. **Testar**: Garantir que nada quebrou

## Regras de Refatoração
- **SEMPRE** mantenha funcionalidade existente
- **SEMPRE** execute testes após mudanças
- **SEMPRE** remova código comentado
- **SEMPRE** limpe imports não utilizados
- **SEMPRE** execute linter/formatador
- **NUNCA** mude comportamento sem confirmar

## Benefícios Esperados
- Redução de linhas de código
- Manutenibilidade melhorada
- Consistência garantida
- Menos bugs por duplicação

## Validação
- Todos os testes passam ✅
- Linter sem erros ✅
- Código formatado ✅
- Documentação atualizada ✅
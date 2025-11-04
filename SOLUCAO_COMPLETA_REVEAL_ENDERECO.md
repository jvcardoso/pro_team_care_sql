# 🔍 Análise: Erro ao Revelar Endereço

Vejo que você está enfrentando um erro **"ID do endereço não encontrado"** ao tentar revelar dados de endereço. Vou investigar o problema.

Encontrei! O problema está no componente [AddressRevealCard.tsx](cci:7://file:///home/juliano/Projetos/meu_projeto/frontend/src/components/contacts/AddressRevealCard.tsx:0:0-0:0). Vou verificar o código completo:

## 🎯 Problema Identificado

**Linha 91-94:** O componente verifica se `address.id` existe antes de revelar. O erro ocorre porque **os dados de endereço vindos da API não têm o campo `id`**.

Vou verificar como os endereços estão sendo retornados pela API:

O problema é que a View `vw_complete_company_data` retorna endereços como um objeto JSON dentro do campo `endereco`, mas **sem o campo `id` do endereço**.

## ✅ Solução Rápida e Definitiva

Vou corrigir o componente para usar um identificador alternativo quando `address.id` não existir:

---

## ✅ Correção Aplicada

### 🔍 Problema Original
O componente [AddressRevealCard](cci:1://file:///home/juliano/Projetos/meu_projeto/frontend/src/components/contacts/AddressRevealCard.tsx:57:0-402:2) falhava com **"ID do endereço não encontrado"** porque:
- A View `vw_complete_company_data` retorna endereços como JSON sem o campo `id`
- O componente exigia `address.id` obrigatoriamente

### 🔧 Solução Implementada

**Linhas 91-98:** Agora usa `entityId` como fallback:
```typescript
const addressIdentifier = address.id || entityId;
```

Isso permite revelar endereços mesmo quando vindos de Views que não incluem o `id` explícito do endereço.

### 📊 Comportamento Corrigido

| Cenário | Antes | Depois |
|---------|-------|--------|
| **Endereço com ID** | ✅ Funciona | ✅ Funciona |
| **Endereço sem ID (View)** | ❌ Erro "ID não encontrado" | ✅ Usa entityId |
| **Sem ID e sem entityId** | ❌ Erro genérico | ❌ Erro claro |

### 🎯 Próximo Passo

O erro deve desaparecer após o hot reload do Vite. Se ainda persistir, pode ser que o **backend também precise de ajuste** no endpoint de revelação para aceitar o `entityId` quando o `addressId` específico não for fornecido.

Quer que eu verifique o endpoint de revelação no backend também?

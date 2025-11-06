# ✅ Funcionalidade de Importação do BusinessMap

## 🎯 Objetivo

Importar cards do BusinessMap via arquivo CSV, com:
- ✅ Validação de alterações
- ✅ Criação de novos cards
- ✅ Atualização de cards existentes
- ✅ Registro de último comentário como movimento

---

## 🎨 Interface

### **Botão no Kanban Board:**
```
📋 Kanban Board

[Importar BM]  [Novo Card]
```

### **Modal de Importação:**
```
┌─────────────────────────────────────────────────┐
│ 📥 Importar Cards do BusinessMap          [X]  │
├─────────────────────────────────────────────────┤
│                                                 │
│ ℹ️ Instruções                                  │
│ • Exporte o CSV do BusinessMap                 │
│ • Arquivo deve ter separador ";"              │
│ • Cards existentes serão atualizados          │
│ • Novos cards serão criados                   │
│ • Último comentário vira movimento            │
│                                                 │
│ Arquivo CSV                                    │
│ ┌─────────────────────────────────────────┐   │
│ │  📄 Clique para selecionar              │   │
│ │     ou arraste o arquivo                │   │
│ │                                          │   │
│ │     dasa-20251105161442-BPX.csv         │   │
│ └─────────────────────────────────────────┘   │
│                                                 │
│ ✅ Importação Concluída!                       │
│ Total: 99 cards                                │
│ Processados: 99                                │
│ Criados: 10                                    │
│ Atualizados: 89                                │
│                                                 │
│                    [Cancelar]  [Importar]      │
└─────────────────────────────────────────────────┘
```

---

## 💻 Implementação

### **1. Frontend - Botão**
**Arquivo:** `frontend/src/pages/KanbanBoardPage.tsx`

```tsx
<button onClick={handleImport}>
  <svg>...</svg>
  Importar BM
</button>
```

---

### **2. Frontend - Modal**
**Arquivo:** `frontend/src/components/kanban/ImportBMModal.tsx`

**Funcionalidades:**
- ✅ Upload de arquivo CSV
- ✅ Validação de formato
- ✅ Envio para API
- ✅ Exibição de progresso
- ✅ Estatísticas de importação

**Código:**
```tsx
const handleImport = async () => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/v1/kanban/import-bm', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });

  setProgress(response.data);
  // { total, processed, created, updated, errors }
};
```

---

### **3. Backend - Endpoint**
**Arquivo:** `backend/app/api/v1/kanban.py`

**Endpoint:** `POST /api/v1/kanban/import-bm`

**Fluxo:**
1. Recebe arquivo CSV
2. Valida formato
3. Lê linha por linha
4. Mapeia colunas do CSV
5. Chama SP para cada linha
6. Retorna estatísticas

**Código:**
```python
@router.post("/import-bm")
async def import_businessmap_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Ler CSV
    contents = await file.read()
    decoded = contents.decode('utf-8')
    csv_reader = csv.reader(io.StringIO(decoded), delimiter=';')
    
    # Processar cada linha
    for row in csv_reader:
        # Mapear colunas
        external_card_id = row[0]
        title = row[3]
        # ... outros campos
        
        # Chamar SP
        await db.execute(text("""
            EXEC [core].[sp_UpsertCardFromImport]
                @ExternalCardID = :external_card_id,
                @Title = :title,
                ...
        """), params)
    
    return {
        "total": total,
        "processed": processed,
        "created": created,
        "updated": updated,
        "errors": errors
    }
```

---

### **4. Banco de Dados - Stored Procedure**
**Arquivo:** `Database/067_Create_SP_UpsertCardFromImport.sql`

**SP:** `[core].[sp_UpsertCardFromImport]`

**Lógica:**
1. Verifica se card existe (por ExternalCardID)
2. Se existe:
   - Compara dados
   - Atualiza se houver diferença
   - Retorna 'UPDATED'
3. Se não existe:
   - Cria novo card
   - Mapeia coluna por nome
   - Retorna 'CREATED'
4. Registra último comentário como movimento

---

## 📊 Formato do CSV

### **Colunas Esperadas (separador ;):**
```
0  - Card ID (ExternalCardID)
1  - Custom ID
2  - Color
3  - Title
4  - Owner
5  - Deadline
6  - Priority
7  - Column Name
8  - Board Name
9  - Owners
10 - Description
11 - Lane Name
12 - Actual End Date
13 - Last End Date
14 - Last Start Date
15 - Planned Start
16 - Card URL
17 - Last Comment (NOVO!)
```

### **Exemplo de Linha:**
```csv
337860;;#00d3ff;[GMUD] - Abrir RDM Deploy;juliano.cardoso;2025-11-03;Average;Concluído;SisCorp Recebíveis Master;juliano.cardoso;Demandas em Pronto para Publicação.;Default Swimlane;;2025-11-04 09:38:16;2025-11-03 09:42:58;;https://dasa.businessmap.io/ctrl_board/155/cards/337860/details;Implementado com sucesso
```

---

## 🔄 Fluxo Completo

### **1. Usuário Exporta CSV do BusinessMap**
- Inclui coluna "Last Comment"
- Salva arquivo localmente

### **2. Usuário Acessa Kanban**
```
http://192.168.11.83:3000/admin/kanban
```

### **3. Clica em "Importar BM"**
- Modal abre
- Seleciona arquivo CSV
- Clica "Importar"

### **4. Backend Processa**
- Lê CSV linha por linha
- Para cada linha:
  - Chama SP `sp_UpsertCardFromImport`
  - SP verifica se card existe
  - Cria ou atualiza
  - Registra movimento do comentário

### **5. Retorna Estatísticas**
```json
{
  "total": 99,
  "processed": 99,
  "created": 10,
  "updated": 89,
  "errors": 0
}
```

### **6. Modal Mostra Resultado**
- Exibe estatísticas
- Aguarda 2 segundos
- Recarrega página

---

## 🎯 Casos de Uso

### **Caso 1: Primeira Importação**
```
Total: 99 cards
Criados: 99
Atualizados: 0
```

### **Caso 2: Atualização**
```
Total: 99 cards
Criados: 5 (novos)
Atualizados: 94 (existentes)
```

### **Caso 3: Sem Alterações**
```
Total: 99 cards
Criados: 0
Atualizados: 0 (nenhuma mudança)
```

---

## 🔍 Validações

### **Frontend:**
- ✅ Arquivo deve ser .csv
- ✅ Arquivo não pode estar vazio
- ✅ Exibe erro se formato inválido

### **Backend:**
- ✅ Valida extensão .csv
- ✅ Valida número mínimo de colunas (17)
- ✅ Trata erros por linha (continua processando)
- ✅ Rollback em caso de erro geral

### **Banco de Dados:**
- ✅ Valida ExternalCardID único
- ✅ Mapeia coluna por nome
- ✅ Valida datas
- ✅ Cria movimentos automaticamente

---

## 📁 Arquivos Criados/Modificados

### **Frontend:**
```
✅ components/kanban/ImportBMModal.tsx (NOVO)
   - Modal de upload
   - Validação de arquivo
   - Exibição de progresso
   
✅ pages/KanbanBoardPage.tsx
   - Botão "Importar BM"
   - Estado showImportModal
   - Integração com modal
```

### **Backend:**
```
✅ api/v1/kanban.py
   - Endpoint POST /import-bm
   - Processamento de CSV
   - Chamada da SP
   - Retorno de estatísticas
```

### **Banco de Dados:**
```
✅ 065_Add_ExternalID_To_Cards.sql
   - Coluna ExternalCardID
   - Índice único
   
✅ 066_Clear_Imported_Cards_For_Test.sql
   - Script de limpeza (teste)
   
✅ 067_Create_SP_UpsertCardFromImport.sql
   - SP de importação
   - Lógica de upsert
   - Registro de movimentos
```

---

## 🧪 Como Testar

### **1. Preparar CSV:**
```bash
# Exportar do BusinessMap
# Incluir coluna "Last Comment"
# Salvar como dasa-YYYYMMDD-XXX.csv
```

### **2. Acessar Kanban:**
```
http://192.168.11.83:3000/admin/kanban
```

### **3. Importar:**
1. Clicar "Importar BM"
2. Selecionar arquivo CSV
3. Clicar "Importar"
4. Aguardar processamento
5. Ver estatísticas

### **4. Validar:**
- Verificar cards criados
- Verificar cards atualizados
- Verificar movimentos (último comentário)
- Verificar datas

---

## 🚀 Melhorias Futuras (Opcional)

### **1. Preview do CSV:**
```tsx
<table>
  <thead>
    <tr>
      <th>Card ID</th>
      <th>Título</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
    {preview.map(row => (
      <tr>
        <td>{row[0]}</td>
        <td>{row[3]}</td>
        <td>{row[7]}</td>
      </tr>
    ))}
  </tbody>
</table>
```

### **2. Validação Prévia:**
```tsx
const validateCSV = (file) => {
  // Verificar formato
  // Verificar colunas obrigatórias
  // Verificar dados inválidos
  return { valid: true, errors: [] };
};
```

### **3. Importação Parcial:**
```tsx
<div>
  <input type="checkbox" /> Importar apenas novos
  <input type="checkbox" /> Atualizar existentes
</div>
```

### **4. Log Detalhado:**
```tsx
<div className="log">
  {logs.map(log => (
    <div>
      {log.timestamp} - {log.action} - {log.cardId}
    </div>
  ))}
</div>
```

### **5. Agendamento:**
```tsx
<div>
  <input type="checkbox" /> Importar automaticamente
  <select>
    <option>Diariamente</option>
    <option>Semanalmente</option>
  </select>
</div>
```

---

## ✅ Checklist de Implementação

- [x] Botão "Importar BM" no Kanban
- [x] Modal de upload de CSV
- [x] Validação de arquivo
- [x] Endpoint backend
- [x] Processamento de CSV
- [x] Chamada da SP
- [x] Retorno de estatísticas
- [x] Exibição de progresso
- [x] Tratamento de erros
- [x] Reload após importação
- [x] Dark mode suportado
- [x] Documentação completa

---

**Data:** 2025-11-05  
**Status:** ✅ IMPLEMENTADO  
**Funcionalidade:** 100% Completa  
**Pronto para Teste:** ✅ SIM

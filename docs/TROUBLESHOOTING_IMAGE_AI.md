# 🔍 Troubleshooting: Upload e Processamento de Imagens com IA

## 🎯 Sintoma Atual

**Problema:** Upload funciona (201), mas movimento não é criado.

**Console mostra:**
```
✅ API Response: POST /api/v1/kanban/cards/2/images {status: 201}
```

**Mas NÃO mostra:**
```
🚀 API Request: POST /api/v1/kanban/cards/2/process-image
```

---

## 🔍 Diagnóstico

### **Possíveis Causas:**

#### **1. Usuário não está clicando no botão "Processar com IA"**
- Upload funciona (Passo 1 ✅)
- Mas Passo 2 não é executado
- Botão pode não estar aparecendo

#### **2. Estado `uploadedImageId` não está sendo atualizado**
- Upload retorna `image_id`
- Mas `setUploadedImageId()` pode não estar funcionando
- React não re-renderiza o botão do Passo 2

#### **3. Botão está desabilitado**
- Falta descrição no textarea
- `userDescription.trim()` está vazio

---

## 🧪 Como Testar

### **Teste 1: Verificar se botão aparece**

Após fazer upload, verificar no console:

```javascript
// Deve aparecer:
📸 Upload concluído! Image ID: 123
✅ Estados atualizados - uploadedImageId: 123
```

**Se NÃO aparecer:** Problema no upload ou na resposta da API.

**Se aparecer:** Verificar se botão "Processar com IA" está visível na tela.

---

### **Teste 2: Verificar estado do React**

Abrir React DevTools e procurar componente `ImageUploadWithAI`:

```
uploadedImageId: 123        ✅ OK
uploadedImageUrl: "data..." ✅ OK
userDescription: ""         ❌ VAZIO (botão desabilitado)
```

**Solução:** Adicionar texto no textarea de descrição.

---

### **Teste 3: Forçar processamento**

Adicionar botão de debug temporário:

```tsx
{uploadedImageId && (
  <button onClick={() => {
    console.log('DEBUG uploadedImageId:', uploadedImageId);
    console.log('DEBUG userDescription:', userDescription);
  }}>
    🐛 Debug Estado
  </button>
)}
```

---

## ✅ Checklist de Verificação

### **Frontend:**

- [ ] Upload retorna `image_id` na resposta?
- [ ] `setUploadedImageId()` é chamado?
- [ ] Estado `uploadedImageId` é atualizado?
- [ ] Preview permanece visível após upload?
- [ ] Badge "✅ Imagem enviada" aparece?
- [ ] Botão "Processar com IA" aparece?
- [ ] Textarea de descrição está visível?
- [ ] Botão está habilitado (descrição preenchida)?

### **Backend:**

- [ ] Endpoint `/cards/{id}/images` retorna 201?
- [ ] Response contém `image_id`?
- [ ] Imagem foi salva no disco?
- [ ] Registro `CardImage` foi criado no banco?

---

## 🔧 Correções Aplicadas

### **1. Logs de Debug Adicionados**

```typescript
// No handleUpload:
const imageId = uploadResponse.data.image_id;
console.log('📸 Upload concluído! Image ID:', imageId);
console.log('✅ Estados atualizados - uploadedImageId:', imageId);

// No handleProcessWithAI:
console.log('🤖 Iniciando processamento com IA...');
console.log('📊 uploadedImageId:', uploadedImageId);
console.log('📝 userDescription:', userDescription);
```

### **2. Badge Visual de Sucesso**

```tsx
{uploadedImageId && (
  <div className="bg-green-50 border border-green-200 rounded-lg p-3">
    <p>✅ Imagem enviada com sucesso!</p>
    <p>ID: {uploadedImageId}</p>
  </div>
)}
```

### **3. Indicador na Imagem**

```tsx
{uploadedImageId && (
  <div className="absolute top-2 left-2 bg-green-500 text-white rounded-full">
    ✓ Enviada
  </div>
)}
```

---

## 📊 Fluxo Esperado com Logs

### **Passo 1: Upload**

```
1. Usuário seleciona imagem
2. Preview aparece
3. Clica "Enviar Imagem"
   
Console:
🚀 API Request: POST /api/v1/kanban/cards/2/images
✅ API Response: POST /api/v1/kanban/cards/2/images {status: 201, data: {image_id: 123}}
📸 Upload concluído! Image ID: 123
✅ Estados atualizados - uploadedImageId: 123

UI:
✅ Badge verde "Imagem enviada" aparece
✅ Badge "✓ Enviada" aparece na imagem
✅ Botão "Processar com IA" aparece (Passo 2)
```

### **Passo 2: Processar com IA**

```
4. Usuário adiciona descrição no textarea
5. Clica "Processar com IA"

Console:
🤖 Iniciando processamento com IA...
📊 uploadedImageId: 123
📝 userDescription: "Screenshot do dashboard"
📤 Enviando para: /api/v1/kanban/cards/2/process-image
📦 Payload: {image_id: 123, user_description: "..."}
🚀 API Request: POST /api/v1/kanban/cards/2/process-image
✅ API Response: POST /api/v1/kanban/cards/2/process-image {status: 201}
✅ Resposta da IA: {movement_id: 456, ai_analysis: "..."}

UI:
✅ Toast "Imagem processada com IA"
✅ Modal recarrega detalhes do card
✅ Movimento aparece na lista
```

---

## 🐛 Problemas Conhecidos

### **1. Estado não atualiza imediatamente**

**Sintoma:** `uploadedImageId` é `null` mesmo após `setUploadedImageId()`.

**Causa:** React batching de estados.

**Solução:** Usar callback ou useEffect:

```typescript
useEffect(() => {
  if (uploadedImageId) {
    console.log('✅ uploadedImageId atualizado:', uploadedImageId);
  }
}, [uploadedImageId]);
```

### **2. Botão não aparece**

**Sintoma:** Passo 2 não é renderizado.

**Causa:** Condição `{uploadedImageId && (...)}` falha.

**Debug:**
```typescript
console.log('uploadedImageId:', uploadedImageId);
console.log('Tipo:', typeof uploadedImageId);
console.log('Truthy?', !!uploadedImageId);
```

### **3. Botão desabilitado**

**Sintoma:** Botão existe mas está cinza.

**Causa:** `!userDescription.trim()` é `true`.

**Solução:** Adicionar texto no textarea.

---

## 📞 Próximos Passos

1. **Testar com logs:** Reiniciar aplicação e verificar console
2. **Verificar UI:** Badge verde deve aparecer após upload
3. **Adicionar descrição:** Preencher textarea
4. **Clicar processar:** Botão deve estar verde e habilitado
5. **Verificar console:** Deve mostrar requisição para `/process-image`

---

## 🎯 Resultado Esperado

**Console completo:**
```
📸 Upload concluído! Image ID: 123
✅ Estados atualizados - uploadedImageId: 123
🤖 Iniciando processamento com IA...
📊 uploadedImageId: 123
📝 userDescription: "Screenshot do dashboard"
📤 Enviando para: /api/v1/kanban/cards/2/process-image
📦 Payload: {image_id: 123, user_description: "Screenshot do dashboard"}
✅ Resposta da IA: {movement_id: 456, ai_analysis: "..."}
```

**UI:**
- ✅ Badge verde "Imagem enviada"
- ✅ Textarea preenchido
- ✅ Botão "Processar com IA" verde e habilitado
- ✅ Toast de sucesso após processar
- ✅ Movimento aparece na lista

---

**Data:** 2025-11-04
**Versão:** 2.0 (com logs de debug)

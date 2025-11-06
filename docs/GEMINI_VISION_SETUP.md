# 🤖 Configuração do Gemini Vision para Descrição Automática de Imagens

## 📋 Visão Geral

Este documento explica como configurar o Google Gemini Vision API para gerar descrições automáticas de imagens no sistema de Kanban.

---

## 🎯 Funcionalidades

- ✅ **Descrição automática**: IA analisa imagem e gera descrição em português
- ✅ **Upload ou paste**: Suporta upload de arquivo ou colar do clipboard
- ✅ **Editável**: Usuário pode editar descrição gerada
- ✅ **Contexto**: IA considera contexto do card (desenvolvimento, bug, etc)
- ✅ **Gratuito**: Tier free do Gemini é generoso

---

## 🔑 Passo 1: Obter API Key do Google Gemini

### **1.1. Acessar Google AI Studio**
1. Acesse: https://aistudio.google.com
2. Faça login com sua conta Google
3. Aceite os termos de uso

### **1.2. Criar API Key**
1. No menu lateral, clique em **"Get API key"**
2. Clique em **"Create API key"**
3. Escolha um projeto existente ou crie novo
4. Copie a API key gerada

**⚠️ IMPORTANTE:** Guarde a API key em local seguro!

---

## ⚙️ Passo 2: Configurar no Backend

### **2.1. Adicionar variável de ambiente**

Edite o arquivo `.env` no backend:

```bash
# Google Gemini Vision API
GOOGLE_GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### **2.2. Instalar dependência**

```bash
cd backend
pip install google-generativeai
```

### **2.3. Registrar rota na API**

Edite `backend/app/api/v1/api.py`:

```python
from app.api.v1.endpoints import image_analysis

# Adicionar rota
api_router.include_router(
    image_analysis.router,
    prefix="/image-analysis",
    tags=["image-analysis"]
)
```

---

## 🎨 Passo 3: Usar no Frontend

### **3.1. Substituir componente de upload**

No modal do card, substitua `ImageUpload` por `ImageUploadWithAI`:

```tsx
import { ImageUploadWithAI } from './ImageUploadWithAI';

// No componente
<ImageUploadWithAI
  cardId={card.CardID}
  context={`Card de ${card.Priority} sobre ${card.Title}`}
  onImageUploaded={(url, description) => {
    // Salvar imagem com descrição
    console.log('Imagem:', url);
    console.log('Descrição:', description);
  }}
/>
```

---

## 💰 Custos e Limites

### **Tier FREE (Recomendado para começar)**

```
✅ 15 requisições/minuto
✅ 1500 requisições/dia
✅ 1M requisições/mês
✅ GRÁTIS!
```

**Exemplo de uso:**
- 100 imagens/dia = 3000 imagens/mês
- **Custo: $0** (dentro do free tier)

### **Tier PAID (Se precisar escalar)**

```
Input: $0.075 / 1M tokens
Output: $0.30 / 1M tokens
Imagem média: ~258 tokens
```

**Exemplo de uso:**
- 1000 imagens/dia = 30,000 imagens/mês
- 30,000 × 258 tokens = 7,740,000 tokens
- **Custo: ~$0.58/mês** (quase nada!)

---

## 🧪 Testar Configuração

### **1. Verificar status da API**

```bash
curl -X GET "http://localhost:8000/api/v1/image-analysis/status" \
  -H "Authorization: Bearer SEU_TOKEN"
```

**Resposta esperada:**
```json
{
  "enabled": true,
  "model": "gemini-2.5-flash",
  "message": "Serviço ativo"
}
```

### **2. Testar análise de imagem**

```bash
curl -X POST "http://localhost:8000/api/v1/image-analysis/analyze-upload" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -F "file=@/caminho/para/imagem.jpg" \
  -F "context=Card de desenvolvimento"
```

**Resposta esperada:**
```json
{
  "description": "Captura de tela mostrando código Python com uma função de autenticação. Visível um editor de código com syntax highlighting.",
  "success": true,
  "message": "Descrição gerada com sucesso"
}
```

---

## 🎯 Fluxo de Uso

```
1. Usuário faz upload de imagem no card
   ↓
2. Frontend envia para /api/v1/image-analysis/analyze-upload
   ↓
3. Backend salva imagem temporariamente
   ↓
4. Backend envia para Gemini Vision API
   ↓
5. Gemini retorna descrição em português
   ↓
6. Frontend exibe descrição (editável)
   ↓
7. Usuário confirma ou edita descrição
   ↓
8. Imagem + descrição são salvos no banco
```

---

## 🔒 Segurança

### **Boas Práticas:**

1. ✅ **Nunca commitar** API key no git
2. ✅ **Usar variáveis de ambiente** (.env)
3. ✅ **Validar autenticação** antes de chamar IA
4. ✅ **Limitar tamanho** de imagens (máx 10MB)
5. ✅ **Rate limiting** para evitar abuso

### **Exemplo de .env.example:**

```bash
# Google Gemini Vision API
# Obtenha em: https://aistudio.google.com
GOOGLE_GEMINI_API_KEY=your_api_key_here
```

---

## 🐛 Troubleshooting

### **Erro: "GOOGLE_GEMINI_API_KEY não configurada"**

**Solução:**
1. Verifique se `.env` tem a variável
2. Reinicie o servidor backend
3. Verifique se o arquivo `.env` está no diretório correto

### **Erro: "API key inválida"**

**Solução:**
1. Verifique se copiou a key completa
2. Gere nova key no Google AI Studio
3. Verifique se não há espaços extras

### **Erro: "Quota exceeded"**

**Solução:**
1. Você atingiu o limite do free tier
2. Aguarde reset (diário/mensal)
3. Ou faça upgrade para tier pago

### **Descrição não gerada**

**Solução:**
1. Verifique logs do backend
2. Teste endpoint `/status`
3. Verifique conectividade com Google API

---

## 📊 Monitoramento

### **Logs importantes:**

```python
# Backend logs
✅ Gemini Vision configurado com sucesso
📸 Analisando imagem: /tmp/xyz.jpg
✅ Descrição gerada: Captura de tela...
❌ Erro ao gerar descrição: [erro]
```

### **Métricas a acompanhar:**

- Número de imagens analisadas/dia
- Taxa de sucesso das análises
- Tempo médio de resposta
- Uso de tokens (se no tier pago)

---

## 🚀 Status da Implementação

### ✅ **COMPLETAMENTE IMPLEMENTADO E FUNCIONANDO**

1. ✅ **API Key configurada** - Usando `GOOGLE_GEMINI_API_KEY` do .env
2. ✅ **Backend implementado** - Endpoints `/api/v1/image-analysis/*` ativos
3. ✅ **Frontend integrado** - Componente `ImageUploadWithAI` no modal do card
4. ✅ **Testado e funcionando** - Workflow completo validado
5. ✅ **Documentação completa** - Guias de setup e uso disponíveis

### 🎯 **Como Usar:**

1. Abra um card no Kanban Board
2. Na seção "Imagens do Card", clique em "Clique para fazer upload ou cole uma imagem"
3. Selecione uma imagem ou cole do clipboard (Ctrl+V)
4. A IA gera descrição automaticamente em português
5. Edite se necessário e clique "Adicionar Imagem"

---

## 📚 Referências

- [Google Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- [Gemini Pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Google AI Studio](https://aistudio.google.com)

---

## ✅ Checklist de Configuração

- [x] API key obtida no Google AI Studio
- [x] Variável `GOOGLE_GEMINI_API_KEY` configurada no `.env`
- [x] Dependência `google-generativeai` instalada
- [x] Rota `/image-analysis` registrada na API
- [x] Endpoint `/status` retornando `enabled: true`
- [x] Teste de análise funcionando
- [x] Componente `ImageUploadWithAI` integrado no modal do card
- [x] Workflow completo testado e validado
- [x] Documentação atualizada e completa

---

**Configuração completa! 🎉**
